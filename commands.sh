# commands.sh  ── sourced from ~/.bashrc
readonly AIH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# temp file, python script writes to it
# allows for history push and eval
AIH_FILE="$AIH_DIR/.aih_command"
trap 'rm -f "$AIH_FILE"' EXIT

aih() {
  rm -f "$AIH_FILE"

  trap 'rm -f "$AIH_FILE"' RETURN

  ( cd "$AIH_DIR" && uv run python3 main.py "$@" )

  if [[ -s "$AIH_FILE" ]]; then
    cmd=$(<"$AIH_FILE")

    history -s -- "$cmd"
    eval "$cmd"
  else
    echo "No command found."
  fi
}
