from __future__ import annotations

import time
from typing import Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

try:
    from gpiozero import Button
except ImportError:  # Allows development on macOS/Windows without GPIO hardware.
    Button = None


MORSE_TO_LETTER = {
    "._": "a", "_...": "b", "_._.": "c", "_..": "d", ".": "e",
    ".._.": "f", "__.": "g", "....": "h", "..": "i", ".___": "j",
    "_._": "k", "._..": "l", "__": "m", "_.": "n", "___": "o",
    ".__.": "p", "__._": "q", "._.": "r", "...": "s", "_": "t",
    ".._": "u", "..._": "v", ".__": "w", "_.._": "x", "_.__": "y",
    "__..": "z",
}
LETTER_TO_MORSE = {letter: code for code, letter in MORSE_TO_LETTER.items()}


class LetterTrainer(QObject):
    """Reactive bridge between the Morse input hardware and QML."""

    letterChanged = Signal()
    morseChanged = Signal()
    inputChanged = Signal()
    runningChanged = Signal()
    correct = Signal(float)
    mistake = Signal(str, str)

    def __init__(self, pin: int = 17, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._letter = "l"
        self._input = ""
        self._running = False
        self._started_at = 0.0
        self._last_change = time.monotonic()
        self._button = None

        if Button is not None:
            try:
                self._button = Button(pin, bounce_time=0.01)
                self._button.when_pressed = self._button_pressed
                self._button.when_released = self._button_released
            except Exception as error:
                print(f"GPIO input unavailable: {error}")

    @Property(str, notify=letterChanged)
    def letter(self) -> str:
        return self._letter

    @Property(str, notify=morseChanged)
    def morse(self) -> str:
        return LETTER_TO_MORSE.get(self._letter.lower(), "")

    @Property(str, notify=inputChanged)
    def currentInput(self) -> str:
        return self._input

    @Property(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._running

    @Slot(str)
    def startLetter(self, letter: str) -> None:
        normalized = letter[:1].lower()
        if normalized not in LETTER_TO_MORSE:
            return

        self._letter = normalized
        self._input = ""
        self._running = True
        self._started_at = time.monotonic()
        self._last_change = self._started_at
        self.letterChanged.emit()
        self.morseChanged.emit()
        self.inputChanged.emit()
        self.runningChanged.emit()

    @Slot()
    def stop(self) -> None:
        if self._running:
            self._running = False
            self.runningChanged.emit()

    @Slot(str)
    def submitSymbol(self, symbol: str) -> None:
        """Useful for keyboard testing; hardware calls the same logic."""
        if symbol in (".", "_"):
            self._append_symbol(symbol)

    @Slot()
    def finishLetter(self) -> None:
        if not self._running:
            return

        expected = self.morse
        if self._input == expected:
            elapsed = time.monotonic() - self._started_at
            self._running = False
            self.runningChanged.emit()
            self.correct.emit(elapsed)
        else:
            self._fail()

    def _append_symbol(self, symbol: str) -> None:
        if not self._running:
            return

        self._input += symbol
        self.inputChanged.emit()

        # Stop immediately after the first impossible symbol.
        if not self.morse.startswith(self._input):
            self._fail()
        elif self._input == self.morse:
            # A complete correct code can be accepted immediately.
            elapsed = time.monotonic() - self._started_at
            self._running = False
            self.runningChanged.emit()
            self.correct.emit(elapsed)

    def _fail(self) -> None:
        entered = self._input
        expected = self.morse
        self._running = False
        self.runningChanged.emit()
        self.mistake.emit(entered, expected)

    def _button_pressed(self) -> None:
        now = time.monotonic()
        released_for = now - self._last_change
        self._last_change = now

        # A longer pause marks the end of the current letter.
        if self._running and released_for >= 0.48 and self._input:
            self.finishLetter()

    def _button_released(self) -> None:
        now = time.monotonic()
        pressed_for = now - self._last_change
        self._last_change = now

        if pressed_for <= 0.2:
            self._append_symbol(".")
        elif pressed_for < 0.5:
            self._append_symbol("_")
