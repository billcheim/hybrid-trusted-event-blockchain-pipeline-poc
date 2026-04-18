#!/bin/bash
set -e

cd "$(dirname "$0")"

rm -f events.db

echo "[OK] Database reset."
