from __future__ import annotations

import time
from typing import Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

try:
    from gpiozero import Button
except ImportError:
    Button = None


# ============================================================
# GPIO CONFIGURATION
# ============================================================
#
# Enter the BCM GPIO numbers here.
#
# Example:
# GPIO 17 means BCM GPIO17, physical header pin 11.
#
# For a one-button input, SINGLE_BUTTON_PIN is used.
#
# For a two-button input:
# LEFT_BUTTON_PIN and RIGHT_BUTTON_PIN are used.
#
# ============================================================

SINGLE_BUTTON_PIN = 17  # TODO: replace with the correct BCM pin
LEFT_BUTTON_PIN = 17  # TODO: replace with the correct BCM pin
RIGHT_BUTTON_PIN = 27  # TODO: replace with the correct BCM pin


# Maximum press duration that is interpreted as a short symbol.
SHORT_PRESS_LIMIT = 0.22

# A pause longer than this finishes the current letter.
LETTER_PAUSE_TIME = 0.65


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
    letterChanged = Signal()
    morseChanged = Signal()
    inputChanged = Signal()
    runningChanged = Signal()

    correct = Signal(float)

    # entered code, expected code, explanation
    mistake = Signal(str, str, str)

    def __init__(
        self,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._letter = "l"
        self._input = ""
        self._running = False
        self._started_at = 0.0

        self._input_type = "1"
        self._left_type = "Zeitgesteuert"
        self._right_type = "Zeitgesteuert"

        self._single_button = None
        self._left_button = None
        self._right_button = None

        self._press_started = {
            "single": 0.0,
            "left": 0.0,
            "right": 0.0,
        }

    # --------------------------------------------------------
    # QML properties
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    @Slot(str, str, str)
    def configureInput(
        self,
        input_type: str,
        left_type: str,
        right_type: str,
    ) -> None:
        self._input_type = input_type.strip()
        self._left_type = left_type.strip()
        self._right_type = right_type.strip()

        self._close_buttons()

        if Button is None:
            print("gpiozero is unavailable. " "Keyboard input can still be used.")
            return

        try:
            if self._input_type == "2":
                self._configure_two_buttons()
            else:
                self._configure_single_button()

        except Exception as error:
            print(f"GPIO input could not be configured: {error}")
            self._close_buttons()

    def _configure_single_button(self) -> None:
        print(f"Configuring one-button input on BCM GPIO " f"{SINGLE_BUTTON_PIN}")

        self._single_button = Button(
            SINGLE_BUTTON_PIN,
            pull_up=True,
            bounce_time=0.01,
        )

        self._single_button.when_pressed = lambda: self._button_pressed("single")

        self._single_button.when_released = lambda: self._button_released(
            "single",
            "Zeitgesteuert",
        )

    def _configure_two_buttons(self) -> None:
        print(
            f"Configuring two-button input: "
            f"left BCM GPIO {LEFT_BUTTON_PIN}, "
            f"right BCM GPIO {RIGHT_BUTTON_PIN}"
        )

        self._left_button = Button(
            LEFT_BUTTON_PIN,
            pull_up=True,
            bounce_time=0.01,
        )

        self._right_button = Button(
            RIGHT_BUTTON_PIN,
            pull_up=True,
            bounce_time=0.01,
        )

        self._left_button.when_pressed = lambda: self._button_pressed("left")

        self._left_button.when_released = lambda: self._button_released(
            "left",
            self._left_type,
        )

        self._right_button.when_pressed = lambda: self._button_pressed("right")

        self._right_button.when_released = lambda: self._button_released(
            "right",
            self._right_type,
        )

    def _close_buttons(self) -> None:
        for button_name in (
            "_single_button",
            "_left_button",
            "_right_button",
        ):
            button = getattr(self, button_name)

            if button is not None:
                try:
                    button.close()
                except Exception:
                    pass

                setattr(self, button_name, None)

    # --------------------------------------------------------
    # Training control
    # --------------------------------------------------------

    @Slot(str)
    def startLetter(self, letter: str) -> None:
        normalized = letter[:1].lower()

        if normalized not in LETTER_TO_MORSE:
            return

        self._letter = normalized
        self._input = ""
        self._running = True
        self._started_at = time.monotonic()

        self.letterChanged.emit()
        self.morseChanged.emit()
        self.inputChanged.emit()
        self.runningChanged.emit()

    @Slot()
    def stop(self) -> None:
        if self._running:
            self._running = False
            self.runningChanged.emit()

    @Slot()
    def shutdown(self) -> None:
        self.stop()
        self._close_buttons()

    # --------------------------------------------------------
    # Keyboard testing
    # --------------------------------------------------------

    @Slot(str)
    def submitSymbol(self, symbol: str) -> None:
        if symbol == ".":
            self._append_symbol(".")

        elif symbol in ("_", "-"):
            self._append_symbol("_")

    @Slot()
    def finishLetter(self) -> None:
        if not self._running:
            return

        expected = self.morse

        if self._input == expected:
            self._finish_correct()
        else:
            explanation = self._describe_error(
                self._input,
                expected,
            )

            self._finish_mistake(explanation)

    # --------------------------------------------------------
    # GPIO handling
    # --------------------------------------------------------

    def _button_pressed(self, button_name: str) -> None:
        self._press_started[button_name] = time.monotonic()

    def _button_released(
        self,
        button_name: str,
        configured_type: str,
    ) -> None:
        if not self._running:
            return

        normalized_type = configured_type.strip().lower()

        if normalized_type == "pause":
            return

        if normalized_type in ("kurz", "short"):
            self._append_symbol(".")
            return

        if normalized_type in ("lang", "long"):
            self._append_symbol("_")
            return

        started = self._press_started.get(
            button_name,
            time.monotonic(),
        )

        duration = time.monotonic() - started

        if duration <= SHORT_PRESS_LIMIT:
            self._append_symbol(".")
        else:
            self._append_symbol("_")

    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    def _append_symbol(self, symbol: str) -> None:
        if not self._running:
            return

        self._input += symbol
        self.inputChanged.emit()

        expected = self.morse

        if not expected.startswith(self._input):
            explanation = self._describe_error(
                self._input,
                expected,
            )

            self._finish_mistake(explanation)
            return

        if self._input == expected:
            self._finish_correct()

    def _finish_correct(self) -> None:
        elapsed = time.monotonic() - self._started_at

        self._running = False
        self.runningChanged.emit()
        self.correct.emit(elapsed)

    def _finish_mistake(self, explanation: str) -> None:
        entered = self._input
        expected = self.morse

        self._running = False
        self.runningChanged.emit()

        self.mistake.emit(
            entered,
            expected,
            explanation,
        )

    @staticmethod
    def _describe_error(
        entered: str,
        expected: str,
    ) -> str:
        common_length = min(
            len(entered),
            len(expected),
        )

        for position in range(common_length):
            if entered[position] != expected[position]:
                entered_name = "kurz" if entered[position] == "." else "lang"

                expected_name = "kurz" if expected[position] == "." else "lang"

                return (
                    f"Das Zeichen {position + 1} war "
                    f"{entered_name}, erwartet wurde "
                    f"{expected_name}."
                )

        if len(entered) > len(expected):
            return "Du hast mindestens ein Zeichen zu viel eingegeben."

        if len(entered) < len(expected):
            missing = len(expected) - len(entered)

            return f"Es fehlen noch {missing} " f"Morsezeichen."

        return "Der eingegebene Morsecode war nicht korrekt."
