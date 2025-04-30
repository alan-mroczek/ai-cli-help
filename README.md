# ai-cli-help (aih - AI Help)

AI-powered command helper for your terminal. Built for Bash, customizable and ready to extend.

Terminal‑integrated assistant that **suggests shell commands** with help from a Large Language Model (LLM).

> "Describe what you want → pick a suggestion → optionally run it."

---

## ✨ Features

- **LLM‑powered suggestions** (OpenAI, Ollama)
- **Interactive picker** – always asks before running
- **Context‑aware** – optionally include cwd, `git status`, and recent history
- **Customizable** via `commands.md` to let LLM know what you want
- **Custom context script** – use `.aih_context.sh` to provide additional system context
- **Single Bash function** (`aih`) for quick access
- **Configurable** through `.env` or CLI flags
- **MIT‑licensed** and Python 3.11+ compatible

---

## 🛠️ Installation

```bash
# 1. Clone or unzip
git clone https://github.com/alan-mroczek/ai-cli-help.git
cd ai-cli-help

# 2. Run installer (installs deps with uv, sets up .env & shell hook)
python install.py

# 3. Reload shell
source ~/.bashrc
```

> **Note**: The script uses **[uv](https://github.com/astral-sh/uv)** for fast, isolated deps.  
> If `uv` isn’t installed, the installer will fetch it.

---

## ⚡ Quick Start

```bash
aih --help
```

```
usage: aih [-h] [--context] [--model MODEL] [--max MAX_SUGGESTIONS]
           [--no-confirm] [--history]
           [prompt ...]

Suggest shell commands with LLM assistance.

positional arguments:
  prompt                Describe what you want to do

options:
  -h, --help            show this help message and exit
  --context             Include directory & git context in the LLM prompt
                        (default from INCLUDE_CONTEXT in .env)
  --model MODEL         Override model name (default from MODEL in .env)
  --max MAX_SUGGESTIONS
                        Max suggestions (default from MAX_SUGGESTIONS in .env)
  --no-confirm          Skip command confirmation prompt (default from
                        REQUIRE_CONFIRMATION in .env)
  --history             Display command history and exit
```

Example session:

```bash
aih large files here
```

```   
Suggestions:
  1. du -ah . | sort -rh | head -n 10

Options:
  Enter a number to select a command
  r - Regenerate suggestions
  c - Add a comment or clarification
  0 or empty - Quit

Your choice:
```

---

## 🔧 Configuration

### `.env` (see .env.example for up to date list)

| Key               | Purpose                                                  | Example                     |
| ----------------- | ---------------------------------------------------      | --------------------------- |
| `OPENAI_API_KEY`  | API key for OpenAI models                                | `sk-…`                      |
| `MODEL`           | Default model (`openai/gpt-4o-mini`, `ollama/codellama`) | `openai/gpt-4o-mini`        |
| `OLLAMA_API_URL`  | Ollama chat endpoint                                     | `http://local…::11434/api/…`|
| `MAX_SUGGESTIONS` | Limit shown suggestions                                  | `3`                         |

### CLI Flags

| Flag        | Description                      |
| ----------- | -------------------------------- |
| `--context` | Include cwd, git info, & history |
| `--model`   | Override model for a single call |
| `--max`     | Override max suggestions         |

### `commands.md`

This file is a free-form cheat-sheet for the LLM.  
There’s **no rigid schema**—the model simply reads the text and tries to imitate or reuse whatever it finds—so write it in whatever style feels natural.  

### `.aih_context.sh`

This optional script allows you to add custom context gathering commands.
- An empty executable script is created during installation
- Copy commands from `.aih_context.example.sh` or write your own
- The script is executed each time you run `aih --context`
- Output from each command will be included in the LLM prompt
- Perfect for adding project-specific context or system information
- Empty scripts are safely ignored and won't affect the context

---

## 📂 Project Layout

```
ai-cli-help/
├── main.py              # Entry point
├── model.py             # LLM abstraction
├── utils.py             # Helpers (spinner, context, env)
├── install.py           # One‑shot installer
├── commands.sh          # Bash wrapper (sources aih)
├── commands.md          # Docs (git-ignored)
├── commands.example.md  # Docs example
├── .aih_context.sh      # Custom context script (git-ignored)
├── .aih_context.example.sh # Context script example
├── .env                 # Configuration (git-ignored)
├── .env.example         # Configuration example, used as a template to create .env
└── LICENSE
```

---

## 🛡️ License

Licensed under the **MIT License** – see `LICENSE` for details.
