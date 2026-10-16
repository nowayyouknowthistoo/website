#!/bin/bash
# Double-click to start Vintage Finder on a Mac.
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
python -m vintage_finder
