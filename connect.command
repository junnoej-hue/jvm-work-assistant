#!/bin/bash
set -euo pipefail
package_dir="$(cd "$(dirname "$0")" && pwd -P)"
runner="$package_dir/.venv/bin/jvm-assistant"
if [[ ! -x "$runner" ]]; then echo '먼저 AI에게 install.sh 설치를 요청하세요.'; read -r -p 'Enter로 닫기' reply; exit 1; fi
echo 'JvM 업무 도우미 · 내 계정 연결'
echo '1) Zimbra 연결  2) Webex 연결  3) Webex 회사 방 선택  4) 연결 진단'
read -r -p '번호: ' choice
case "$choice" in
1) "$runner" setup zimbra ;;
2) "$runner" setup webex ;;
3) "$runner" setup rooms ;;
4) "$runner" doctor --live ;;
*) echo '변경하지 않았습니다.' ;;
esac
read -r -p 'Enter로 닫기' reply
