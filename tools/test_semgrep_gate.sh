#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fixture_dir="$(mktemp -d "${TMPDIR:-/tmp}/semgrep-gate.XXXXXX")"
trap 'rm -rf "$fixture_dir"' EXIT

semgrep_cmd=(semgrep)
if ! command -v semgrep >/dev/null 2>&1; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "Semgrep or Docker is required" >&2
    exit 2
  fi
  semgrep_cmd=(docker run --rm -v "$repo_root:/src" -w /src semgrep/semgrep:1.174.0)
fi

cat > "$fixture_dir/vulnerable.py" <<'PY'
import subprocess


def run_command(value):
    return subprocess.run(value, shell=True)
PY

cat > "$fixture_dir/safe.py" <<'PY'
import subprocess


def run_command(value):
    return subprocess.run(["/usr/bin/printf", "%s", value], check=True)
PY

run_scan() {
  "${semgrep_cmd[@]}" scan --config "$repo_root/semgrep/rules.yml" --error "$@"
}

if run_scan "$fixture_dir/vulnerable.py" >/dev/null 2>&1; then
  echo "Expected vulnerable fixture to fail Semgrep" >&2
  exit 1
fi

if ! run_scan "$fixture_dir/safe.py" >/dev/null; then
  echo "Expected safe fixture to pass Semgrep" >&2
  exit 1
fi

echo "Semgrep gate fixtures behaved as expected"
