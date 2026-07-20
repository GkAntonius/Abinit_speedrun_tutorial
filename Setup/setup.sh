#!/bin/bash
# Environment setup for the CEMDI 2026 "Planewave DFT with Abinit" tutorial.
#
# Run this once per student, from a terminal on the tutorial cluster
# (either an SSH session: `ssh -Y user_name@cemdi.calculquebec.cloud`,
# or a terminal opened inside JupyterLab). Safe to re-run.
#
#   bash setup.sh


#!/usr/bin/env bash
# ==============================================================================
#  Abinit speedrun tutorial setup
# ==============================================================================

set -euo pipefail

# --- Configuration (edit these paths to change source files) -----------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SOURCE_SCRIPT="$SCRIPT_DIR/source-scripts/cemdi.sh"
SOURCE_TARGET="$HOME/.cemdi.sh"
SOURCE_BASHRC_LINE="source $SOURCE_TARGET"

MANAGER_SOURCE="$SCRIPT_DIR/abipy-config/cemdi/manager.yml"
SCHEDULER_SOURCE="$SCRIPT_DIR/abipy-config/cemdi/scheduler.yml"
ABIPY_DIR="$HOME/.abinit/abipy"
# -----------------------------------------------------------------------------

banner() {
    echo ""
    echo "=============================================="
    echo "  Abinit speedrun tutorial setup"
    echo "=============================================="
    echo ""
}

step() {
    echo ">>> $*"
}

skip() {
    echo "    [skip] $*"
}

done_msg() {
    echo "    [done] $*"
}

banner

# --- 1. Copy cemdi.sh --------------------------------------------------------
step "Installing $SOURCE_TARGET"
if [ ! -f "$SOURCE_SCRIPT" ]; then
    echo "ERROR: Source file not found: $SOURCE_SCRIPT" >&2
    exit 1
fi
if [ -f "$SOURCE_TARGET" ]; then
    skip "$SOURCE_TARGET already exists — not overwriting."
else
    cp "$SOURCE_SCRIPT" "$SOURCE_TARGET"
    done_msg "Copied $SOURCE_SCRIPT -> $SOURCE_TARGET"
fi

# --- 2. Add source line to ~/.bashrc -----------------------------------------
step "Ensuring ~/.bashrc sources $SOURCE_TARGET"
BASHRC="$HOME/.bashrc"
touch "$BASHRC"
if grep -qF "$SOURCE_BASHRC_LINE" "$BASHRC"; then
    skip "Line already present in ~/.bashrc."
else
    printf '\n# Added by Abinit speedrun tutorial setup\n%s\n' "$SOURCE_BASHRC_LINE" >> "$BASHRC"
    done_msg "Added '$SOURCE_BASHRC_LINE' to ~/.bashrc"
fi

# --- 3. Create ~/.abinit/abipy -----------------------------------------------
step "Creating directory $ABIPY_DIR"
if [ -d "$ABIPY_DIR" ]; then
    skip "$ABIPY_DIR already exists."
else
    mkdir -p "$ABIPY_DIR"
    done_msg "Created $ABIPY_DIR"
fi

# --- 4. Copy abipy config files ----------------------------------------------
for SRC in "$MANAGER_SOURCE" "$SCHEDULER_SOURCE"; do
    FILENAME="$(basename "$SRC")"
    DEST="$ABIPY_DIR/$FILENAME"
    step "Installing $DEST"
    if [ ! -f "$SRC" ]; then
        echo "ERROR: Source file not found: $SRC" >&2
        exit 1
    fi
    if [ -f "$DEST" ]; then
        skip "$DEST already exists — not overwriting."
    else
        cp "$SRC" "$DEST"
        done_msg "Copied $SRC -> $DEST"
    fi
done

# --- 5. Source the installed script ----------------------------------------------
step "source $SOURCE_TARGET"
source $SOURCE_TARGET

echo ""
echo "=============================================="
echo "  Setup complete."
echo "=============================================="
echo ""
