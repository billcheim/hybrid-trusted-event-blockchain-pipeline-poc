#!/bin/bash
set -e

cd "$(dirname "$0")"
source venv/bin/activate

echo "[1/3] Starting bridge service..."
lxterminal -e "bash -c 'cd $PWD && source venv/bin/activate && python bridge_service.py; exec bash'" &

sleep 2

echo "[2/3] Starting LoRa simulator..."
lxterminal -e "bash -c 'cd $PWD && source venv/bin/activate && python lora_sim.py; exec bash'" &

sleep 2

echo "[3/3] Starting LTE simulator..."
lxterminal -e "bash -c 'cd $PWD && source venv/bin/activate && python lte_sim.py; exec bash'" &
