#!/bin/bash
# Double-click to start Vintage Finder on a Mac.
cd "$(dirname "$0")" || exit 1
case "$PWD" in
  "$HOME/Desktop"*|"$HOME/Documents"*|"$HOME/Downloads"*)
    echo "macOS blocks apps from writing inside Desktop, Documents and Downloads."
    echo "Move the VintageFinder folder into your home folder (Finder > Go > Home), then start it again."
    exit 1;;
esac
if ! command -v python3 >/dev/null; then
  echo "Python 3 isn't installed. Get it from https://www.python.org/downloads/ and run this again."
  exit 1
fi
[ -x .venv/bin/python ] || python3 -m venv .venv || { echo "Couldn't create .venv here."; exit 1; }
.venv/bin/python -m pip install -q -r requirements.txt || { echo "Installing requirements failed."; exit 1; }
.venv/bin/python -m vintage_finder
