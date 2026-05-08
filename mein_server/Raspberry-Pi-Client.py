import requests
import time
import sys
import select
import socket
from datetime import datetime, timezone

SERVER_URL = "http://127.0.0.1:8000"
MODUS = "Wort"

MAX_INPUT_TIME = 10.0


def input_with_timeout(prompt, timeout):
    print(prompt, end="", flush=True)

    ready, _, _ = select.select([sys.stdin], [], [], timeout)

    if ready:
        return sys.stdin.readline().rstrip("\n")

    return None


def parse_server_time(value):
    return datetime.fromisoformat(value)


def wait_until(start_time):
    now = datetime.now(timezone.utc)
    wait_seconds = (start_time - now).total_seconds()

    if wait_seconds > 0:
        print(f"Start in {wait_seconds:.2f} Sekunden...")
        time.sleep(wait_seconds)


def join_game():
    player_name = socket.gethostname()

    response = requests.post(
        f"{SERVER_URL}/join", json={"name": player_name}, timeout=10
    )

    response.raise_for_status()
    return response.json()


def request_task(player_id):
    response = requests.post(
        f"{SERVER_URL}/request",
        json={"player_id": player_id, "modus": MODUS},
        timeout=10,
    )

    response.raise_for_status()
    return response.json()["data"]


def send_result(player_id, round_id, status, time_seconds=None):
    response = requests.post(
        f"{SERVER_URL}/result",
        json={
            "player_id": player_id,
            "round_id": round_id,
            "status": status,
            "time_seconds": time_seconds,
        },
        timeout=10,
    )

    response.raise_for_status()
    return response.json()


def wait_for_winner(round_id):
    while True:
        response = requests.get(f"{SERVER_URL}/winner/{round_id}", timeout=10)

        response.raise_for_status()
        data = response.json()

        if data["finished"]:
            return data

        print(
            f"Warte auf Ergebnisse: "
            f"{data['received_results']}/{data['expected_results']}"
        )

        time.sleep(1)


def main():
    print("Verbinde mit Server...")

    join_data = join_game()
    player_id = join_data["player_id"]

    print("Angemeldet als:", join_data["name"])
    print("Player ID:", player_id)

    task = request_task(player_id)

    round_id = task["round_id"]
    modus = task["modus"]
    start_time = parse_server_time(task["zeit"])
    content = task["inhalt"]
    player_count = task["spieler_anzahl"]

    print()
    print("Runde:", round_id)
    print("Modus:", modus)
    print("Spieleranzahl:", player_count)
    print("Startzeit:", start_time.isoformat())
    print()

    wait_until(start_time)

    print()
    print("JETZT!")
    print("Eingabe:", content)
    print()

    typing_start = time.perf_counter()

    user_input = input_with_timeout("Tippe jetzt und drücke Enter: ", MAX_INPUT_TIME)

    typing_end = time.perf_counter()
    elapsed = typing_end - typing_start

    if user_input is None:
        print()
        print("Zu langsam. Timeout.")
        send_result(player_id, round_id, "timeout", None)

    elif elapsed > MAX_INPUT_TIME:
        print("Zu langsam.")
        send_result(player_id, round_id, "timeout", None)

    elif user_input == content:
        print(f"Richtig. Zeit: {elapsed:.3f} Sekunden")
        send_result(player_id, round_id, "correct", elapsed)

    else:
        print("Falsch.")
        print("Erwartet:", content)
        print("Eingegeben:", user_input)
        send_result(player_id, round_id, "wrong", None)

    print()
    print("Warte auf Gewinner...")

    result = wait_for_winner(round_id)

    print()
    print("ERGEBNIS")

    winner = result["winner"]

    if winner is None:
        print("Kein Gewinner. Niemand war richtig.")
    else:
        print(
            f"Gewinner: {winner['name']} " f"mit {winner['time_seconds']:.3f} Sekunden"
        )

    print()
    print("Alle Ergebnisse:")

    for item in result["results"]:
        name = item["name"]
        status = item["status"]
        time_seconds = item["time_seconds"]

        if time_seconds is None:
            print(f"- {name}: {status}")
        else:
            print(f"- {name}: {status}, {time_seconds:.3f} Sekunden")


if __name__ == "__main__":
    main()
