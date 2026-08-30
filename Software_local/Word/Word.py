from __future__ import annotations

import json
import random
import time
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

try:
    from gpiozero import Button
except ImportError:
    Button = None


LETTER_TO_MORSE = {
    "a": "._",
    "b": "_...",
    "c": "_._.",
    "d": "_..",
    "e": ".",
    "f": ".._.",
    "g": "__.",
    "h": "....",
    "i": "..",
    "j": ".___",
    "k": "_._",
    "l": "._..",
    "m": "__",
    "n": "_.",
    "o": "___",
    "p": ".__.",
    "q": "__._",
    "r": "._.",
    "s": "...",
    "t": "_",
    "u": ".._",
    "v": "..._",
    "w": ".__",
    "x": "_.._",
    "y": "_.__",
    "z": "__..",
}


class WordTrainer(QObject):
    """
    Morse word trainer.

    A completed letter is followed by a short letter gap.

    Without an explicit Pause button:
        The gap is detected by waiting DIT_SECONDS without another press.

    With an explicit Pause button:
        The user presses the Pause button for at least DIT_SECONDS.
    """

    DIT_SECONDS = 0.25
    LETTER_GAP_MIN_SECONDS = 0.18
    LETTER_GAP_MAX_SECONDS = 0.25

    wordChanged = Signal()
    letterChanged = Signal()
    letterIndexChanged = Signal()
    morseChanged = Signal()
    inputChanged = Signal()
    completedLettersChanged = Signal()
    waitingForGapChanged = Signal()
    runningChanged = Signal()

    wordCorrect = Signal(
        float,
        arguments=["elapsedSeconds"],
    )

    mistakeDetailsChanged = Signal()
    mistake = Signal()

    def __init__(
        self,
        single_pin: int = 17,
        left_pin: int = 17,
        right_pin: int = 27,
        setup_gpio: bool = True,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._word = "house"
        self._letter_index = 0
        self._input = ""
        self._completed_letters = 0

        self._running = False
        self._waiting_for_gap = False
        self._started_at = 0.0

        self._input_type = "1"
        self._left_type = "Zeitgesteuert"
        self._right_type = "Zeitgesteuert"

        self._pressed_at: dict[str, float] = {}

        self._last_mistake_entered = ""
        self._last_mistake_expected = ""
        self._last_mistake_explanation = ""

        self._words = self._load_words()

        self._single_button = None
        self._left_button = None
        self._right_button = None

        self._single_pin = single_pin
        self._left_pin = left_pin
        self._right_pin = right_pin
        self._letter_completed_at: Optional[float] = None
        if setup_gpio:
            self._setup_gpio()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @Property(str, notify=wordChanged)
    def word(self) -> str:
        return self._word

    @Property(int, notify=letterIndexChanged)
    def letterIndex(self) -> int:
        return self._letter_index

    @Property(str, notify=letterChanged)
    def currentLetter(self) -> str:
        if not self._word:
            return ""

        if self._letter_index >= len(self._word):
            return ""

        return self._word[self._letter_index]

    @Property(str, notify=morseChanged)
    def morse(self) -> str:
        return LETTER_TO_MORSE.get(
            self.currentLetter.lower(),
            "",
        )

    @Property(str, notify=inputChanged)
    def currentInput(self) -> str:
        return self._input

    @Property(int, notify=completedLettersChanged)
    def completedLetters(self) -> int:
        return self._completed_letters

    @Property(bool, notify=waitingForGapChanged)
    def waitingForLetterGap(self) -> bool:
        return self._waiting_for_gap

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
        self._input_type = str(input_type or "1")
        self._left_type = left_type or "Zeitgesteuert"
        self._right_type = right_type or "Zeitgesteuert"

        print(
            "Word input configured:",
            f"type={self._input_type},",
            f"left={self._left_type},",
            f"right={self._right_type}",
        )

    # ------------------------------------------------------------------
    # Training control
    # ------------------------------------------------------------------

    @Slot()
    def startRandomWord(self) -> None:
        if self._words:
            word = random.choice(self._words)
        else:
            word = "house"

        self.startWord(word)

    @Slot(str)
    def startWord(self, word: str) -> None:
        normalized = "".join(
            character for character in word.lower() if character in LETTER_TO_MORSE
        )

        if not normalized:
            print(f"Invalid word: {word!r}")
            return

        self._word = normalized
        self._letter_index = 0
        self._completed_letters = 0
        self._input = ""

        self._running = True

        # Important: a new word must never start in gap mode.
        self._waiting_for_gap = False
        self._letter_completed_at = None
        self._pressed_at.clear()

        self._started_at = time.monotonic()

        self.wordChanged.emit()
        self.letterIndexChanged.emit()
        self.completedLettersChanged.emit()
        self.letterChanged.emit()
        self.morseChanged.emit()
        self.inputChanged.emit()
        self.waitingForGapChanged.emit()
        self.runningChanged.emit()

        print(
            f"New word: {self._word.upper()}, "
            f"running={self._running}, "
            f"waitingForGap={self._waiting_for_gap}"
        )

    @Slot()
    def stop(self) -> None:
        self._letter_completed_at = None
        self._pressed_at.clear()

        waiting_changed = self._waiting_for_gap
        running_changed = self._running

        self._waiting_for_gap = False
        self._running = False

        if waiting_changed:
            self.waitingForGapChanged.emit()

        if running_changed:
            self.runningChanged.emit()

    # ------------------------------------------------------------------
    # Button input
    # ------------------------------------------------------------------

    @Slot(str)
    def buttonPressed(self, button_name: str) -> None:
        button_name = button_name.strip().lower()

        print(
            "buttonPressed:",
            button_name,
            f"running={self._running}",
            f"waiting={self._waiting_for_gap}",
            f"letter={self.currentLetter}",
            f"input={self._input!r}",
            f"pressed_before={list(self._pressed_at.keys())}",
        )

        if not self._running:
            print("Press ignored: trainer is not running")
            return

        if button_name not in {"single", "left", "right"}:
            print("Press ignored: unknown button", button_name)
            return

        if button_name in self._pressed_at:
            print("Press ignored: button already held", button_name)
            return

        button_function = self._function_for_button(button_name)
        now = time.monotonic()

        # In implicit-gap mode, the next letter is already displayed.
        # The first press for that letter also confirms the preceding gap.
        if (
            self._waiting_for_gap
            and not self._uses_explicit_pause()
            and button_function != "Pause"
        ):
            if self._letter_completed_at is None:
                print(
                    "Invalid gap state: no completion timestamp; " "resetting gap state"
                )

                self._waiting_for_gap = False
                self.waitingForGapChanged.emit()

            else:
                gap_duration = now - self._letter_completed_at

                print(
                    "Implicit letter gap:",
                    f"{gap_duration:.3f}s",
                )

                if gap_duration < self.LETTER_GAP_MIN_SECONDS:
                    self._emit_mistake(
                        "Die Pause zwischen den Buchstaben " "war zu kurz."
                    )
                    return

                self._waiting_for_gap = False
                self._letter_completed_at = None
                self.waitingForGapChanged.emit()

        # Store every accepted press.
        self._pressed_at[button_name] = now

        print(
            "Press stored:",
            button_name,
            f"function={button_function}",
            f"pressed_after={list(self._pressed_at.keys())}",
        )

    @Slot(str)
    def buttonReleased(self, button_name: str) -> None:
        button_name = button_name.strip().lower()

        print(
            "buttonReleased:",
            button_name,
            f"running={self._running}",
            f"waiting={self._waiting_for_gap}",
            f"pressed_before={list(self._pressed_at.keys())}",
        )

        if not self._running:
            print("Release ignored: trainer is not running")
            return

        pressed_at = self._pressed_at.pop(
            button_name,
            None,
        )

        if pressed_at is None:
            print(
                "Release ignored: no matching press for",
                button_name,
            )
            return

        duration = time.monotonic() - pressed_at
        button_function = self._function_for_button(button_name)

        print(
            "Release accepted:",
            button_name,
            f"function={button_function}",
            f"duration={duration:.3f}s",
            f"pressed_after={list(self._pressed_at.keys())}",
        )

        self._process_button_release(
            button_function,
            duration,
        )

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
        print(
            "_process_button_release:",
            button_function,
            f"duration={duration:.3f}",
            f"waiting={self._waiting_for_gap}",
        )

        if button_function == "Pause":
            self._process_pause(duration)
            return

        # With an explicit Pause button, ordinary Morse buttons must
        # not start the next letter until Pause has been entered.
        if self._waiting_for_gap and self._uses_explicit_pause():
            print("Symbol ignored: waiting for explicit Pause button")
            return

        if button_function == "Kurz":
            self._append_symbol(".")
            return

        if button_function == "Lang":
            self._append_symbol("_")
            return

        if button_function == "Zeitgesteuert":
            symbol = "." if duration < self.DIT_SECONDS else "_"

            self._append_symbol(symbol)
            return

        print(
            "Unknown button function:",
            button_function,
        )

    def _process_pause(
        self,
        duration: float,
    ) -> None:
        if not self._waiting_for_gap:
            print("Pause ignored: not waiting for a letter gap")
            return

        if duration < self.LETTER_GAP_MAX_SECONDS:
            self._advance_to_next_letter()
            return

        # Reserved for a later sentence mode.
        print(
            "Pause press too long for a letter break:",
            f"{duration:.3f}s",
        )

    # ------------------------------------------------------------------
    # Morse processing
    # ------------------------------------------------------------------

    def _append_symbol(
        self,
        symbol: str,
    ) -> None:
        if not self._running:
            return

        if self._waiting_for_gap:
            print("Symbol ignored: trainer is waiting for a gap")
            return

        self._input += symbol
        self.inputChanged.emit()

        print(
            f"Word={self._word}, "
            f"letter={self.currentLetter}, "
            f"input={self._input}, "
            f"expected={self.morse}"
        )

        if not self.morse.startswith(self._input):
            self._emit_mistake("Das zuletzt eingegebene Zeichen ist falsch.")
            return

        if self._input == self.morse:
            self._complete_current_letter()

    def _complete_current_letter(self) -> None:
        self._completed_letters = self._letter_index + 1
        self.completedLettersChanged.emit()

        # The entire word is complete.
        if self._letter_index >= len(self._word) - 1:
            self._emit_word_correct()
            return

        self._letter_completed_at = time.monotonic()
        self._waiting_for_gap = True

        if self._uses_explicit_pause():
            # Keep the completed letter visible until the short
            # Pause-button press has been entered.
            self.waitingForGapChanged.emit()

            print(
                f"Letter {self.currentLetter.upper()} completed; "
                "waiting for explicit Pause button."
            )

        else:
            # Immediately display the next letter. The gap is checked
            # when its first button is pressed.
            self._show_next_letter_while_waiting_for_gap()

    def _show_next_letter_while_waiting_for_gap(
        self,
    ) -> None:
        self._letter_index += 1
        self._input = ""

        # Deliberately retain:
        # self._waiting_for_gap = True

        self.letterIndexChanged.emit()
        self.letterChanged.emit()
        self.morseChanged.emit()
        self.inputChanged.emit()
        self.waitingForGapChanged.emit()

        print(
            f"Showing next letter: "
            f"{self.currentLetter.upper()} ({self.morse}); "
            "waiting for implicit letter gap."
        )

    def _advance_to_next_letter(self) -> None:
        if not self._running:
            return

        if not self._waiting_for_gap:
            return

        self._letter_index += 1
        self._input = ""
        self._waiting_for_gap = False
        self._letter_completed_at = None

        self.letterIndexChanged.emit()
        self.letterChanged.emit()
        self.morseChanged.emit()
        self.inputChanged.emit()
        self.waitingForGapChanged.emit()

        print(f"Next letter: " f"{self.currentLetter.upper()} " f"({self.morse})")

    def _uses_explicit_pause(self) -> bool:
        if self._input_type != "2":
            return False

        return self._left_type == "Pause" or self._right_type == "Pause"

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def _emit_word_correct(self) -> None:
        elapsed = time.monotonic() - self._started_at

        self._running = False
        self._waiting_for_gap = False
        self._pressed_at.clear()

        self.waitingForGapChanged.emit()
        self.runningChanged.emit()

        self.wordCorrect.emit(elapsed)

    def _emit_mistake(self, explanation: str) -> None:
        self._last_mistake_entered = self._input
        self._last_mistake_expected = self.morse
        self._last_mistake_explanation = explanation

        self._running = False
        self._waiting_for_gap = False
        self._pressed_at.clear()

        self.mistakeDetailsChanged.emit()
        self.waitingForGapChanged.emit()
        self.runningChanged.emit()
        self.mistake.emit()

    # ------------------------------------------------------------------
    # Word list
    # ------------------------------------------------------------------

    def _load_words(self) -> list[str]:
        word_file = Path(__file__).resolve().parent / "data_w.json"

        try:
            data = json.loads(word_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"Could not load {word_file}: {error}")
            return []

        raw_words = data.get("words", [])

        # Avoid one-letter words initially. Limiting the length also
        # keeps the first version comfortable on smaller displays.
        return [
            word.lower()
            for word in raw_words
            if (
                isinstance(word, str)
                and 2 <= len(word) <= 6
                and word.isalpha()
                and all(character in LETTER_TO_MORSE for character in word.lower())
            )
        ]

    # ------------------------------------------------------------------
    # GPIO
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
