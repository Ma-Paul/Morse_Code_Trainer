from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PySide6.QtCore import QObject, Property, QStandardPaths, Signal, Slot

class OnlineBridge(QObject):
    playerIdChanged=Signal(); leaderboardChanged=Signal(); tournamentsChanged=Signal(); dailyChallengesChanged=Signal(); matchesChanged=Signal(); errorChanged=Signal()

    def __init__(self, base_url='http://127.0.0.1:8000', parent=None):
        super().__init__(parent); self._base_url=base_url.rstrip('/'); self._player_id=''; self._leaderboard=[]; self._tournaments=[]; self._daily=[]; self._matches=[]; self._error=''; self._load_identity()

    @Property(str, notify=playerIdChanged)
    def playerId(self): return self._player_id
    @Property('QVariantList', notify=leaderboardChanged)
    def leaderboard(self): return self._leaderboard
    @Property('QVariantList', notify=tournamentsChanged)
    def tournaments(self): return self._tournaments
    @Property('QVariantList', notify=dailyChallengesChanged)
    def dailyChallenges(self): return self._daily
    @Property('QVariantList', notify=matchesChanged)
    def matches(self): return self._matches
    @Property(str, notify=errorChanged)
    def error(self): return self._error

    def _identity_file(self):
        folder=Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)); folder.mkdir(parents=True,exist_ok=True); return folder/'online_identity.json'
    def _load_identity(self):
        try: self._player_id=str(json.loads(self._identity_file().read_text(encoding='utf-8')).get('player_id','')).strip()
        except Exception: self._player_id=''
    def _save_identity(self): self._identity_file().write_text(json.dumps({'player_id':self._player_id},indent=2),encoding='utf-8')
    def _set_error(self,value):
        value=str(value or '')
        if value!=self._error: self._error=value; self.errorChanged.emit()
    def _request(self,path,method='GET',payload=None):
        data=json.dumps(payload).encode() if payload is not None else None
        req=urllib.request.Request(self._base_url+path,data=data,headers={'Content-Type':'application/json'},method=method)
        try:
            with urllib.request.urlopen(req,timeout=5) as r:
                raw=r.read().decode(); return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            try: msg=json.loads(e.read().decode()).get('detail',str(e))
            except Exception: msg=str(e)
            raise RuntimeError(msg)
        except Exception as e: raise RuntimeError(f'Cannot reach server at {self._base_url}: {e}')

    @Slot(str,result=bool)
    def setPlayerId(self,value):
        value=str(value).strip()
        if not value: self._set_error('Please enter an ID.'); return False
        try: self._request('/api/player/register','POST',{'player_id':value})
        except Exception as e: self._set_error(e); return False
        self._player_id=value; self._save_identity(); self.playerIdChanged.emit(); self._set_error(''); self.refresh(); return True

    @Slot()
    def refresh(self):
        try:
            self._leaderboard=self._request('/api/leaderboard'); self._tournaments=self._request('/api/tournaments')
            self._daily=self._request('/api/daily/player/'+urllib.parse.quote(self._player_id)) if self._player_id else self._request('/api/daily')
            self._matches=self._request('/api/player/'+urllib.parse.quote(self._player_id)+'/matches') if self._player_id else []
            self.leaderboardChanged.emit(); self.tournamentsChanged.emit(); self.dailyChallengesChanged.emit(); self.matchesChanged.emit(); self._set_error('')
        except Exception as e: self._set_error(e)

    @Slot(int)
    def joinTournament(self,tid):
        try: self._request(f'/api/tournaments/{int(tid)}/join','POST',{'player_id':self._player_id}); self.refresh()
        except Exception as e: self._set_error(e)
    @Slot(str)
    def joinWithCode(self,code):
        try: self._request('/api/tournaments/join-code','POST',{'player_id':self._player_id,'invite_code':str(code).strip()}); self.refresh()
        except Exception as e: self._set_error(e)
    @Slot(int)
    def completeDaily(self,cid):
        try: self._request('/api/daily/complete','POST',{'player_id':self._player_id,'challenge_id':int(cid)}); self.refresh()
        except Exception as e: self._set_error(e)
    @Slot(int,result='QVariantMap')
    def loadMatch(self,mid):
        try:
            query=urllib.parse.urlencode({'player_id':self._player_id}); return self._request(f'/api/matches/{int(mid)}/play?{query}')
        except Exception as e: self._set_error(e); return {}
    @Slot(int,int,float)
    def submitMatch(self,mid,score,total_time):
        try: self._request(f'/api/matches/{int(mid)}/submit','POST',{'player_id':self._player_id,'score':int(score),'completion_time':float(total_time)}); self.refresh()
        except Exception as e: self._set_error(e)
