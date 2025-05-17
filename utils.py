import os
import sys
import itertools
import subprocess
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional, MutableMapping, Iterator

from dotenv import load_dotenv

def load_env(env_path: Optional[str] = None) -> MutableMapping[str, str]:
    """Load .env file and return a mapping of env vars."""
    env_path = env_path or Path(__file__).with_name('.env')
    load_dotenv(env_path)
    return os.environ

def execute_context_script() -> Optional[str]:
    """Execute .aih_context.sh script and return its output if it exists."""
    script_path = Path(__file__).with_name('.aih_context.sh')
    
    # Check if file exists and is executable
    if not script_path.exists():
        return None
    
    # Check if file is executable
    if not os.access(script_path, os.X_OK):
        print(f"Warning: .aih_context.sh exists but is not executable. Run: chmod +x {script_path}", file=sys.stderr)
        return None
    
    # Check if file has content (not empty)
    if script_path.stat().st_size == 0:
        return None
        
    try:
        result = subprocess.run([script_path], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
        print(f"Warning: Error executing context script: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Unexpected error with context script: {e}", file=sys.stderr)
    
    return None

def build_context() -> str:
    """Collect optional contextual info from custom context script only."""
    cwd = os.getcwd()
    ctx_parts = [f"Current directory: {cwd}"]
    
    # Execute custom context script if it exists
    script_output = execute_context_script()
    if script_output:
        ctx_parts.append("Additional context:\n" + script_output)
    
    return "\n\n".join(ctx_parts)


@contextmanager
def spinner(msg: str = "Loading...") -> Iterator[None]:
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
