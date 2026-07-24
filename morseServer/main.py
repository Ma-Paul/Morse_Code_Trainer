from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

from datetime import datetime, timedelta, timezone

import random

import uuid

from threading import Lock

app = FastAPI()

lock = Lock()

WORDS = ["Haus", "Baum", "Auto", "Lampe", "Computer"]

SENTENCES = [
    "Das Programm startet gleich.",
    "Der Client wartet auf das Signal.",
    "Heute ist ein guter Tag.",
    "Der Server sendet die Startzeit.",
    "Das System ist bereit.",
]

players = {}

current_round = None


class JoinRequest(BaseModel):

    name: str


class TaskRequest(BaseModel):

    player_id: str

    modus: str


class ResultRequest(BaseModel):

    player_id: str

    round_id: str

    status: str

    time_seconds: float | None = None


@app.get("/")
def root():

    return {"status": "online"}


@app.post("/join")
def join_game(data: JoinRequest):

    player_id = str(uuid.uuid4())

    with lock:

        players[player_id] = {"id": player_id, "name": data.name}

    return {"player_id": player_id, "name": data.name}


@app.post("/request")
def request_task(data: TaskRequest):

    global current_round

    modus = data.modus.strip().lower()

    if modus not in ["wort", "satz"]:

        raise HTTPException(
            status_code=400, detail="Modus muss 'Wort' oder 'Satz' sein"
        )

    with lock:

        if data.player_id not in players:

            raise HTTPException(status_code=404, detail="Spieler nicht angemeldet")

        if current_round is None or current_round["finished"]:

            if modus == "wort":

                content = random.choice(WORDS)

                response_modus = "Wort"

            else:

                content = random.choice(SENTENCES)

                response_modus = "Satz"

            round_id = str(uuid.uuid4())

            start_time = datetime.now(timezone.utc) + timedelta(seconds=2)

            expected_players = list(players.keys())

            current_round = {
                "round_id": round_id,
                "modus": response_modus,
                "content": content,
                "start_time": start_time,
                "expected_players": expected_players,
                "results": {},
                "finished": False,
                "winner": None,
            }

        return {
            "data": {
                "round_id": current_round["round_id"],
                "modus": current_round["modus"],
                "zeit": current_round["start_time"].isoformat(),
                "inhalt": current_round["content"],
                "spieler_anzahl": len(current_round["expected_players"]),
            }
        }


@app.post("/result")
def submit_result(data: ResultRequest):

    global current_round

    with lock:

        if current_round is None:

            raise HTTPException(status_code=400, detail="Keine aktive Runde")

        if data.round_id != current_round["round_id"]:

            raise HTTPException(status_code=400, detail="Falsche Runde")

        if data.player_id not in current_round["expected_players"]:

            raise HTTPException(
                status_code=400, detail="Spieler gehört nicht zu dieser Runde"
            )

        if data.status not in ["correct", "wrong", "timeout"]:

            raise HTTPException(
                status_code=400, detail="Status muss correct, wrong oder timeout sein"
            )

        current_round["results"][data.player_id] = {
            "player_id": data.player_id,
            "name": players[data.player_id]["name"],
            "status": data.status,
            "time_seconds": data.time_seconds,
        }

        if len(current_round["results"]) >= len(current_round["expected_players"]):

            correct_results = [
                result
                for result in current_round["results"].values()
                if result["status"] == "correct" and result["time_seconds"] is not None
            ]

            if correct_results:

                winner = min(correct_results, key=lambda x: x["time_seconds"])

                current_round["winner"] = winner

            else:

                current_round["winner"] = None

            current_round["finished"] = True

        return {"status": "received", "round_finished": current_round["finished"]}


@app.get("/winner/{round_id}")
def get_winner(round_id: str):

    with lock:

        if current_round is None:

            raise HTTPException(status_code=404, detail="Keine Runde vorhanden")

        if round_id != current_round["round_id"]:

            raise HTTPException(status_code=404, detail="Runde nicht gefunden")

        if not current_round["finished"]:

            return {
                "finished": False,
                "message": "Warte noch auf Spieler",
                "received_results": len(current_round["results"]),
                "expected_results": len(current_round["expected_players"]),
            }

        return {
            "finished": True,
            "winner": current_round["winner"],
            "results": list(current_round["results"].values()),
        }


@app.post("/reset")
def reset_game():

    global current_round

    with lock:

        current_round = None

    return {"status": "reset"}
