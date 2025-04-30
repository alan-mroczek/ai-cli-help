# Resolve repo directory at *source* time
readonly AIH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

aih() {
  uv run python3 "$AIH_DIR/main.py" "$@"
}
