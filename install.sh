#!/bin/bash
set -euo pipefail
package_dir="$(cd "$(dirname "$0")" && pwd -P)"
if [[ "$(uname -s)" != Darwin ]]; then
  echo '이 버전은 macOS용입니다.' >&2; exit 1
fi
chosen_python=""
for candidate in "${JVM_PYTHON:-}" python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  [[ -n "$candidate" ]] || continue
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3,11) else 1)' 2>/dev/null; then
    chosen_python="$candidate"; break
  fi
done
if [[ -z "$chosen_python" ]]; then
  echo 'Python 3.11 이상이 필요합니다. python.org에서 설치 후 다시 실행하세요.' >&2
  echo '별도 Python 사용: JVM_PYTHON=/절대경로/python3 bash install.sh' >&2; exit 1
fi
if [[ -L "$package_dir/.venv" ]]; then echo '.venv 심볼릭 링크는 지원하지 않습니다.' >&2; exit 1; fi
if [[ ! -e "$package_dir/.venv/bin/python" ]]; then "$chosen_python" -m venv "$package_dir/.venv"; fi
"$package_dir/.venv/bin/python" -m pip install --disable-pip-version-check -r "$package_dir/requirements.lock"
"$package_dir/.venv/bin/python" -m pip install --disable-pip-version-check --no-deps --no-build-isolation "$package_dir"
"$package_dir/.venv/bin/python" -m jvm_assistant.cli --help >/dev/null
echo '설치 완료. 계정 연결과 AI 등록은 docs/SETUP.md 순서로 진행하세요.'
printf '진단: "%s/.venv/bin/jvm-assistant" doctor\n' "$package_dir"
