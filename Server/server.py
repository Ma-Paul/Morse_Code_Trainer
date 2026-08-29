from __future__ import annotations

import json
import random
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

DB_PATH = Path(__file__).resolve().parent / "morse_server.sqlite3"
MATCH_DURATION_SECONDS = 120
MATCH_START_SPACING_SECONDS = 120

LETTER_POOL = list("abcdefghijklmnopqrstuvwxyz")
WORD_POOL = [
    "morse", "radio", "signal", "train", "apple", "house", "light", "sound",
    "quick", "green", "table", "water", "world", "code", "learn", "button",
]
SENTENCE_POOL = [
    "the radio is ready", "practice makes progress", "send the code",
    "keep the rhythm", "read the signal", "we learn morse", "a clear signal",
    "the quick fox", "morse is fun", "learn every day",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


@contextmanager
def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with db() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            daily_points INTEGER NOT NULL DEFAULT 0,
            tournament_place INTEGER,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenge_key TEXT NOT NULL UNIQUE,
            mode TEXT NOT NULL,
            challenge_text TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_completions (
            challenge_id INTEGER NOT NULL,
            player_id TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            PRIMARY KEY(challenge_id, player_id),
            FOREIGN KEY(challenge_id) REFERENCES daily_challenges(id),
            FOREIGN KEY(player_id) REFERENCES players(id)
        );

        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            visibility TEXT NOT NULL,
            invite_code TEXT,
            recurrence TEXT NOT NULL,
            mode TEXT NOT NULL,
            starts_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'scheduled',
            created_at TEXT NOT NULL,
            parent_tournament_id INTEGER
        );

        CREATE TABLE IF NOT EXISTS tournament_players (
            tournament_id INTEGER NOT NULL,
            player_id TEXT NOT NULL,
            joined_at TEXT NOT NULL,
            PRIMARY KEY(tournament_id, player_id),
            FOREIGN KEY(tournament_id) REFERENCES tournaments(id),
            FOREIGN KEY(player_id) REFERENCES players(id)
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            player1_id TEXT NOT NULL,
            player2_id TEXT NOT NULL,
            scheduled_at TEXT NOT NULL,
            duration_seconds INTEGER NOT NULL DEFAULT 120,
            status TEXT NOT NULL DEFAULT 'scheduled',
            challenge_seed INTEGER NOT NULL,
            challenges_json TEXT NOT NULL,
            player1_score INTEGER NOT NULL DEFAULT 0,
            player2_score INTEGER NOT NULL DEFAULT 0,
            player1_time REAL NOT NULL DEFAULT 0,
            player2_time REAL NOT NULL DEFAULT 0,
            player1_submitted INTEGER NOT NULL DEFAULT 0,
            player2_submitted INTEGER NOT NULL DEFAULT 0,
            winner_id TEXT,
            FOREIGN KEY(tournament_id) REFERENCES tournaments(id),
            FOREIGN KEY(player1_id) REFERENCES players(id),
            FOREIGN KEY(player2_id) REFERENCES players(id)
        );
        ''')


def normalize_player_id(value: str) -> str:
    value = value.strip()
    if not value:
        raise HTTPException(400, "Player ID cannot be empty")
    if len(value) > 32:
        raise HTTPException(400, "Player ID is too long")
    return value


def ensure_daily_challenges() -> None:
    today = utc_now().date().isoformat()
    randomizer = random.Random(today)
    defaults = [
        ("Letter", randomizer.choice(LETTER_POOL)),
        ("Word", randomizer.choice(WORD_POOL)),
        ("Sentence", randomizer.choice(SENTENCE_POOL)),
    ]
    with db() as con:
        con.execute("UPDATE daily_challenges SET active = 0")
        for mode, challenge in defaults:
            key = f"{today}:{mode}"
            con.execute(
                '''INSERT OR IGNORE INTO daily_challenges
                   (challenge_key, mode, challenge_text, active, created_at)
                   VALUES (?, ?, ?, 1, ?)''',
                (key, mode, challenge, iso(utc_now())),
            )
            con.execute(
                "UPDATE daily_challenges SET active = 1 WHERE challenge_key = ?",
                (key,),
            )


def recurrence_delta(value: str) -> Optional[timedelta]:
    return {
        "daily": timedelta(days=1),
        "weekly": timedelta(days=7),
        "biweekly": timedelta(days=14),
        "monthly": timedelta(days=30),
    }.get(value)


def create_next_occurrence_if_needed(con, tournament) -> None:
    delta = recurrence_delta(tournament["recurrence"])
    if delta is None:
        return
    existing = con.execute(
        "SELECT id FROM tournaments WHERE parent_tournament_id = ?",
        (tournament["id"],),
    ).fetchone()
    if existing:
        return
    next_start = datetime.fromisoformat(tournament["starts_at"]) + delta
    invite_code = secrets.token_hex(3).upper() if tournament["visibility"] == "invite" else None
    cur = con.execute(
        '''INSERT INTO tournaments
           (name, visibility, invite_code, recurrence, mode, starts_at, status,
            created_at, parent_tournament_id)
           VALUES (?, ?, ?, ?, ?, ?, 'scheduled', ?, ?)''',
        (
            tournament["name"], tournament["visibility"], invite_code,
            tournament["recurrence"], tournament["mode"], iso(next_start),
            iso(utc_now()), tournament["id"],
        ),
    )
    new_id = cur.lastrowid
    old_players = con.execute(
        "SELECT player_id FROM tournament_players WHERE tournament_id = ?",
        (tournament["id"],),
    ).fetchall()
    for row in old_players:
        con.execute(
            '''INSERT OR IGNORE INTO tournament_players
               (tournament_id, player_id, joined_at) VALUES (?, ?, ?)''',
            (new_id, row["player_id"], iso(utc_now())),
        )


def challenge_sequence(mode: str, seed: int, count: int = 200) -> list[str]:
    rng = random.Random(seed)
    pool = {
        "Letter": LETTER_POOL,
        "Word": WORD_POOL,
        "Sentence": SENTENCE_POOL,
    }[mode]
    return [rng.choice(pool) for _ in range(count)]


def generate_round_robin(con, tournament_id: int) -> None:
    if con.execute("SELECT 1 FROM matches WHERE tournament_id = ? LIMIT 1", (tournament_id,)).fetchone():
        return
    tournament = con.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,)).fetchone()
    if not tournament:
        raise HTTPException(404, "Tournament not found")
    players = [r["player_id"] for r in con.execute(
        "SELECT player_id FROM tournament_players WHERE tournament_id = ? ORDER BY joined_at, player_id",
        (tournament_id,),
    )]
    if len(players) < 2:
        raise HTTPException(400, "At least two players are required")
    start = datetime.fromisoformat(tournament["starts_at"])
    match_index = 0
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            scheduled = start + timedelta(seconds=match_index * MATCH_START_SPACING_SECONDS)
            seed = secrets.randbits(31)
            challenges = challenge_sequence(tournament["mode"], seed)
            con.execute(
                '''INSERT INTO matches
                   (tournament_id, player1_id, player2_id, scheduled_at,
                    duration_seconds, challenge_seed, challenges_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (
                    tournament_id, players[i], players[j], iso(scheduled),
                    MATCH_DURATION_SECONDS, seed, json.dumps(challenges),
                ),
            )
            match_index += 1


