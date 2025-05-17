import psutil
import subprocess
import time
import os
import threading
import sys

# === Terminal Color ===
BLUE = "\033[96m"
RESET = "\033[0m"
YELLOW = "\033[93m"
GREEN = "\033[92m"

# === Configuration ===
CONFIG_FILE = "config.txt"
DEFAULT_CONFIG = {
    "discord_path": "C:\\Path\\To\\Discord.exe",
    "priority": "high",
    "interval": "15",
}

CONFIG_TEMPLATE = f"""# Configuration for Discord Priority Setter
# Set the full path to your Discord.exe below:
discord_path={DEFAULT_CONFIG['discord_path']}

# Priority options: low, below_normal, normal, above_normal, high, realtime
priority={DEFAULT_CONFIG['priority']}

# Interval in seconds between priority checks
interval={DEFAULT_CONFIG['interval']}
"""

PRIORITY_LEVELS = {
    "low": psutil.IDLE_PRIORITY_CLASS,
    "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "normal": psutil.NORMAL_PRIORITY_CLASS,
    "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "high": psutil.HIGH_PRIORITY_CLASS,
    "realtime": psutil.REALTIME_PRIORITY_CLASS,
}

PRIORITY_ORDER = {
    psutil.IDLE_PRIORITY_CLASS: 0,
    psutil.BELOW_NORMAL_PRIORITY_CLASS: 1,
    psutil.NORMAL_PRIORITY_CLASS: 2,
    psutil.ABOVE_NORMAL_PRIORITY_CLASS: 3,
    psutil.HIGH_PRIORITY_CLASS: 4,
    psutil.REALTIME_PRIORITY_CLASS: 5,
}

# === Utility Functions ===


def print_info(text):
    print(f"{BLUE}{text}{RESET}")


def create_default_config():
    with open(CONFIG_FILE, "w") as f:
        f.write(CONFIG_TEMPLATE)
    print_info(
        f"No config found. Created default '{CONFIG_FILE}'. Please edit it and restart."
    )


def read_config():
    if not os.path.isfile(CONFIG_FILE):
        create_default_config()
        return DEFAULT_CONFIG.copy()

    config = DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip().lower()] = val.strip()
    except Exception as e:
        print_info(f"Failed to read config file: {e}")
    return config


def set_self_low_priority():
    try:
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    except Exception:
        pass


# === Discord Logic ===


def is_real_discord_process(proc):
    try:
        return proc.name().lower() == "discord.exe"
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def discord_running():
    return any(is_real_discord_process(p) for p in psutil.process_iter(["name"]))


def start_discord(path):
    try:
        subprocess.Popen(
            [path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        print_info("Started Discord.")
    except Exception as e:
        print_info(f"Failed to start Discord: {e}")


def set_priority_if_needed(proc, target_priority):
    try:
        current = proc.nice()
        if PRIORITY_ORDER.get(current, -1) < PRIORITY_ORDER.get(target_priority, -1):
            proc.nice(target_priority)
            print_info(f"Set PID {proc.pid} to higher priority.")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass


def list_discord_processes():
    print_info("\nCurrent Discord processes:")
    found = False
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] and "discord" in proc.info["name"].lower():
                prio = proc.nice()
                prio_name = next(
                    (k for k, v in PRIORITY_LEVELS.items() if v == prio), str(prio)
                )
                print_info(f" - PID {proc.pid}, Priority: {prio_name}")
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    if not found:
        print_info(" - None found.")


def kill_discord_processes():
    print_info("Terminating Discord...")
    for proc in psutil.process_iter(["name", "pid"]):
        try:
            if proc.info["name"] and "discord" in proc.info["name"].lower():
                proc.terminate()
                print_info(f" - Terminated PID {proc.pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


# === Threading: Background Monitor + CLI ===


def progress_bar(seconds):
    for i in range(seconds):
        done = int(30 * (i + 1) / seconds)
        sys.stdout.write(
            f"\r{GREEN}Waiting for Discord... [{'#' * done}{' ' * (30 - done)}] {i+1}s{RESET}"
        )
        sys.stdout.flush()
        time.sleep(1)
    print()


def monitor_loop(stop_event, config_lock, config):
    while not stop_event.is_set():
        with config_lock:
            path = config["discord_path"]
            priority_name = config["priority"].lower()
            interval = int(config["interval"])

        if priority_name not in PRIORITY_LEVELS:
            print_info(f"Invalid priority '{priority_name}', defaulting to 'high'")
            priority_name = "high"
        target_priority = PRIORITY_LEVELS[priority_name]

        if not os.path.isfile(path):
            print_info(f"Invalid path: {path}")
            time.sleep(5)
            continue

        if not discord_running():
            start_discord(path)
            progress_bar(30)

        for proc in psutil.process_iter(["name", "pid"]):
            if is_real_discord_process(proc):
                set_priority_if_needed(proc, target_priority)

        time.sleep(interval)


def user_input_loop(stop_event, config_lock, config):
    print_info("Commands: [r]eload config, [q]uit and stop Discord")
    while not stop_event.is_set():
        try:
            user_input = input()
            if user_input.lower() == "r":
                new_config = read_config()
                with config_lock:
                    config.update(new_config)
                print_info("Config reloaded.")
                print_settings(config)
            elif user_input.lower() == "q":
                kill_discord_processes()
                stop_event.set()
        except EOFError:
            stop_event.set()


# === CLI ===


def print_settings(config):
    print_info("\nCurrent Settings:")
    print_info(f"  Discord path: {config['discord_path']}")
    print_info(f"  Priority:     {config['priority']}")
    print_info(f"  Interval:     {config['interval']}s")


# === Main ===


def main():
    print_info("Discord Priority Setter\n" + "-" * 25)
    set_self_low_priority()

    config_lock = threading.Lock()
    config = read_config()
    stop_event = threading.Event()

    print_settings(config)
    list_discord_processes()

    threading.Thread(
        target=monitor_loop, args=(stop_event, config_lock, config), daemon=True
    ).start()
    threading.Thread(
        target=user_input_loop, args=(stop_event, config_lock, config), daemon=True
    ).start()

    try:
        while not stop_event.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print_info("Interrupted by user.")
        stop_event.set()


if __name__ == "__main__":
    main()
