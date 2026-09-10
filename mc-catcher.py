import time
import csv
from datetime import datetime
from mcstatus import JavaServer
# enter your desired server ip
# in the interval, that 15 is 15 seconds, make it shorter or longer if you want
# you can rename the log file, but keep it .csv
SERVER = ""
INTERVAL = 15
EMPTY_LIMIT = 5
LOG_FILE = "where/you/want/it/to/go/minecraft_player_log.csv"

previous_players = set()
first_check = True
empty_checks = 0
server_was_online = False


def log_line(timestamp, status, online, names, details):
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            timestamp,
            status,
            online,
            ", ".join(sorted(names)),
            details
        ])
        f.flush()


# Create log file if it doesn't exist
try:
    with open(LOG_FILE, "x", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Timestamp",
            "Status",
            "Players Online",
            "Names Detected",
            "Details"
        ])
        f.flush()
except FileExistsError:
    pass


print("=" * 60)
print(" Minecraft Server Player Watcher")
print("=" * 60)
print(f"Server: {SERVER}")
print(f"Checking every {INTERVAL} seconds")
print(f"Log file: {LOG_FILE}")
print("The watcher will keep running even when the server is offline.")
print("Press Ctrl+C to stop.")
print("=" * 60)


while True:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Create a fresh server connection every check.
        # This is important for Aternos because the server can disappear
        # and come back later.
        server = JavaServer.lookup(SERVER)

        status = server.status()

        online = status.players.online

        players = set()

        if status.players.sample:
            players = {
                player.name
                for player in status.players.sample
                if player.name
            }

        # ---------------------------------------------------------
        # SERVER IS ONLINE
        # ---------------------------------------------------------

        if not server_was_online:
            print(f"[{now}] 🟢 SERVER ONLINE")

            log_line(
                now,
                "SERVER ONLINE",
                online,
                players,
                "Server became reachable"
            )

            server_was_online = True
            previous_players = set()
            first_check = True
            empty_checks = 0

        # ---------------------------------------------------------
        # SERVER ONLINE, ZERO PLAYERS
        # ---------------------------------------------------------

        if online == 0:
            empty_checks += 1

            message = (
                f"[{now}] Online: 0 | "
                f"Names detected: Nobody | "
                f"Empty check {empty_checks}/{EMPTY_LIMIT}"
            )

            print(message)

            log_line(
                now,
                "ONLINE",
                0,
                [],
                f"Nobody online | Empty check "
                f"{empty_checks}/{EMPTY_LIMIT}"
            )

            if empty_checks >= EMPTY_LIMIT:
                previous_players = set()
                first_check = True
                empty_checks = 0

            time.sleep(INTERVAL)
            continue

        # ---------------------------------------------------------
        # SERVER ONLINE, BUT PLAYER NAMES UNAVAILABLE
        # ---------------------------------------------------------

        empty_checks = 0

        if not players:
            message = (
                f"[{now}] Online: {online} | "
                f"Names detected: Names unavailable"
            )

            print(message)

            log_line(
                now,
                "ONLINE",
                online,
                [],
                "Player names unavailable"
            )

            time.sleep(INTERVAL)
            continue

        # ---------------------------------------------------------
        # FIRST PLAYER LIST AFTER SERVER COMES ONLINE
        # ---------------------------------------------------------

        if first_check:
            message = (
                f"[{now}] Initial player list: "
                f"{', '.join(sorted(players))}"
            )

            print(message)

            log_line(
                now,
                "INITIAL",
                online,
                players,
                "Initial player list"
            )

            first_check = False

        # ---------------------------------------------------------
        # JOIN / LEAVE DETECTION
        # ---------------------------------------------------------

        else:
            joined = players - previous_players
            left = previous_players - players

            for player in sorted(joined):
                message = f"[{now}] JOIN  {player}"
                print(message)

                log_line(
                    now,
                    "JOIN",
                    online,
                    players,
                    player
                )

            for player in sorted(left):
                message = f"[{now}] LEAVE {player}"
                print(message)

                log_line(
                    now,
                    "LEAVE",
                    online,
                    players,
                    player
                )

        # ---------------------------------------------------------
        # NORMAL STATUS
        # ---------------------------------------------------------

        names_text = ", ".join(sorted(players))

        message = (
            f"[{now}] Online ({online}): {names_text}"
        )

        print(message)

        log_line(
            now,
            "ONLINE",
            online,
            players,
            ""
        )

        previous_players = players

    # -------------------------------------------------------------
    # SERVER OFFLINE / UNREACHABLE
    # -------------------------------------------------------------

    except Exception as e:

        if server_was_online:
            print(f"[{now}] 🔴 SERVER OFFLINE")

            log_line(
                now,
                "SERVER OFFLINE",
                "",
                [],
                str(e)
            )

            # Clear the old player list so that when the server
            # comes back, we get a fresh initial list.
            previous_players = set()
            first_check = True
            empty_checks = 0
            server_was_online = False

        else:
            print(
                f"[{now}] 🔴 Server unavailable — "
                f"still waiting... ({e})"
            )

            log_line(
                now,
                "WAITING",
                "",
                [],
                str(e)
            )

    time.sleep(INTERVAL)