def calculate_standings(con, tournament_id: int) -> list[dict]:
    standings = {
        row["id"]: {
            "player_id": row["id"], "display_name": row["display_name"],
            "tournament_points": 0, "wins": 0, "draws": 0, "losses": 0,
            "correct": 0, "total_time": 0.0,
        }
        for row in con.execute(
            '''SELECT p.id, p.display_name FROM tournament_players tp
               JOIN players p ON p.id = tp.player_id
               WHERE tp.tournament_id = ?''', (tournament_id,)
        )
    }
    for m in con.execute(
        "SELECT * FROM matches WHERE tournament_id = ? AND status = 'finished'",
        (tournament_id,),
    ):
        a = standings[m["player1_id"]]
        b = standings[m["player2_id"]]
        a["correct"] += m["player1_score"]
        b["correct"] += m["player2_score"]
        a["total_time"] += m["player1_time"]
        b["total_time"] += m["player2_time"]
        if m["winner_id"] is None:
            a["draws"] += 1; b["draws"] += 1
            a["tournament_points"] += 1; b["tournament_points"] += 1
        elif m["winner_id"] == a["player_id"]:
            a["wins"] += 1; b["losses"] += 1; a["tournament_points"] += 3
        else:
            b["wins"] += 1; a["losses"] += 1; b["tournament_points"] += 3
    values = list(standings.values())
    values.sort(key=lambda x: (-x["tournament_points"], -x["wins"], -x["correct"], x["total_time"], x["display_name"].lower()))
    for place, row in enumerate(values, 1):
        row["place"] = place
    return values


