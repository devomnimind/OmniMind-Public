#!/usr/bin/env bash
set -euo pipefail

BASEDIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "$BASEDIR/.."

OMNIMIND_DASHBOARD_USER=${OMNIMIND_DASHBOARD_USER:-dashboard}
OMNIMIND_DASHBOARD_PASS=${OMNIMIND_DASHBOARD_PASS:-omnimind}
export OMNIMIND_DASHBOARD_USER
export OMNIMIND_DASHBOARD_PASS

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker não encontrado. Instale Docker antes de rodar o dashboard."
  exit 1
fi

exec docker compose up --build
