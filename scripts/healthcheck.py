#!/usr/bin/env python3
"""
AI Job Hunter - Health Checker
Provides system health, uptime, and scraper status
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
import pytz


def check_health():
    """Output JSON health status"""
    project_dir = Path(__file__).parent.parent

    health = {
        "service": "AI Job Hunter",
        "status": "healthy",
        "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat(),
    }

    # Check PID file
    pid_file = project_dir / "data/runtime/scraper.pid"
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            import subprocess
            result = subprocess.run(
                ["ps", "-p", str(pid)], capture_output=True, text=True
            )
            if result.returncode == 0:
                health["scraper_pid"] = pid
                health["scraper_status"] = "running"
            else:
                health["scraper_status"] = "dead"
                health["status"] = "unhealthy"
        except Exception as e:
            health["scraper_status"] = f"error: {str(e)}"
            health["status"] = "degraded"
    else:
        health["scraper_status"] = "not running"
        health["status"] = "unhealthy"

    # Check recent logs for errors
    log_file = project_dir / "logs/scheduler_continuous.log"
    try:
        if log_file.exists():
            lines = log_file.read_text().splitlines()
            health["recent_log_entries"] = len(lines)
            health["latest_log_line"] = lines[-1] if lines else "No logs"
    except Exception:
        health["latest_log_line"] = "Cannot read logs"

    # Count recent jobs
    data_storage = project_dir / "data_storage"
    if data_storage.exists():
        recent_jobs = list(data_storage.glob("jobs_master_*.csv"))
        health["job_files_recent"] = len(recent_jobs)

    print(json.dumps(health, indent=2))
    return 0 if health["status"] == "healthy" else 1


if __name__ == "__main__":
    sys.exit(check_health())
