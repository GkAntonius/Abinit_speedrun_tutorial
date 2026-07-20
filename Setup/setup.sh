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

CEMDI_SOURCE="$SCRIPT_DIR/source-scripts/cemdi.sh"
CEMDI_TARGET="$HOME/.cemdi.sh"
CEMDI_BASHRC_LINE="source $CEMDI_TARGET"

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
step "Installing $CEMDI_TARGET"
if [ ! -f "$CEMDI_SOURCE" ]; then
    echo "ERROR: Source file not found: $CEMDI_SOURCE" >&2
    exit 1
fi
if [ -f "$CEMDI_TARGET" ]; then
    skip "$CEMDI_TARGET already exists — not overwriting."
else
    cp "$CEMDI_SOURCE" "$CEMDI_TARGET"
    done_msg "Copied $CEMDI_SOURCE -> $CEMDI_TARGET"
fi

# --- 2. Add source line to ~/.bashrc -----------------------------------------
step "Ensuring ~/.bashrc sources $CEMDI_TARGET"
BASHRC="$HOME/.bashrc"
touch "$BASHRC"
if grep -qF "$CEMDI_BASHRC_LINE" "$BASHRC"; then
    skip "Line already present in ~/.bashrc."
else
    printf '\n# Added by Abinit speedrun tutorial setup\n%s\n' "$CEMDI_BASHRC_LINE" >> "$BASHRC"
    done_msg "Added '$CEMDI_BASHRC_LINE' to ~/.bashrc"
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

echo ""
echo "=============================================="
echo "  Setup complete."
echo "=============================================="
echo ""
