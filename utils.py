import os
import sys
import itertools
import subprocess
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

def load_env(env_path: Optional[str] = None):
    """Load .env file and return a mapping of env vars."""
    env_path = env_path or Path(__file__).with_name('.env')
    load_dotenv(env_path)
    return os.environ

def build_context() -> str:
    """Collect optional contextual info such as cwd, git status, and recent shell history."""
    cwd = os.getcwd()
    ctx_parts = [f"Current directory: {cwd}"]
    
    # git status if repo
    try:
        result = subprocess.run(['git', 'status', '-s', '-b'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            ctx_parts.append("Git status:\n" + result.stdout.strip())
    except Exception:
        pass
    # last 10 history lines (bash)
    histfile = os.environ.get('HISTFILE', str(Path.home() / '.bash_history'))
    try:
        with open(histfile, 'r') as hf:
            lines = hf.readlines()[-10:]
            ctx_parts.append("Recent history:\n" + "".join(lines))
    except Exception:
        pass
    return "\n\n".join(ctx_parts)


@contextmanager
def spinner(msg: str = "Loading..."):
    """Simple terminal spinner context manager."""
    stop = False

    def spin():
        for ch in itertools.cycle("|/-\\"):
            if stop:
                break
            sys.stdout.write(f"\r{msg} {ch}")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(msg) + 2) + "\r")

    thread = threading.Thread(target=spin)
    thread.start()
    try:
        yield
    finally:
        stop = True
        thread.join()
