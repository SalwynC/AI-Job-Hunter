#!/usr/bin/env python3
"""
Lightweight Health Check Server
Runs on port 8080 (or $HEALTH_PORT)
Provides /health and /status endpoints for monitoring
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
import pytz
from http.server import HTTPServer, BaseHTTPRequestHandler

# Get project directory
SCRIPT_DIR = Path(__file__).parent.parent
PROJECT_DIR = SCRIPT_DIR.parent


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP request handler for health checks"""

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health' or self.path == '/healthz':
            health = self.get_health()
            self.send_response(200 if health['status'] == 'healthy' else 503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health, indent=2).encode())
        elif self.path == '/status':
            status = self.get_status()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status, indent=2).encode())
        elif self.path == '/metrics':
            metrics = self.get_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(metrics.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def get_health(self):
        """Return health check JSON"""
        health = {
            "service": "ai-job-hunter",
            "status": "healthy",
            "timestamp": datetime.now(pytz.timezone("Asia/Kolkata")).isoformat()
        }

        # Check scraper process
        pid_file = PROJECT_DIR / "data/runtime/scraper.pid"
        if pid_file.exists():
            try:
                pid = int(pid_file.read_text().strip())
                result = subprocess.run(
                    ["ps", "-p", str(pid)],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    health["scraper_running"] = True
                else:
                    health["scraper_running"] = False
                    health["status"] = "unhealthy"
            except Exception as e:
                health["scraper_running"] = False
                health["status"] = "degraded"
                health["error"] = str(e)
        else:
            health["scraper_running"] = False
            health["status"] = "unhealthy"

        return health

    def get_status(self):
        """Return detailed status information"""
        status = self.get_health()
        status["details"] = {}

        # Check recent job files
        data_storage = PROJECT_DIR / "data_storage"
        if data_storage.exists():
            recent_jobs = list(data_storage.glob("jobs_master_*.csv"))
            status["details"]["recent_job_files"] = len(recent_jobs)

        # Check logs
        log_file = PROJECT_DIR / "logs/scheduler_continuous.log"
        if log_file.exists():
            try:
                log_size = log_file.stat().st_size / (1024*1024)  # MB
                status["details"]["log_file_size_mb"] = round(log_size, 2)
                tail = subprocess.run(
                    ["tail", "-5", str(log_file)],
                    capture_output=True, text=True
                )
                status["details"]["recent_log"] = tail.stdout.strip().split('\n')[-1] if tail.stdout else ""
            except Exception:
                pass

        # Memory usage if PID exists
        if status.get("scraper_running"):
            try:
                pid_file = PROJECT_DIR / "data/runtime/scraper.pid"
                pid = int(pid_file.read_text().strip())
                result = subprocess.run(
                    ["ps", "-p", str(pid), "-o", "rss="],
                    capture_output=True, text=True
                )
                if result.stdout:
                    mem_kb = int(result.stdout.strip())
                    status["details"]["memory_usage_mb"] = round(mem_kb / 1024, 1)
            except Exception:
                pass

        return status

    def get_metrics(self):
        """Return Prometheus-style metrics (simplified)"""
        metrics = []

        # Scraper status
        health = self.get_health()
        status_val = 1 if health.get("scraper_running") else 0
        metrics.append(f"ai_job_hunter_scraper_running {status_val}")

        # Job count
        data_storage = PROJECT_DIR / "data_storage"
        if data_storage.exists():
            recent_jobs = list(data_storage.glob("jobs_master_*.csv"))
            metrics.append(f"ai_job_hunter_job_files {len(recent_jobs)}")

        return '\n'.join(metrics) + '\n'


def run_server(port=8080):
    """Run the health check server"""
    port = int(os.getenv('HEALTH_PORT', port))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Health server listening on port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down health server")
        server.shutdown()


if __name__ == "__main__":
    run_server()