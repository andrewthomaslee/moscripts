#!/usr/bin/env bash

# This script configures VS Code's Python interpreter settings
# based on the active Nix development shell.

PYTHON_INTERPRETER=$(which python)
REPO_ROOT=$(git rev-parse --show-toplevel)
VSCODE_SETTINGS_DIR="$REPO_ROOT/.vscode"
mkdir -p "$VSCODE_SETTINGS_DIR"
# Use jq to update or create settings.json
if [ -f "$VSCODE_SETTINGS_DIR/settings.json" ]; then
  jq --arg pythonPath "$PYTHON_INTERPRETER" \
     '. + {"python.defaultInterpreterPath": $pythonPath, "python.terminal.activateEnvironment": true, "python.terminal.activateEnvInCurrentTerminal": true}' \
     "$VSCODE_SETTINGS_DIR/settings.json" > "$VSCODE_SETTINGS_DIR/settings.json.tmp" && \
  mv "$VSCODE_SETTINGS_DIR/settings.json.tmp" "$VSCODE_SETTINGS_DIR/settings.json"
else
  jq -n \
     --arg pythonPath "$PYTHON_INTERPRETER" \
     '{
       "python.defaultInterpreterPath": $pythonPath,
       "python.terminal.activateEnvironment": true,
       "python.terminal.activateEnvInCurrentTerminal": true
     }' > "$VSCODE_SETTINGS_DIR/settings.json"
fi
echo "✅ VS Code configured with Python: $PYTHON_INTERPRETER"