def finalize_tournament_if_done(con, tournament_id: int) -> None:
    tournament = con.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,)).fetchone()
    if not tournament:
        return
    counts = con.execute(
        '''SELECT COUNT(*) total,
                  SUM(CASE WHEN status='finished' THEN 1 ELSE 0 END) finished
           FROM matches WHERE tournament_id = ?''',
        (tournament_id,),
    ).fetchone()
    if not counts["total"] or counts["total"] != counts["finished"]:
        return
    con.execute("UPDATE tournaments SET status='finished' WHERE id = ?", (tournament_id,))
    if tournament["visibility"] == "open":
        con.execute("UPDATE players SET tournament_place = NULL")
        for place, row in enumerate(calculate_standings(con, tournament_id)[:3], 1):
            con.execute("UPDATE players SET tournament_place = ? WHERE id = ?", (place, row["player_id"]))
    create_next_occurrence_if_needed(con, tournament)


def tournament_payload(con, tournament_id: int) -> dict:
    tournament = con.execute("SELECT * FROM tournaments WHERE id = ?", (tournament_id,)).fetchone()
    if not tournament:
        raise HTTPException(404, "Tournament not found")
    payload = dict(tournament)
    payload["players"] = [dict(r) for r in con.execute(
        '''SELECT p.id, p.display_name, p.tournament_place FROM tournament_players tp
           JOIN players p ON p.id = tp.player_id WHERE tp.tournament_id = ?
           ORDER BY p.display_name COLLATE NOCASE''', (tournament_id,)
    )]
    payload["matches"] = [dict(r) for r in con.execute(
        '''SELECT m.id, m.tournament_id, m.player1_id, m.player2_id, m.scheduled_at,
                  m.duration_seconds, m.status, m.player1_score, m.player2_score,
                  m.player1_time, m.player2_time, m.winner_id,
                  p1.display_name player1_name, p2.display_name player2_name,
                  pw.display_name winner_name
           FROM matches m JOIN players p1 ON p1.id=m.player1_id
           JOIN players p2 ON p2.id=m.player2_id
           LEFT JOIN players pw ON pw.id=m.winner_id
           WHERE m.tournament_id=? ORDER BY m.scheduled_at''', (tournament_id,)
    )]
    payload["standings"] = calculate_standings(con, tournament_id)
    return payload


class PlayerRequest(BaseModel):
    player_id: str = Field(min_length=1, max_length=32)

class TournamentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    visibility: str
    recurrence: str = "once"
    mode: str
    starts_at: Optional[str] = None

class JoinTournament(BaseModel):
    player_id: str

class JoinCode(BaseModel):
    player_id: str
    invite_code: str

class DailyComplete(BaseModel):
    player_id: str
    challenge_id: int

class MatchSubmit(BaseModel):
    player_id: str
    score: int = Field(ge=0)
    completion_time: float = Field(ge=0)


app = FastAPI(title="Morse Code Tournament Server")

@app.on_event("startup")
def startup():
    init_db(); ensure_daily_challenges()

@app.get("/api/health")
def health():
    return {"ok": True, "server_time": iso(utc_now())}

@app.post("/api/player/register")
def register_player(req: PlayerRequest):
    player_id = normalize_player_id(req.player_id)
    with db() as con:
        con.execute(
            '''INSERT INTO players(id, display_name, updated_at) VALUES(?,?,?)
               ON CONFLICT(id) DO UPDATE SET display_name=excluded.display_name,
               updated_at=excluded.updated_at''',
            (player_id, player_id, iso(utc_now())),
        )
        return dict(con.execute("SELECT * FROM players WHERE id=?", (player_id,)).fetchone())

@app.get("/api/leaderboard")
def leaderboard():
    with db() as con:
        return [dict(r) for r in con.execute(
            '''SELECT id, display_name, daily_points, tournament_place FROM players
               ORDER BY daily_points DESC, display_name COLLATE NOCASE LIMIT 100'''
        )]

@app.get("/api/daily")
def daily():
    ensure_daily_challenges()
    with db() as con:
        return [dict(r) for r in con.execute(
            "SELECT id, mode, challenge_text FROM daily_challenges WHERE active=1 ORDER BY id"
        )]

