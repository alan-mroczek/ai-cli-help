#!/usr/bin/env python3
"""Installation script for Command Helper."""
import subprocess
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
HOME = Path.home()
SHELL_RC = HOME / '.bashrc'

def run(cmd):
    print(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def ensure_uv():
    try:
        run('uv --version')
    except subprocess.CalledProcessError:
        print('Installing uv package manager...')
        run('pip install --upgrade uv')

def install_deps():
    run("uv venv")
    run(f'cd {PROJECT_DIR} && uv pip install -r requirements.txt')

def link_commands():
    cmd_file = PROJECT_DIR / "commands.sh"
    source_line = f"source {cmd_file}\n"

    if source_line not in SHELL_RC.read_text():
        with open(SHELL_RC, "a") as rc:
            rc.write(f"\n# Command Helper\n{source_line}")
        print(f"Added source line to {SHELL_RC}")
    else:
        print("Source line already present.")

def create_env():
    example = PROJECT_DIR / ".env.example"
    target  = PROJECT_DIR / ".env"

    if target.exists():
        return

    if example.exists():
        import shutil
        shutil.copy(example, target)
        print("Created .env from .env.example – fill in your values.")
    else:
        print("Warning: .env.example missing; skipping .env creation.")

def main():
    ensure_uv()
    install_deps()
    link_commands()
    create_env()
    print('Installation complete. Restart your shell or run: source ~/.bashrc')

if __name__ == '__main__':
    main()
