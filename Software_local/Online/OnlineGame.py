from __future__ import annotations
import time
from PySide6.QtCore import QObject, Property, QTimer, Signal, Slot

class OnlineGame(QObject):
    stateChanged=Signal(); finished=Signal(int,float)
    def __init__(self, online_bridge, letter, word, sentence, parent=None):
        super().__init__(parent); self.bridge=online_bridge; self.letter=letter; self.word=word; self.sentence=sentence
        self._match_id=-1; self._mode=''; self._challenges=[]; self._index=0; self._score=0; self._running=False; self._started=0.0; self._duration=120
        self.timer=QTimer(self); self.timer.setInterval(100); self.timer.timeout.connect(self._tick)
        self.letter.correct.connect(self._correct); self.letter.mistake.connect(self._mistake)
        self.word.wordCorrect.connect(self._correct); self.word.mistake.connect(self._mistake)
        self.sentence.sentenceCorrect.connect(self._correct); self.sentence.mistake.connect(self._mistake)
    @Property(str, notify=stateChanged)
    def mode(self): return self._mode
    @Property(str, notify=stateChanged)
    def challenge(self): return self._challenges[self._index] if self._challenges and self._index<len(self._challenges) else ''
    @Property(int, notify=stateChanged)
    def score(self): return self._score
    @Property(int, notify=stateChanged)
    def secondsLeft(self): return max(0,int(self._duration-(time.monotonic()-self._started))) if self._running else 0
    @Property(bool, notify=stateChanged)
    def running(self): return self._running
    def trainer(self): return self.letter if self._mode=='Letter' else self.word if self._mode=='Word' else self.sentence
    @Slot(str, str, str)
    def configureInput(self, input_type, left_type, right_type):
        self.letter.configureInput(input_type, left_type, right_type)
        self.word.configureInput(input_type, left_type, right_type)
        self.sentence.configureInput(input_type, left_type, right_type)

    @Slot(int,result=bool)
    def start(self,match_id):
        data=self.bridge.loadMatch(match_id)
        if not data:return False
        self._match_id=match_id; self._mode=data['mode']; self._challenges=list(data['challenges']); self._duration=int(data.get('duration_seconds',120)); self._index=0; self._score=0; self._started=time.monotonic(); self._running=True; self._start_current(); self.timer.start(); self.stateChanged.emit(); return True
    def _start_current(self):
        if not self._running or self._index>=len(self._challenges): return self._finish()
        value=self._challenges[self._index]
        if self._mode=='Letter': self.letter.startLetter(value)
        elif self._mode=='Word': self.word.startWord(value)
        else:self.sentence.startSentence(value)
        self.stateChanged.emit()
    @Slot(str)
    def buttonPressed(self,name): self.trainer().buttonPressed(name)
    @Slot(str)
    def buttonReleased(self,name): self.trainer().buttonReleased(name)
    def _correct(self,*args):
        if not self._running:return
        self._score+=1; self._index+=1; self._start_current()
    def _mistake(self,*args):
        if not self._running:return
        self._index+=1; self._start_current()
    def _tick(self):
        self.stateChanged.emit()
        if time.monotonic()-self._started>=self._duration:self._finish()
    def _finish(self):
        if not self._running:return
        elapsed=min(self._duration,time.monotonic()-self._started); self._running=False; self.timer.stop(); self.trainer().stop(); self.bridge.submitMatch(self._match_id,self._score,elapsed); self.stateChanged.emit(); self.finished.emit(self._score,elapsed)