@app.get("/api/daily/player/{player_id}")
def daily_for_player(player_id: str):
    ensure_daily_challenges()
    with db() as con:
        return [dict(r) for r in con.execute(
            '''SELECT d.id, d.mode, d.challenge_text,
                      CASE WHEN c.player_id IS NULL THEN 0 ELSE 1 END completed
               FROM daily_challenges d LEFT JOIN daily_completions c
                 ON c.challenge_id=d.id AND c.player_id=?
               WHERE d.active=1 ORDER BY d.id''', (player_id,)
        )]

@app.post("/api/daily/complete")
def complete_daily(req: DailyComplete):
    with db() as con:
        if not con.execute("SELECT 1 FROM players WHERE id=?", (req.player_id,)).fetchone():
            raise HTTPException(404, "Player not registered")
        if not con.execute("SELECT 1 FROM daily_challenges WHERE id=? AND active=1", (req.challenge_id,)).fetchone():
            raise HTTPException(404, "Challenge not found")
        try:
            con.execute(
                "INSERT INTO daily_completions(challenge_id, player_id, completed_at) VALUES(?,?,?)",
                (req.challenge_id, req.player_id, iso(utc_now())),
            )
        except sqlite3.IntegrityError:
            return {"awarded": False}
        con.execute("UPDATE players SET daily_points=daily_points+1 WHERE id=?", (req.player_id,))
        return {"awarded": True}

@app.post("/api/admin/reset-leaderboard")
def reset_leaderboard():
    with db() as con:
        con.execute("DELETE FROM daily_completions")
        con.execute("UPDATE players SET daily_points=0")
    return {"ok": True}

@app.post("/api/tournaments")
def create_tournament(req: TournamentCreate):
    if req.visibility not in {"open", "invite"}:
        raise HTTPException(400, "visibility must be open or invite")
    if req.mode not in {"Letter", "Word", "Sentence"}:
        raise HTTPException(400, "invalid mode")
    if req.recurrence not in {"once", "daily", "weekly", "biweekly", "monthly"}:
        raise HTTPException(400, "invalid recurrence")
    starts = datetime.fromisoformat(req.starts_at) if req.starts_at else utc_now()+timedelta(minutes=5)
    code = secrets.token_hex(3).upper() if req.visibility == "invite" else None
    with db() as con:
        cur = con.execute(
            '''INSERT INTO tournaments(name, visibility, invite_code, recurrence, mode,
               starts_at, status, created_at) VALUES(?,?,?,?,?,?,'scheduled',?)''',
            (req.name.strip(), req.visibility, code, req.recurrence, req.mode, iso(starts), iso(utc_now())),
        )
        return tournament_payload(con, cur.lastrowid)

@app.get("/api/tournaments")
def list_tournaments():
    with db() as con:
        return [dict(r) for r in con.execute(
            '''SELECT * FROM tournaments ORDER BY
               CASE status WHEN 'running' THEN 0 WHEN 'scheduled' THEN 1 ELSE 2 END,
               starts_at DESC'''
        )]

@app.get("/api/tournaments/{tournament_id}")
def get_tournament(tournament_id: int):
    with db() as con:
        return tournament_payload(con, tournament_id)

@app.post("/api/tournaments/{tournament_id}/join")
def join_open(tournament_id: int, req: JoinTournament):
    with db() as con:
        tournament = con.execute("SELECT * FROM tournaments WHERE id=?", (tournament_id,)).fetchone()
        if not tournament: raise HTTPException(404, "Tournament not found")
        if tournament["visibility"] != "open": raise HTTPException(403, "Invite code required")
        if tournament["status"] != "scheduled": raise HTTPException(409, "Tournament registration is closed")
        if not con.execute("SELECT 1 FROM players WHERE id=?", (req.player_id,)).fetchone(): raise HTTPException(404, "Player not registered")
        con.execute("INSERT OR IGNORE INTO tournament_players(tournament_id,player_id,joined_at) VALUES(?,?,?)", (tournament_id, req.player_id, iso(utc_now())))
        return tournament_payload(con, tournament_id)

