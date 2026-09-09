import time
import csv
from datetime import datetime
from mcstatus import JavaServer
# enter your desired server ip
# in the interval, that 15 is 15 seconds, make it shorter or longer if you want
SERVER = ""
INTERVAL = 15
EMPTY_LIMIT = 5
LOG_FILE = "minecraft_player_log.csv"

previous_players = set()
first_check = True
empty_checks = 0


def log_event(timestamp, event, player, players):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            event,
            player,
            ", ".join(sorted(players))
        ])


try:
    with open(LOG_FILE, "x", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Timestamp",
            "Event",
            "Player",
            "Players Online"
        ])
except FileExistsError:
    pass


print("=" * 60)
print(" Minecraft Server Player Watcher")
print("=" * 60)
print(f"Server: {SERVER}")
print(f"Checking every {INTERVAL} seconds")
print(f"Resetting after {EMPTY_LIMIT} consecutive empty checks")
print(f"Log file: {LOG_FILE}")
print("Press Ctrl+C to stop.")
print("=" * 60)


while True:
    try:
        server = JavaServer.lookup(SERVER)
        status = server.status()

        players = set()

        if status.players.sample:
            players = {
                player.name
                for player in status.players.sample
                if player.name
            }

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Empty player sample
        if not players:
            empty_checks += 1

            print(
                f"[{now}] Online: {status.players.online} | "
                f"Names detected: Nobody | "
                f"Empty check {empty_checks}/{EMPTY_LIMIT}"
            )

            # Reset after 5 consecutive empty samples
            if empty_checks >= EMPTY_LIMIT:
                print(f"[{now}] Five consecutive empty checks — resetting tracking.")

                log_event(
                    now,
                    "RESET",
                    "",
                    []
                )

                previous_players = set()
                first_check = True
                empty_checks = 0

            time.sleep(INTERVAL)
            continue

        # We found player names again
        empty_checks = 0

        if first_check:
            print(
                f"[{now}] Initial player list: "
                f"{', '.join(sorted(players))}"
            )

            log_event(now, "INITIAL", "", players)
            first_check = False

        else:
            joined = players - previous_players
            left = previous_players - players

            for player in sorted(joined):
                print(f"[{now}] JOIN  {player}")
                log_event(now, "JOIN", player, players)

            for player in sorted(left):
                print(f"[{now}] LEAVE {player}")
                log_event(now, "LEAVE", player, players)

        print(
            f"[{now}] Online ({status.players.online}): "
            f"{', '.join(sorted(players))}"
        )

        previous_players = players

    except Exception as e:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] Server unavailable/error: {e}")

    time.sleep(INTERVAL)
