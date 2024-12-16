#!/bin/python

import os
import sys
import subprocess
import time
import re

FIFO_PATH = "/tmp/tts-fifo"
DAEMON_PIDFILE = "/tmp/tts-daemon.pid"
script_dir = "/home/mika/prj/grammar-correction"
DAEMON_SCRIPT = os.path.join(script_dir, "tts-daemon.py")

def daemon_is_running():
    if not os.path.exists(DAEMON_PIDFILE):
        return False
    with open(DAEMON_PIDFILE, 'r') as pidfile:
        pid = pidfile.read().strip()
        # Check if process with this PID exists and is the daemon
        return os.path.exists(f"/proc/{pid}")

def start_daemon():
    print("Starting daemon...")
    subprocess.Popen(["python", DAEMON_SCRIPT], start_new_session=True)
    # Wait for the PID file to appear, indicating the daemon has started
    print("Waiting for daemon to initialize...")
    for _ in range(30):  # Wait up to 30 seconds
        if os.path.exists(FIFO_PATH):
            print("Daemon started.")
            return True
        time.sleep(1)
    print("Daemon did not start properly.")
    return False

def preprocess_text(text):
    # Remove all carriage returns
    text = text.replace('\n\n', '<br\>')
    text = text.replace('\r', ' ')
    text = text.replace('\n', ' ')
    text = text.replace('<br\>', '\n')
    # Custom pronunciations
    custom_pronunciations = {
        r'c\+\+': 'C plus plus',
        r'risc-v': 'RISC 5',
        r'diablo iv': 'Diablo 4',
    }
    for pattern, replacement in custom_pronunciations.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def send_text(text):
    processed_text = preprocess_text(text)
    if not daemon_is_running():
        if not start_daemon():
            print("Failed to start daemon.")
            return
    with open(FIFO_PATH, 'w') as fifo:
        fifo.write(processed_text)

if __name__ == "__main__":
    # sys.argv[1] is the file, open that file and put the content of the file in the text variable
    with open(sys.argv[1], 'r') as file:
        text = file.read()
    if text:
        send_text(text)
    else:
        print("Usage: python speak.py <text>")
