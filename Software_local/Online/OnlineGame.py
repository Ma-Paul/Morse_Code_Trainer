from __future__ import annotations

import time

from PySide6.QtCore import QObject, Property, QTimer, Signal, Slot


class OnlineGame(QObject):
    stateChanged = Signal()
    finished = Signal(int, float)

    def __init__(self, online_bridge, letter, word, sentence, parent=None):
        super().__init__(parent)
        self.bridge = online_bridge
        self.letter = letter
        self.word = word
        self.sentence = sentence

        self._match_id = -1
        self._mode = ""
        self._challenges = []
        self._index = 0
        self._score = 0
        self._running = False
        self._started = 0.0
        self._duration = 120
        self._showing_correct = False
        self._showing_mistake = False
        self._advance_pending = False

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._tick)

        self.feedback_timer = QTimer(self)
        self.feedback_timer.setSingleShot(True)
        self.feedback_timer.setInterval(1000)
        self.feedback_timer.timeout.connect(self._advance_after_feedback)

        self.letter.correct.connect(self._correct)
        self.letter.mistake.connect(self._mistake)
        self.word.wordCorrect.connect(self._correct)
        self.word.mistake.connect(self._mistake)
        self.sentence.sentenceCorrect.connect(self._correct)
        self.sentence.mistake.connect(self._mistake)

    @Property(str, notify=stateChanged)
    def mode(self):
        return self._mode

    @Property(str, notify=stateChanged)
    def challenge(self):
        if self._challenges and self._index < len(self._challenges):
            return self._challenges[self._index]
        return ""

    @Property(int, notify=stateChanged)
    def score(self):
        return self._score

    @Property(int, notify=stateChanged)
    def secondsLeft(self):
        if not self._running:
            return 0
        return max(0, int(self._duration - (time.monotonic() - self._started)))

    @Property(bool, notify=stateChanged)
    def running(self):
        return self._running

    @Property(bool, notify=stateChanged)
    def showingCorrect(self):
        return self._showing_correct

    @Property(bool, notify=stateChanged)
    def showingMistake(self):
        return self._showing_mistake

    def trainer(self):
        if self._mode == "Letter":
            return self.letter
        if self._mode == "Word":
            return self.word
        return self.sentence

    @Slot(str, str, str)
    def configureInput(self, input_type, left_type, right_type):
        self.letter.configureInput(input_type, left_type, right_type)
        self.word.configureInput(input_type, left_type, right_type)
        self.sentence.configureInput(input_type, left_type, right_type)

    @Slot(int, result=bool)
    def start(self, match_id):
        data = self.bridge.loadMatch(match_id)
        if not data:
            return False

        self.feedback_timer.stop()
        self._match_id = match_id
        self._mode = data["mode"]
        self._challenges = list(data["challenges"])
        self._duration = int(data.get("duration_seconds", 120))
        self._index = 0
        self._score = 0
        self._started = time.monotonic()
        self._running = True
        self._showing_correct = False
        self._showing_mistake = False
        self._advance_pending = False

        self._start_current()
        self.timer.start()
        self.stateChanged.emit()
        return True

    def _start_current(self):
        if not self._running or self._index >= len(self._challenges):
            self._finish()
            return

        self._showing_correct = False
        self._showing_mistake = False
        self._advance_pending = False

        value = self._challenges[self._index]
        if self._mode == "Letter":
            self.letter.startLetter(value)
        elif self._mode == "Word":
            self.word.startWord(value)
        else:
            self.sentence.startSentence(value)

        self.stateChanged.emit()

    @Slot(str)
    def buttonPressed(self, name):
        if self._running and not self._advance_pending:
            self.trainer().buttonPressed(name)

    @Slot(str)
    def buttonReleased(self, name):
        if self._running:
            self.trainer().buttonReleased(name)

    def _correct(self, *args):
        if not self._running or self._advance_pending:
            return

        self._score += 1
        self._showing_correct = True
        self._showing_mistake = False
        self._advance_pending = True
        self.stateChanged.emit()
        self.feedback_timer.start()

    def _mistake(self, *args):
        if not self._running or self._advance_pending:
            return

        self._showing_correct = False
        self._showing_mistake = True
        self._advance_pending = True
        self.stateChanged.emit()
        self.feedback_timer.start()

    def _advance_after_feedback(self):
        if not self._running:
            return

        self._index += 1
        self._start_current()

    def _tick(self):
        self.stateChanged.emit()
        if time.monotonic() - self._started >= self._duration:
            self._finish()

    def _finish(self):
        if not self._running:
            return

        elapsed = min(self._duration, time.monotonic() - self._started)
        self._running = False
        self.timer.stop()
        self.feedback_timer.stop()
        self._advance_pending = False
        self._showing_correct = False
        self._showing_mistake = False
        self.trainer().stop()
        self.bridge.submitMatch(self._match_id, self._score, elapsed)
        self.stateChanged.emit()
        self.finished.emit(self._score, elapsed)