@app.post("/api/tournaments/join-code")
def join_code(req: JoinCode):
    with db() as con:
        tournament = con.execute("SELECT * FROM tournaments WHERE invite_code=?", (req.invite_code.strip().upper(),)).fetchone()
        if not tournament: raise HTTPException(404, "Invalid invite code")
        if tournament["status"] != "scheduled": raise HTTPException(409, "Tournament registration is closed")
        if not con.execute("SELECT 1 FROM players WHERE id=?", (req.player_id,)).fetchone(): raise HTTPException(404, "Player not registered")
        con.execute("INSERT OR IGNORE INTO tournament_players(tournament_id,player_id,joined_at) VALUES(?,?,?)", (tournament["id"], req.player_id, iso(utc_now())))
        return tournament_payload(con, tournament["id"])

@app.post("/api/tournaments/{tournament_id}/start")
def start_tournament(tournament_id: int):
    with db() as con:
        generate_round_robin(con, tournament_id)
        con.execute("UPDATE tournaments SET status='running' WHERE id=?", (tournament_id,))
        return tournament_payload(con, tournament_id)

@app.get("/api/player/{player_id}/matches")
def player_matches(player_id: str):
    with db() as con:
        return [dict(r) for r in con.execute(
            '''SELECT m.id, m.tournament_id, m.scheduled_at, m.duration_seconds, m.status,
                      t.name tournament_name, t.mode,
                      CASE WHEN m.player1_id=? THEN p2.display_name ELSE p1.display_name END opponent
               FROM matches m JOIN tournaments t ON t.id=m.tournament_id
               JOIN players p1 ON p1.id=m.player1_id JOIN players p2 ON p2.id=m.player2_id
               WHERE m.player1_id=? OR m.player2_id=? ORDER BY m.scheduled_at''',
            (player_id, player_id, player_id),
        )]

@app.get("/api/matches/{match_id}/play")
def play_match(match_id: int, player_id: str):
    with db() as con:
        m = con.execute(
            '''SELECT m.*, t.mode, t.name tournament_name FROM matches m
               JOIN tournaments t ON t.id=m.tournament_id WHERE m.id=?''', (match_id,)
        ).fetchone()
        if not m: raise HTTPException(404, "Match not found")
        if player_id not in {m["player1_id"], m["player2_id"]}: raise HTTPException(403, "Not your match")
        scheduled = datetime.fromisoformat(m["scheduled_at"])
        if utc_now() < scheduled:
            raise HTTPException(409, f"Match starts at {m['scheduled_at']}")
        if m["status"] == "finished":
            raise HTTPException(409, "Match is already finished")
        con.execute("UPDATE matches SET status='running' WHERE id=?", (match_id,))
        return {
            "match_id": m["id"], "mode": m["mode"], "tournament_name": m["tournament_name"],
            "duration_seconds": m["duration_seconds"], "scheduled_at": m["scheduled_at"],
            "challenges": json.loads(m["challenges_json"]),
        }

@app.post("/api/matches/{match_id}/submit")
def submit_match(match_id: int, req: MatchSubmit):
    with db() as con:
        m = con.execute("SELECT * FROM matches WHERE id=?", (match_id,)).fetchone()
        if not m: raise HTTPException(404, "Match not found")
        if req.player_id == m["player1_id"]:
            con.execute("UPDATE matches SET player1_score=?, player1_time=?, player1_submitted=1 WHERE id=?", (req.score, req.completion_time, match_id))
        elif req.player_id == m["player2_id"]:
            con.execute("UPDATE matches SET player2_score=?, player2_time=?, player2_submitted=1 WHERE id=?", (req.score, req.completion_time, match_id))
        else: raise HTTPException(403, "Player is not in this match")
        m = con.execute("SELECT * FROM matches WHERE id=?", (match_id,)).fetchone()
        if m["player1_submitted"] and m["player2_submitted"]:
            winner = None
            if m["player1_score"] > m["player2_score"]: winner = m["player1_id"]
            elif m["player2_score"] > m["player1_score"]: winner = m["player2_id"]
            elif m["player1_time"] < m["player2_time"]: winner = m["player1_id"]
            elif m["player2_time"] < m["player1_time"]: winner = m["player2_id"]
            con.execute("UPDATE matches SET status='finished', winner_id=? WHERE id=?", (winner, match_id))
            finalize_tournament_if_done(con, m["tournament_id"])
        return dict(con.execute("SELECT * FROM matches WHERE id=?", (match_id,)).fetchone())


def run_server(host="0.0.0.0", port=8000):
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    init_db(); ensure_daily_challenges(); run_server()
