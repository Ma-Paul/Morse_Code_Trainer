from __future__ import annotations

import time

from PySide6.QtCore import QObject, Property, QTimer, Signal, Slot


class OnlineGame(QObject):
    stateChanged = Signal()
    activeTrainerChanged = Signal()

    finished = Signal(
        int,
        float,
    )

    def __init__(
        self,
        online_bridge,
        letter,
        word,
        sentence,
        parent=None,
    ):
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

    # ----------------------------------------------------------
    # Properties
    # ----------------------------------------------------------

    @Property(
        str,
        notify=stateChanged,
    )
    def mode(self) -> str:
        return self._mode

    @Property(
        str,
        notify=activeTrainerChanged,
    )
    def activeTrainerName(self) -> str:
        """
        Name used by PhysicalInputRouter.

        Possible values:
            Letter
            Word
            Sentence
        """
        return self._mode

    @Property(
        str,
        notify=stateChanged,
    )
    def challenge(self) -> str:
        if self._challenges and self._index < len(self._challenges):
            return self._challenges[self._index]

        return ""

    @Property(
        int,
        notify=stateChanged,
    )
    def score(self) -> int:
        return self._score

    @Property(
        int,
        notify=stateChanged,
    )
    def secondsLeft(self) -> int:
        if not self._running:
            return 0

        return max(
            0,
            int(self._duration - (time.monotonic() - self._started)),
        )

    @Property(
        bool,
        notify=stateChanged,
    )
    def running(self) -> bool:
        return self._running

    @Property(
        bool,
        notify=stateChanged,
    )
    def showingCorrect(self) -> bool:
        return self._showing_correct

    @Property(
        bool,
        notify=stateChanged,
    )
    def showingMistake(self) -> bool:
        return self._showing_mistake

    # ----------------------------------------------------------
    # Trainer selection
    # ----------------------------------------------------------

    def trainer(self):
        if self._mode == "Letter":
            return self.letter

        if self._mode == "Word":
            return self.word

        if self._mode == "Sentence":
            return self.sentence

        return None

    # ----------------------------------------------------------
    # Input configuration
    # ----------------------------------------------------------

    @Slot(
        str,
        str,
        str,
    )
    def configureInput(
        self,
        input_type,
        left_type,
        right_type,
    ) -> None:
        self.letter.configureInput(
            input_type,
            left_type,
            right_type,
        )

        self.word.configureInput(
            input_type,
            left_type,
            right_type,
        )

        self.sentence.configureInput(
            input_type,
            left_type,
            right_type,
        )

    # ----------------------------------------------------------
    # Game control
    # ----------------------------------------------------------

    @Slot()
    def stop(self) -> None:
        trainer = self.trainer()

        if trainer is not None:
            trainer.stop()

        self.timer.stop()
        self.feedback_timer.stop()

        was_running = self._running

        self._running = False

        self._advance_pending = False
        self._showing_correct = False
        self._showing_mistake = False

        if was_running:
            self.stateChanged.emit()

    @Slot(
        int,
        result=bool,
    )
    def start(
        self,
        match_id,
    ) -> bool:
        data = self.bridge.loadMatch(match_id)

        if not data:
            print(
                "OnlineGame: " "could not load match",
                match_id,
            )
            return False

        self.feedback_timer.stop()

        self._match_id = match_id

        new_mode = str(
            data.get(
                "mode",
                "",
            )
        )

        mode_changed = new_mode != self._mode

        self._mode = new_mode

        self._challenges = list(
            data.get(
                "challenges",
                [],
            )
        )

        self._duration = int(
            data.get(
                "duration_seconds",
                120,
            )
        )

        self._index = 0
        self._score = 0

        self._started = time.monotonic()
        self._running = True

        self._showing_correct = False
        self._showing_mistake = False
        self._advance_pending = False

        print(
            "OnlineGame started:",
            f"match={self._match_id}",
            f"mode={self._mode}",
            f"challenges={len(self._challenges)}",
        )

        # Tell QML / PhysicalInput which
        # trainer is now active.
        if mode_changed:
            self.activeTrainerChanged.emit()
        else:
            # Still emit it on every start so the
            # physical input router can resync.
            self.activeTrainerChanged.emit()

        self._start_current()

        self.timer.start()

        self.stateChanged.emit()

        return True

    # ----------------------------------------------------------
    # Challenge control
    # ----------------------------------------------------------

    def _start_current(
        self,
    ) -> None:
        if not self._running:
            return

        if self._index >= len(self._challenges):
            self._finish()
            return

        self._showing_correct = False
        self._showing_mistake = False
        self._advance_pending = False

        value = self._challenges[self._index]

        trainer = self.trainer()

        if trainer is None:
            print(
                "OnlineGame: " "no trainer for mode",
                self._mode,
            )
            self._finish()
            return

        print(
            "Online challenge:",
            self._index + 1,
            "/",
            len(self._challenges),
            "-",
            self._mode,
            "-",
            value,
        )

        if self._mode == "Letter":
            self.letter.startLetter(value)

        elif self._mode == "Word":
            self.word.startWord(value)

        elif self._mode == "Sentence":
            self.sentence.startSentence(value)

        self.stateChanged.emit()

    # ----------------------------------------------------------
    # Physical input entry points
    # ----------------------------------------------------------

    @Slot(str)
    def buttonPressed(
        self,
        name,
    ) -> None:
        if not self._running:
            return

        if self._advance_pending:
            return

        trainer = self.trainer()

        if trainer is None:
            return

        trainer.buttonPressed(name)

    @Slot(str)
    def buttonReleased(
        self,
        name,
    ) -> None:
        if not self._running:
            return

        if self._advance_pending:
            return

        trainer = self.trainer()

        if trainer is None:
            return

        trainer.buttonReleased(name)

    # ----------------------------------------------------------
    # Correct / mistake
    # ----------------------------------------------------------

    def _correct(
        self,
        *args,
    ) -> None:
        if not self._running:
            return

        if self._advance_pending:
            return

        self._score += 1

        self._showing_correct = True
        self._showing_mistake = False
        self._advance_pending = True

        print(
            "Online correct:",
            f"score={self._score}",
        )

        self.stateChanged.emit()

        self.feedback_timer.start()

    def _mistake(
        self,
        *args,
    ) -> None:
        if not self._running:
            return

        if self._advance_pending:
            return

        self._showing_correct = False
        self._showing_mistake = True
        self._advance_pending = True

        print("Online mistake")

        self.stateChanged.emit()

        self.feedback_timer.start()

    def _advance_after_feedback(
        self,
    ) -> None:
        if not self._running:
            return

        self._index += 1

        self._start_current()

    # ----------------------------------------------------------
    # Timer
    # ----------------------------------------------------------

    def _tick(
        self,
    ) -> None:
        self.stateChanged.emit()

        if time.monotonic() - self._started >= self._duration:
            self._finish()

    # ----------------------------------------------------------
    # Finish
    # ----------------------------------------------------------

    def _finish(
        self,
    ) -> None:
        if not self._running:
            return

        elapsed = min(
            self._duration,
            time.monotonic() - self._started,
        )

        self._running = False

        self.timer.stop()
        self.feedback_timer.stop()

        self._advance_pending = False
        self._showing_correct = False
        self._showing_mistake = False

        trainer = self.trainer()

        if trainer is not None:
            trainer.stop()

        print(
            "Online match finished:",
            f"score={self._score}",
            f"time={elapsed:.2f}",
        )

        self.bridge.submitMatch(
            self._match_id,
            self._score,
            elapsed,
        )

        self.stateChanged.emit()

        self.finished.emit(
            self._score,
            elapsed,
        )
