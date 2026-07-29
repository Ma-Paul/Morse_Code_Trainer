from __future__ import annotations

import time
from typing import Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

try:
    from gpiozero import Button
except ImportError:
    # Normal on macOS and Windows.
    Button = None


MORSE_TO_LETTER = {
    "._": "a",
    "_...": "b",
    "_._.": "c",
    "_..": "d",
    ".": "e",
    ".._.": "f",
    "__.": "g",
    "....": "h",
    "..": "i",
    ".___": "j",
    "_._": "k",
    "._..": "l",
    "__": "m",
    "_.": "n",
    "___": "o",
    ".__.": "p",
    "__._": "q",
    "._.": "r",
    "...": "s",
    "_": "t",
    ".._": "u",
    "..._": "v",
    ".__": "w",
    "_.._": "x",
    "_.__": "y",
    "__..": "z",
}

LETTER_TO_MORSE = {letter: code for code, letter in MORSE_TO_LETTER.items()}


class LetterTrainer(QObject):
    """
    Morse letter trainer.

    Both GPIO hardware and keyboard simulation use the same input pipeline.
    """

    letterChanged = Signal()
    morseChanged = Signal()
    inputChanged = Signal()
    runningChanged = Signal()
    mistakeDetailsChanged = Signal()

    correct = Signal(
        float,
        arguments=["elapsedSeconds"],
    )

    # Entered code, expected code, explanation
    mistake = Signal()

    def __init__(
        self,
        single_pin: int = 17,
        left_pin: int = 17,
        right_pin: int = 27,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._letter = "l"
        self._input = ""
        self._running = False
        self._started_at = 0.0
        self._last_mistake_entered = ""
        self._last_mistake_expected = ""
        self._last_mistake_explanation = ""

        self._input_type = "1"
        self._left_type = "Zeitgesteuert"
        self._right_type = "Zeitgesteuert"

        # Time at which each simulated or physical button was pressed.
        self._pressed_at: dict[str, float] = {}

        self._single_button = None
        self._left_button = None
        self._right_button = None

        self._single_pin = single_pin
        self._left_pin = left_pin
        self._right_pin = right_pin

        self._setup_gpio()

    # ------------------------------------------------------------------
    # QML properties
    # ------------------------------------------------------------------

    @Property(str, notify=letterChanged)
    def letter(self) -> str:
        return self._letter

    @Property(str, notify=morseChanged)
    def morse(self) -> str:
        return LETTER_TO_MORSE.get(
            self._letter.lower(),
            "",
        )

    @Property(str, notify=inputChanged)
    def currentInput(self) -> str:
        return self._input

    @Property(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._running

    @Property(str, notify=mistakeDetailsChanged)
    def lastMistakeEntered(self) -> str:
        return self._last_mistake_entered

    @Property(str, notify=mistakeDetailsChanged)
    def lastMistakeExpected(self) -> str:
        return self._last_mistake_expected

    @Property(str, notify=mistakeDetailsChanged)
    def lastMistakeExplanation(self) -> str:
        return self._last_mistake_explanation

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @Slot(str, str, str)
    def configureInput(
        self,
        input_type: str,
        left_type: str,
        right_type: str,
    ) -> None:
        """
        Configure the currently selected input device.

        input_type:
            "1" = one button
            "2" = two buttons

        button functions:
            "Kurz"
            "Lang"
            "Zeitgesteuert"
            "Pause"
        """

        self._input_type = str(input_type or "1")
        self._left_type = left_type or "Zeitgesteuert"
        self._right_type = right_type or "Zeitgesteuert"

        print(
            "Input configured:",
            f"type={self._input_type},",
            f"left={self._left_type},",
            f"right={self._right_type}",
        )

    # ------------------------------------------------------------------
    # Training control
    # ------------------------------------------------------------------

    @Slot(str)
    def startLetter(self, letter: str) -> None:
        normalized = letter[:1].lower()

        if normalized not in LETTER_TO_MORSE:
            print(f"Unknown training letter: {letter!r}")
            return

        self._letter = normalized
        self._input = ""
        self._running = True
        self._started_at = time.monotonic()
        self._pressed_at.clear()

        self.letterChanged.emit()
        self.morseChanged.emit()
        self.inputChanged.emit()
        self.runningChanged.emit()

        print(f"New letter: {self._letter.upper()} " f"({self.morse})")

    @Slot()
    def stop(self) -> None:
        self._pressed_at.clear()

        if self._running:
            self._running = False
            self.runningChanged.emit()

    @Slot(str)
    def submitSymbol(self, symbol: str) -> None:
        """
        Direct symbol input, useful for testing.
        """

        normalized = self._normalize_symbol(symbol)

        if normalized is not None:
            self._append_symbol(normalized)

    @Slot()
    def finishLetter(self) -> None:
        if not self._running:
            return

        if self._input == self.morse:
            self._emit_correct()
        else:
            self._emit_mistake("Die Eingabe entspricht nicht dem gesuchten Morsecode.")

    # ------------------------------------------------------------------
    # Public keyboard/GPIO entry points
    # ------------------------------------------------------------------

    @Slot(str)
    def buttonPressed(self, button_name: str) -> None:
        """
        Called from QML keyboard simulation.

        Expected names:
            single
            left
            right
        """

        if not self._running:
            return

        button_name = button_name.strip().lower()

        if button_name not in {
            "single",
            "left",
            "right",
        }:
            print(f"Unknown button name: {button_name!r}")
            return

        # Prevent repeated key-down events from replacing the start time.
        if button_name in self._pressed_at:
            return

        self._pressed_at[button_name] = time.monotonic()

        print(f"Button pressed: {button_name}")

    @Slot(str)
    def buttonReleased(self, button_name: str) -> None:
        """
        Called from QML keyboard simulation.
        """

        if not self._running:
            return

        button_name = button_name.strip().lower()

        pressed_at = self._pressed_at.pop(
            button_name,
            None,
        )

        if pressed_at is None:
            return

        duration = time.monotonic() - pressed_at
        button_function = self._function_for_button(button_name)

        print(
            f"Button released: {button_name}, "
            f"duration={duration:.3f}s, "
            f"function={button_function}"
        )

        self._process_button_release(
            button_function,
            duration,
        )

    # ------------------------------------------------------------------
    # Input processing
    # ------------------------------------------------------------------

    def _function_for_button(
        self,
        button_name: str,
    ) -> str:
        if button_name == "single":
            return "Zeitgesteuert"

        if button_name == "left":
            return self._left_type

        if button_name == "right":
            return self._right_type

        return "Pause"

    def _process_button_release(
        self,
        button_function: str,
        duration: float,
    ) -> None:
        if button_function == "Kurz":
            self._append_symbol(".")
            return

        if button_function == "Lang":
            self._append_symbol("_")
            return

        if button_function == "Pause":
            # Pause is currently ignored in letter mode.
            return

        if button_function == "Zeitgesteuert":
            if duration <= 0.25:
                self._append_symbol(".")
            else:
                self._append_symbol("_")
            return

        print(f"Unknown button function: " f"{button_function!r}")

    def _append_symbol(self, symbol: str) -> None:
        if not self._running:
            return

        self._input += symbol
        self.inputChanged.emit()

        print(f"Input: {self._input}; " f"expected: {self.morse}")

        if not self.morse.startswith(self._input):
            self._emit_mistake("Das zuletzt eingegebene Zeichen ist falsch.")
            return

        if self._input == self.morse:
            self._emit_correct()

    def _emit_correct(self) -> None:
        elapsed = time.monotonic() - self._started_at

        self._running = False
        self._pressed_at.clear()
        self.runningChanged.emit()

        self.correct.emit(elapsed)

    def _emit_mistake(
        self,
        explanation: str,
    ) -> None:
        self._last_mistake_entered = self._input
        self._last_mistake_expected = self.morse
        self._last_mistake_explanation = explanation

        print(
            "Emitting mistake:",
            f"entered={self._last_mistake_entered!r},",
            f"expected={self._last_mistake_expected!r},",
            f"explanation={self._last_mistake_explanation!r}",
        )

        self._running = False
        self._pressed_at.clear()

        self.mistakeDetailsChanged.emit()
        self.runningChanged.emit()
        self.mistake.emit()

    @staticmethod
    def _normalize_symbol(
        symbol: str,
    ) -> Optional[str]:
        if symbol in {".", "•"}:
            return "."

        if symbol in {
            "_",
            "-",
            "—",
        }:
            return "_"

        return None

    # ------------------------------------------------------------------
    # GPIO support
    # ------------------------------------------------------------------

    def _setup_gpio(self) -> None:
        if Button is None:
            print("GPIO unavailable: keyboard development " "mode can still be used.")
            return

        try:
            self._single_button = Button(
                self._single_pin,
                bounce_time=0.01,
            )

            self._single_button.when_pressed = lambda: self.buttonPressed("single")
            self._single_button.when_released = lambda: self.buttonReleased("single")

            # Do not create the left button a second time when it uses
            # the same pin as the single button.
            if self._left_pin != self._single_pin:
                self._left_button = Button(
                    self._left_pin,
                    bounce_time=0.01,
                )

                self._left_button.when_pressed = lambda: self.buttonPressed("left")
                self._left_button.when_released = lambda: self.buttonReleased("left")

            self._right_button = Button(
                self._right_pin,
                bounce_time=0.01,
            )

            self._right_button.when_pressed = lambda: self.buttonPressed("right")
            self._right_button.when_released = lambda: self.buttonReleased("right")

        except Exception as error:
            print(f"GPIO input unavailable: {error}")
