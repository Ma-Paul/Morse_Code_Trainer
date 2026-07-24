from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QObject, Property, Signal, Slot

from Letter import LetterTrainer


class TrainingDispatcher(QObject):
    """Owns the training backends and exposes only the currently active one to QML.

    Letter, word, sentence, and online modes can all be added here later.  This
    guarantees that only one input handler is active at a time.
    """

    activeModeChanged = Signal()

    # Signals relayed from the active letter trainer.
    letterChanged = Signal()
    morseChanged = Signal()
    inputChanged = Signal()
    runningChanged = Signal()
    correct = Signal(float)
    mistake = Signal(str, str)

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._active_mode = ""
        self._letter = LetterTrainer(parent=self)

        self._letter.letterChanged.connect(self.letterChanged)
        self._letter.morseChanged.connect(self.morseChanged)
        self._letter.inputChanged.connect(self.inputChanged)
        self._letter.runningChanged.connect(self.runningChanged)
        self._letter.correct.connect(self.correct)
        self._letter.mistake.connect(self.mistake)

    @Property(str, notify=activeModeChanged)
    def activeMode(self) -> str:
        return self._active_mode

    @Property(str, notify=letterChanged)
    def letter(self) -> str:
        return self._letter.letter

    @Property(str, notify=morseChanged)
    def morse(self) -> str:
        return self._letter.morse

    @Property(str, notify=inputChanged)
    def currentInput(self) -> str:
        return self._letter.currentInput

    @Property(bool, notify=runningChanged)
    def running(self) -> bool:
        return self._letter.running

    @Slot(str)
    def activate(self, mode: str) -> None:
        normalized = mode.strip().lower()
        if normalized == self._active_mode:
            return

        self._stop_active_trainer()
        self._active_mode = normalized
        self.activeModeChanged.emit()

    @Slot(str)
    def deactivate(self, mode: str = "") -> None:
        normalized = mode.strip().lower()
        if normalized and normalized != self._active_mode:
            return

        self._stop_active_trainer()
        if self._active_mode:
            self._active_mode = ""
            self.activeModeChanged.emit()

    @Slot(str)
    def startLetter(self, letter: str) -> None:
        if self._active_mode != "letter":
            self.activate("letter")
        self._letter.startLetter(letter)

    @Slot(str)
    def submitSymbol(self, symbol: str) -> None:
        if self._active_mode == "letter":
            self._letter.submitSymbol(symbol)

    @Slot()
    def finishLetter(self) -> None:
        if self._active_mode == "letter":
            self._letter.finishLetter()

    @Slot()
    def stop(self) -> None:
        self._stop_active_trainer()

    def _stop_active_trainer(self) -> None:
        if self._active_mode == "letter":
            self._letter.stop()
        # Future modes are stopped here as they are added.
