#!/bin/bash
set -euo pipefail
package_dir="$(cd "$(dirname "$0")/.." && pwd -P)"
if [[ ! -x "$package_dir/.venv/bin/python" ]]; then
  echo 'JvM assistant is not installed. Run bash install.sh in the package directory.' >&2; exit 1
fi
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
exec "$package_dir/.venv/bin/python" -m jvm_assistant.server
