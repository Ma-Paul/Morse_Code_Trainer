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
    "a": "._", "b": "_...", "c": "_._.", "d": "_..", "e": ".",
    "f": ".._.", "g": "__.", "h": "....", "i": "..", "j": ".___",
    "k": "_._", "l": "._..", "m": "__", "n": "_.", "o": "___",
    "p": ".__.", "q": "__._", "r": "._.", "s": "...", "t": "_",
    "u": ".._", "v": "..._", "w": ".__", "x": "_.._", "y": "_.__",
    "z": "__..",
}


class SentenceTrainer(QObject):
    """Morse trainer for complete sentences."""

    DIT_SECONDS = 0.25

    # Gap validation when no dedicated Pause button is configured.
    LETTER_GAP_MIN_SECONDS = 0.18
    WORD_GAP_MIN_SECONDS = 0.55

    # Dedicated Pause button:
    # short press = letter gap, long press = word gap.
    WORD_PAUSE_THRESHOLD_SECONDS = 0.45

    sentenceChanged = Signal()
    wordChanged = Signal()
    wordIndexChanged = Signal()
    letterChanged = Signal()
    letterIndexChanged = Signal()
    morseChanged = Signal()
    inputChanged = Signal()
    completedWordsChanged = Signal()
    completedLettersChanged = Signal()
    waitingForGapChanged = Signal()
    runningChanged = Signal()

    sentenceCorrect = Signal(float, arguments=["elapsedSeconds"])

    mistakeDetailsChanged = Signal()
    mistake = Signal()

    def __init__(
        self,
        single_pin: int = 17,
        left_pin: int = 17,
        right_pin: int = 27,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        self._sentence = "the quick fox"
        self._words = ["the", "quick", "fox"]
        self._word_index = 0
        self._letter_index = 0
        self._input = ""
        self._completed_words = 0
        self._completed_letters = 0

        self._running = False
        self._waiting_gap_type = ""
        self._gap_started_at: Optional[float] = None
        self._started_at = 0.0

        self._input_type = "1"
        self._left_type = "Zeitgesteuert"
        self._right_type = "Zeitgesteuert"
        self._pressed_at: dict[str, float] = {}

        self._last_mistake_entered = ""
        self._last_mistake_expected = ""
        self._last_mistake_explanation = ""

        self._sentences = self._load_sentences()
        self._sentence_pool: list[str] = []
        self._last_sentence: str = ""

        self._single_button = None
        self._left_button = None
        self._right_button = None
        self._single_pin = single_pin
        self._left_pin = left_pin
        self._right_pin = right_pin
        self._setup_gpio()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @Property(str, notify=sentenceChanged)
    def sentence(self) -> str:
        return self._sentence

    @Property("QStringList", notify=sentenceChanged)
    def words(self) -> list[str]:
        return self._words

    @Property(int, notify=wordIndexChanged)
    def wordIndex(self) -> int:
        return self._word_index

    @Property(str, notify=wordChanged)
    def currentWord(self) -> str:
        if 0 <= self._word_index < len(self._words):
            return self._words[self._word_index]
        return ""

    @Property(int, notify=letterIndexChanged)
    def letterIndex(self) -> int:
        return self._letter_index

    @Property(str, notify=letterChanged)
    def currentLetter(self) -> str:
        word = self.currentWord
        if 0 <= self._letter_index < len(word):
            return word[self._letter_index]
        return ""

    @Property(str, notify=morseChanged)
    def morse(self) -> str:
        return LETTER_TO_MORSE.get(self.currentLetter.lower(), "")

    @Property(str, notify=inputChanged)
    def currentInput(self) -> str:
        return self._input

    @Property(int, notify=completedWordsChanged)
    def completedWords(self) -> int:
        return self._completed_words

    @Property(int, notify=completedLettersChanged)
    def completedLetters(self) -> int:
        return self._completed_letters

    @Property(bool, notify=waitingForGapChanged)
    def waitingForLetterGap(self) -> bool:
        return self._waiting_gap_type == "letter"

    @Property(bool, notify=waitingForGapChanged)
    def waitingForWordGap(self) -> bool:
        return self._waiting_gap_type == "word"

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
    # Configuration and control
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
            "Sentence input configured:",
            f"type={self._input_type},",
            f"left={self._left_type},",
            f"right={self._right_type}",
        )

    @Slot()
    def startRandomSentence(self) -> None:
        self.startSentence(self._next_random_sentence())

    def _next_random_sentence(self) -> str:
        """Return each sentence once before any sentence can repeat."""
        if not self._sentences:
            return "the quick fox"

        if not self._sentence_pool:
            self._sentence_pool = self._sentences.copy()
            random.shuffle(self._sentence_pool)

            # Prevent an immediate repeat at the boundary between two pools.
            if (
                len(self._sentence_pool) > 1
                and self._sentence_pool[-1] == self._last_sentence
            ):
                self._sentence_pool[0], self._sentence_pool[-1] = (
                    self._sentence_pool[-1],
                    self._sentence_pool[0],
                )

        sentence = self._sentence_pool.pop()
        self._last_sentence = sentence
        return sentence

    @Slot(str)
    def startSentence(self, sentence: str) -> None:
        normalized_words = []

        for raw_word in sentence.lower().split():
            word = "".join(
                character
                for character in raw_word
                if character in LETTER_TO_MORSE
            )
            if word:
                normalized_words.append(word)

        if len(normalized_words) < 2:
            print(f"Invalid sentence: {sentence!r}")
            return

        self._words = normalized_words
        self._sentence = " ".join(normalized_words)
        self._word_index = 0
        self._letter_index = 0
        self._input = ""
        self._completed_words = 0
        self._completed_letters = 0
        self._waiting_gap_type = ""
        self._gap_started_at = None
        self._pressed_at.clear()
        self._running = True
        self._started_at = time.monotonic()

        self.sentenceChanged.emit()
        self.wordIndexChanged.emit()
        self.wordChanged.emit()
        self.letterIndexChanged.emit()
        self.letterChanged.emit()
        self.morseChanged.emit()
        self.inputChanged.emit()
        self.completedWordsChanged.emit()
        self.completedLettersChanged.emit()
        self.waitingForGapChanged.emit()
        self.runningChanged.emit()

        print(f"New sentence: {self._sentence.upper()}")

    @Slot()
    def stop(self) -> None:
        waiting_changed = bool(self._waiting_gap_type)
        running_changed = self._running

        self._running = False
        self._waiting_gap_type = ""
        self._gap_started_at = None
        self._pressed_at.clear()

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

        if not self._running:
            return
        if button_name not in {"single", "left", "right"}:
            return
        if button_name in self._pressed_at:
            return

        button_function = self._function_for_button(button_name)
        now = time.monotonic()

        # In implicit-gap mode, the next target is already visible.
        # This same press validates the gap and starts the next letter.
        if (
            self._waiting_gap_type
            and not self._uses_explicit_pause()
            and button_function != "Pause"
        ):
            if self._gap_started_at is None:
                self._waiting_gap_type = ""
                self.waitingForGapChanged.emit()
            else:
                gap_duration = now - self._gap_started_at
                minimum = (
                    self.WORD_GAP_MIN_SECONDS
                    if self._waiting_gap_type == "word"
                    else self.LETTER_GAP_MIN_SECONDS
                )

                if gap_duration < minimum:
                    if self._waiting_gap_type == "word":
                        explanation = "Die Pause zwischen den Wörtern war zu kurz."
                    else:
                        explanation = "Die Pause zwischen den Buchstaben war zu kurz."
                    self._emit_mistake(explanation)
                    return

                self._waiting_gap_type = ""
                self._gap_started_at = None
                self.waitingForGapChanged.emit()

        self._pressed_at[button_name] = now

    @Slot(str)
    def buttonReleased(self, button_name: str) -> None:
        button_name = button_name.strip().lower()

        if not self._running:
            return

        pressed_at = self._pressed_at.pop(button_name, None)
        if pressed_at is None:
            return

        duration = time.monotonic() - pressed_at
        self._process_button_release(
            self._function_for_button(button_name),
            duration,
        )

    def _function_for_button(self, button_name: str) -> str:
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
        if button_function == "Pause":
            self._process_pause(duration)
            return

        if self._waiting_gap_type and self._uses_explicit_pause():
            print("Symbol ignored: waiting for explicit Pause button")
            return

        if button_function == "Kurz":
            self._append_symbol(".")
        elif button_function == "Lang":
            self._append_symbol("_")
        elif button_function == "Zeitgesteuert":
            self._append_symbol(
                "." if duration < self.DIT_SECONDS else "_"
            )

    def _process_pause(self, duration: float) -> None:
        if not self._waiting_gap_type:
            print("Pause ignored: not waiting for a gap")
            return

        is_long_pause = duration >= self.WORD_PAUSE_THRESHOLD_SECONDS

        if self._waiting_gap_type == "letter":
            if is_long_pause:
                self._emit_mistake(
                    "Die Pause zwischen den Buchstaben war zu lang."
                )
                return
            self._advance_after_explicit_gap()
            return

        if self._waiting_gap_type == "word":
            if not is_long_pause:
                self._emit_mistake(
                    "Die Pause zwischen den Wörtern war zu kurz."
                )
                return
            self._advance_after_explicit_gap()

    # ------------------------------------------------------------------
    # Morse processing
    # ------------------------------------------------------------------

    def _append_symbol(self, symbol: str) -> None:
        if not self._running or self._waiting_gap_type:
            return

        self._input += symbol
        self.inputChanged.emit()

        if not self.morse.startswith(self._input):
            self._emit_mistake("Das zuletzt eingegebene Zeichen ist falsch.")
            return

        if self._input == self.morse:
            self._complete_current_letter()

    def _complete_current_letter(self) -> None:
        self._completed_letters = self._letter_index + 1
        self.completedLettersChanged.emit()

        last_letter_in_word = self._letter_index >= len(self.currentWord) - 1
        last_word_in_sentence = self._word_index >= len(self._words) - 1

        if last_letter_in_word and last_word_in_sentence:
            self._completed_words = len(self._words)
            self.completedWordsChanged.emit()
            self._emit_sentence_correct()
            return

        self._gap_started_at = time.monotonic()

        if last_letter_in_word:
            self._completed_words = self._word_index + 1
            self.completedWordsChanged.emit()
            self._waiting_gap_type = "word"
        else:
            self._waiting_gap_type = "letter"

        if self._uses_explicit_pause():
            self.waitingForGapChanged.emit()
        else:
            self._show_next_target_while_waiting()

    def _show_next_target_while_waiting(self) -> None:
        if self._waiting_gap_type == "word":
            self._word_index += 1
            self._letter_index = 0
            self._completed_letters = 0
            self.wordIndexChanged.emit()
            self.wordChanged.emit()
            self.completedLettersChanged.emit()
        else:
            self._letter_index += 1
            self.letterIndexChanged.emit()

        self._input = ""
        self.letterChanged.emit()
        self.morseChanged.emit()
        self.inputChanged.emit()
        self.waitingForGapChanged.emit()

    def _advance_after_explicit_gap(self) -> None:
        if self._waiting_gap_type == "word":
            self._word_index += 1
            self._letter_index = 0
            self._completed_letters = 0
            self.wordIndexChanged.emit()
            self.wordChanged.emit()
            self.completedLettersChanged.emit()
        else:
            self._letter_index += 1
            self.letterIndexChanged.emit()

        self._input = ""
        self._waiting_gap_type = ""
        self._gap_started_at = None

        self.letterChanged.emit()
        self.morseChanged.emit()
        self.inputChanged.emit()
        self.waitingForGapChanged.emit()

    def _uses_explicit_pause(self) -> bool:
        if self._input_type != "2":
            return False
        return self._left_type == "Pause" or self._right_type == "Pause"

    # ------------------------------------------------------------------
    # Results
    # ------------------------------------------------------------------

    def _emit_sentence_correct(self) -> None:
        elapsed = time.monotonic() - self._started_at
        self._running = False
        self._waiting_gap_type = ""
        self._gap_started_at = None
        self._pressed_at.clear()

        self.waitingForGapChanged.emit()
        self.runningChanged.emit()
        self.sentenceCorrect.emit(elapsed)

    def _emit_mistake(self, explanation: str) -> None:
        self._last_mistake_entered = self._input
        self._last_mistake_expected = self.morse
        self._last_mistake_explanation = explanation

        self._running = False
        self._waiting_gap_type = ""
        self._gap_started_at = None
        self._pressed_at.clear()

        self.mistakeDetailsChanged.emit()
        self.waitingForGapChanged.emit()
        self.runningChanged.emit()
        self.mistake.emit()

    # ------------------------------------------------------------------
    # Sentence list
    # ------------------------------------------------------------------

    def _load_sentences(self) -> list[str]:
        sentence_file = Path(__file__).resolve().parent / "data_s.json"

        try:
            data = json.loads(sentence_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"Could not load {sentence_file}: {error}")
            return []

        raw_sentences = data.get("sentences", [])
        valid_sentences = []

        for sentence in raw_sentences:
            if not isinstance(sentence, str):
                continue

            normalized_words = []

            for raw_word in sentence.lower().split():
                word = "".join(
                    character
                    for character in raw_word
                    if character in LETTER_TO_MORSE
                )
                if word:
                    normalized_words.append(word)

            if len(normalized_words) >= 2:
                valid_sentences.append(sentence.strip())

        return valid_sentences

    # ------------------------------------------------------------------
    # GPIO
    # ------------------------------------------------------------------

    def _setup_gpio(self) -> None:
        if Button is None:
            print("GPIO unavailable: keyboard development mode can still be used.")
            return

        try:
            self._single_button = Button(self._single_pin, bounce_time=0.01)
            self._single_button.when_pressed = lambda: self.buttonPressed("single")
            self._single_button.when_released = lambda: self.buttonReleased("single")

            if self._left_pin != self._single_pin:
                self._left_button = Button(self._left_pin, bounce_time=0.01)
                self._left_button.when_pressed = lambda: self.buttonPressed("left")
                self._left_button.when_released = lambda: self.buttonReleased("left")

            self._right_button = Button(self._right_pin, bounce_time=0.01)
            self._right_button.when_pressed = lambda: self.buttonPressed("right")
            self._right_button.when_released = lambda: self.buttonReleased("right")

        except Exception as error:
            print(f"GPIO input unavailable: {error}")
