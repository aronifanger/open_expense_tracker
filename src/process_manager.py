"""
Process Manager

This module handles the lifecycle of the background pipeline process, making it
resilient to Streamlit page reloads. It uses a file-based approach to persist
the process ID (PID) and status.
"""
import json
import logging
import os
import signal
import subprocess
from pathlib import Path

PROCESS_FILE = Path("process_info.json")

def start_process(command: list) -> dict:
    """
    Starts a background process if one isn't already running and saves its
    info to a file.
    """
    if get_process_info():
        logging.warning("A process is already running. Cannot start a new one.")
        return None

    # Start the new process, redirecting its output to the main log file
    with open("pipeline.log", "w") as log:
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
    
    info = {
        "pid": process.pid,
        "status": "running",
        "command": " ".join(command)
    }
    
    try:
        with open(PROCESS_FILE, "w") as f:
            json.dump(info, f, indent=4)
        logging.info(f"Started process with PID {process.pid} and created state file.")
        return info
    except IOError as e:
        logging.error(f"Failed to create process state file: {e}")
        # If we can't create the file, we can't manage the process, so terminate it.
        process.terminate()
        return None

def get_process_info() -> dict:
    """
    Reads process info from the state file and checks if the process is still alive.
    Returns the info dict if alive, otherwise cleans up the file and returns None.
    """
    if not PROCESS_FILE.exists():
        return None
        
    try:
        with open(PROCESS_FILE, "r") as f:
            info = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.warning(f"Could not read state file ({e}). Cleaning up.")
        cleanup_process_file()
        return None

    pid = info.get("pid")
    if pid is None:
        cleanup_process_file()
        return None

    # Check if a process with this PID actually exists.
    if is_process_running(pid):
        return info
    else:
        # The process is dead, but the file exists. This can happen if the
        # machine reboots or the process crashes. Clean up the stale file.
        logging.warning(f"Found stale process file for dead PID {pid}. Cleaning up.")
        cleanup_process_file()
        return None

def update_process_status(status: str):
    """Updates the status of the process in the state file."""
    info = get_process_info()
    if not info:
        return

    info["status"] = status
    try:
        with open(PROCESS_FILE, "w") as f:
            json.dump(info, f, indent=4)
    except IOError as e:
        logging.error(f"Could not update process state file: {e}")

def send_signal_to_process(sig):
    """Sends a signal (e.g., SIGSTOP, SIGCONT) to the managed process."""
    info = get_process_info()
    if not info:
        logging.warning("Cannot send signal: no active process found.")
        return
    
    try:
        os.kill(info["pid"], sig)
    except ProcessLookupError:
        logging.warning(f"Process with PID {info['pid']} not found during signal. Cleaning up.")
        cleanup_process_file()
    except Exception as e:
        logging.error(f"Failed to send signal {sig} to PID {info['pid']}: {e}")

def cleanup_process_file():
    """Removes the process state file."""
    try:
        if PROCESS_FILE.exists():
            os.remove(PROCESS_FILE)
            logging.info("Process state file cleaned up.")
    except IOError as e:
        logging.error(f"Error removing process state file: {e}")

def is_process_running(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    if pid is None:
        return False
    # In Unix-like systems, sending signal 0 to a process checks for its existence
    # without actually sending a signal. It raises an OSError if the PID does not exist.
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True
