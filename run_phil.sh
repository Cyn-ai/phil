#!/bin/bash
# Phil 24/7 runner — sets the environment and loops cycle-by-cycle.
# Managed by launchd (ai.phil.trader). KeepAlive restarts this if it ever dies.
set -u
cd /Users/liran/Desktop/phil-investigation

export PATH="/Users/liran/.nvm/versions/node/v22.19.0/bin:/opt/homebrew/bin:$PATH"
export PEARL_CONNECT_STORE="/Users/liran/.operate/services/sc-2a300821-b4eb-498c-aed6-5deea3b2bcfc/persistent_data"
export CONNECT_POLYMARKET_VENV="/Users/liran/.cache/connect-polymarket/venv313"
export SSL_CERT_FILE="$(/Users/liran/.cache/connect-polymarket/venv313/bin/python -c 'import certifi; print(certifi.where())' 2>/dev/null)"
export REQUESTS_CA_BUNDLE="$SSL_CERT_FILE"

while true; do
  ./loop.sh 1 45 --real
  # 45 minutes between cycle starts; the agent's own pacing decides FULL vs LIGHT.
  sleep 2700
done
