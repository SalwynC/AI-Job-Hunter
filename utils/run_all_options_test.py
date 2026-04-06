#!/usr/bin/env python3
"""Run all 5 options in parallel with error monitoring."""

import subprocess
import os
import sys
import time
import signal
from pathlib import Path
from datetime import datetime

os.chdir(Path(__file__).parent)

# Color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

print(f"{BLUE}{'='*60}{NC}")
print(f"{YELLOW}🚀 RUNNING ALL 5 OPTIONS SIMULTANEOUSLY{NC}")
print(f"{BLUE}{'='*60}{NC}\n")

# Define all options
options = {
    "main.py": {"timeout": 60, "cmd": ["python3", "main.py"]},
    "job_scraper_3hr.py": {"timeout": 15, "cmd": ["python3", "job_scraper_3hr.py"]},
    "job_digest_scheduler.py": {"timeout": 15, "cmd": ["python3", "job_digest_scheduler.py"]},
    "telegram_bot.py": {"timeout": 15, "cmd": ["python3", "telegram_bot.py"]},
    "cloud_run.py": {"timeout": 15, "cmd": ["python3", "cloud_run.py"]},
}

# Create logs directory
Path("logs/concurrent_run").mkdir(parents=True, exist_ok=True)

# Start all processes
processes = {}
print(f"{YELLOW}Starting processes...{NC}\n")

for name, config in options.items():
    log_file = f"logs/concurrent_run/{name.replace('.py', '')}.log"
    print(f"{BLUE}[{name}]{NC} Starting with timeout={config['timeout']}s")
    print(f"  Logging to: {log_file}")
    
    try:
        with open(log_file, "w") as logfh:
            proc = subprocess.Popen(
                config["cmd"],
                stdout=logfh,
                stderr=subprocess.STDOUT,
                text=True
            )
            processes[name] = {
                "proc": proc,
                "timeout": config["timeout"],
                "start_time": time.time(),
                "log_file": log_file
            }
            print(f"  ✓ PID: {proc.pid}\n")
    except Exception as e:
        print(f"  {RED}✗ ERROR: {e}{NC}\n")

# Monitor processes
print(f"{BLUE}{'='*60}{NC}")
print(f"{YELLOW}Monitoring execution...{NC}")
print(f"{BLUE}{'='*60}{NC}\n")

completed = {}
time.sleep(2)

# Wait for processes with timeout
for name, proc_info in processes.items():
    proc = proc_info["proc"]
    timeout = proc_info["timeout"]
    
    try:
        proc.wait(timeout=timeout)
        elapsed = time.time() - proc_info["start_time"]
        completed[name] = {
            "exit_code": proc.returncode,
            "elapsed": elapsed,
            "status": "✓ OK" if proc.returncode == 0 else "✗ FAILED"
        }
        print(f"{GREEN}[✓]{NC} {name} completed in {elapsed:.1f}s (exit: {proc.returncode})")
    except subprocess.TimeoutExpired:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        elapsed = time.time() - proc_info["start_time"]
        completed[name] = {
            "exit_code": -1,
            "elapsed": elapsed,
            "status": "⏱  TIMEOUT"
        }
        print(f"{YELLOW}[⏱ ]{NC} {name} timed out after {elapsed:.1f}s (killed)")
    except Exception as e:
        print(f"{RED}[✗]{NC} {name} error: {e}")

print(f"\n{BLUE}{'='*60}{NC}")
print(f"{YELLOW}📊 EXECUTION SUMMARY{NC}")
print(f"{BLUE}{'='*60}{NC}\n")

# Analyze logs for errors
error_summary = {}
for name, proc_info in processes.items():
    log_file = proc_info["log_file"]
    if not Path(log_file).exists():
        error_summary[name] = {"errors": 0, "warnings": 0, "info": 0, "status": "NO LOG"}
        continue
    
    with open(log_file, "r") as f:
        content = f.read()
    
    errors = content.count(" ERROR ")
    warnings = content.count(" WARNING ")
    infos = content.count(" INFO ")
    
    error_summary[name] = {
        "errors": errors,
        "warnings": warnings,
        "info": infos,
        "status": completed.get(name, {}).get("status", "?")
    }
    
    # Print summary for each option
    print(f"{BLUE}[{name}]{NC}")
    print(f"  Status: {error_summary[name]['status']}")
    print(f"  Metrics: INFO={infos} | WARNING={warnings} | ERROR={errors}")
    
    if errors > 0:
        print(f"  {RED}[!] ERRORS FOUND:{NC}")
        # Extract error lines
        for line in content.split("\n"):
            if " ERROR " in line or "Traceback" in line:
                print(f"    {line}")
                break
    
    # Show last few lines
    lines = content.strip().split("\n")
    if lines:
        print(f"  Last output:")
        for line in lines[-2:]:
            print(f"    {line}")
    print()

print(f"{BLUE}{'='*60}{NC}")
print(f"{GREEN}✅ ALL OPTIONS EXECUTION COMPLETE{NC}")
print(f"{BLUE}{'='*60}{NC}\n")

# Summary stats
total_errors = sum(s["errors"] for s in error_summary.values())
total_warnings = sum(s["warnings"] for s in error_summary.values())
success_count = sum(1 for s in error_summary.values() if "TIMEOUT" not in s["status"])

print(f"Total Processes: {len(processes)}")
print(f"Completed: {success_count}/{len(processes)}")
print(f"Total Errors: {total_errors}")
print(f"Total Warnings: {total_warnings}")
print()

sys.exit(0 if total_errors == 0 else 1)
