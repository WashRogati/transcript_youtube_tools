#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

python3 -m venv .venv
"$ROOT/.venv/bin/pip" install -U -r requirements.txt
mkdir -p out

echo "Ambiente pronto: venv em .venv/ e pasta out/ criada."
