#!/usr/bin/env python3
"""
Supervisor script - Keeps the scraper running 24/7 with monitoring
This replaces complex external process managers with pure Python
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime

# Color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

PROJECT_DIR = Path(__file__).parent.parent
PYTHON_SCRIPT = PROJECT_DIR / "job_scraper_3hr.py"
PID_FILE = PROJECT_DIR / "data/runtime/scraper.pid"
LOG_FILE = PROJECT_DIR / "logs/supervisor.log"


def log(msg, color=RESET):
    """Log with timestamp and color"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] {msg}{RESET}")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")


def start_scraper():
    """Start the scraper process"""
    log("Starting AI Job Hunter scraper...", GREEN)

    # Load environment
    env = os.environ.copy()
    env_file = PROJECT_DIR / ".env-analyst"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if key.startswith('export '):
                    key = key[7:]  # Remove 'export '
                env[key] = value
                log(f"  Set env: {key}", RESET)

    # Start process
    process = subprocess.Popen(
        [sys.executable, str(PYTHON_SCRIPT)],
        cwd=PROJECT_DIR,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Save PID
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(process.pid))

    log(f"Scraper started with PID {process.pid}", GREEN)
    return process


def monitor_process(process):
    """Monitor the scraper process and capture output"""
    while True:
        if process.poll() is not None:
            break

        # Read output line by line
        try:
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
                with open(PROJECT_DIR / "logs/scheduler_continuous.log", 'a') as f:
                    f.write(line)
        except Exception as e:
            time.sleep(1)

    return process.returncode


def restart_scraper(old_process, wait_time=10):
    """Restart the scraper after failure"""
    log(f"Scraper died (exit code: {old_process.returncode})", RED)

    # Wait before restart
    log(f"Waiting {wait_time} seconds before restart...", YELLOW)
    time.sleep(wait_time)

    # Start new process
    new_process = start_scraper()
    log("Restarted successfully", GREEN)
    return new_process


def main():
    log(f"{BOLD}AI Job Hunter Supervisor{RESET} - PID: {os.getpid()}")
    log("Press Ctrl+C to stop\n")

    # Check if already running
    if PID_FILE.exists():
        old_pid = PID_FILE.read_text().strip()
        try:
            import subprocess
            result = subprocess.run(
                ["ps", "-p", old_pid],
                capture_output=True
            )
            if result.returncode == 0:
                log(f"Already running with PID {old_pid}", YELLOW)
                log("Stop it first: python3 scripts/supervisor.py stop", YELLOW)
                return
            else:
                PID_FILE.unlink(missing_ok=True)
        except Exception:
            PID_FILE.unlink(missing_ok=True)

    # Start scraper
    process = start_scraper()

    # Graceful shutdown
    def handle_signal(sig, frame):
        log("\nShutdown signal received, stopping scraper...", YELLOW)
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        PID_FILE.unlink(missing_ok=True)
        log("Supervisor stopped", GREEN)
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Monitor loop
    restart_count = 0
    try:
        while True:
            returncode = process.poll()
            if returncode is not None:
                log(f"Scraper exited with code {returncode}", RED)
                restart_count += 1

                # Exponential backoff after multiple restarts
                wait_time = min(60, 5 * (2 ** min(restart_count, 4)))
                log(f"Restart attempt #{restart_count} (wait: {wait_time}s)", YELLOW)

                process = restart_scraper(process, wait_time)

                if restart_count > 20:
                    log("Too many restarts, giving up after 20 attempts", RED)
                    break

            time.sleep(2)

    except KeyboardInterrupt:
        handle_signal(signal.SIGINT, None)


if __name__ == "__main__":
    main()
