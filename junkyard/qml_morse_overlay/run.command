#!/bin/zsh
cd "$(dirname "$0")"
if command -v qml >/dev/null 2>&1; then
  qml main.qml
elif command -v qmlscene >/dev/null 2>&1; then
  qmlscene main.qml
else
  echo "Qt QML runtime not found. Install Qt 6 from https://www.qt.io/download or via Homebrew: brew install qt"
  echo "Then run: qml main.qml"
  read "?Press Enter to close."
fi
