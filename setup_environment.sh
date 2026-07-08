#!/bin/bash
# Environment setup for the CEMDI 2026 "Planewave DFT with Abinit" tutorial.
#
# Run this once per student, from a terminal on the tutorial cluster
# (either an SSH session: `ssh -Y user_name@cemdi.calculquebec.cloud`,
# or a terminal opened inside JupyterLab). Safe to re-run.
#
#   bash setup_environment.sh
#
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_SRC="$SCRIPT_DIR/Installation/abinit/abipy"
CONFIG_DST="$HOME/.abinit/abipy"

echo "=== CEMDI 2026 -- Abinit/AbiPy environment setup ==="

# ---------------------------------------------------------------------------
# 1) AbiPy configuration (manager.yml / scheduler.yml)
# ---------------------------------------------------------------------------
echo
echo "--- Step 1/3: AbiPy configuration ---"
mkdir -p "$CONFIG_DST"
cp "$CONFIG_SRC/manager.yml" "$CONFIG_DST/manager.yml"
cp "$CONFIG_SRC/scheduler.yml" "$CONFIG_DST/scheduler.yml"
echo "Copied manager.yml and scheduler.yml to $CONFIG_DST"

# ---------------------------------------------------------------------------
# 2) Abinit executable
# ---------------------------------------------------------------------------
echo
echo "--- Step 2/3: Abinit executable ---"
if command -v abinit >/dev/null 2>&1; then
    echo "Found: $(command -v abinit)"
else
    echo "'abinit' not found on \$PATH yet, trying 'module load abinit' ..."
    if command -v module >/dev/null 2>&1; then
        # shellcheck disable=SC1091
        module load abinit 2>/dev/null || true
    fi
    if command -v abinit >/dev/null 2>&1; then
        echo "Found after 'module load abinit': $(command -v abinit)"
    else
        echo "WARNING: could not find 'abinit'. If you're on the cluster's"
        echo "         JupyterLab, this may be provided automatically at"
        echo "         runtime -- otherwise, ask a tutorial organizer which"
        echo "         module provides it (e.g. 'module load <name>')."
    fi
fi

# ---------------------------------------------------------------------------
# 3) AbiPy Python package
# ---------------------------------------------------------------------------
echo
echo "--- Step 3/3: AbiPy Python package ---"
if python3 -c "import abipy" >/dev/null 2>&1; then
    echo "'abipy' is already importable (this is the default inside JupyterLab)."
else
    echo "'abipy' not importable in the current environment."
    echo "Setting up a virtual environment at ~/venv_cemdi and installing"
    echo "abipy from the cluster's local wheelhouse ..."
    python3 -m venv --system-site-packages "$HOME/venv_cemdi"
    # shellcheck disable=SC1091
    source "$HOME/venv_cemdi/bin/activate"
    pip install --no-index --upgrade pip
    pip install --no-index abipy
    echo
    echo "Done. Remember to activate this environment in every new shell:"
    echo "    source ~/venv_cemdi/bin/activate"
fi

echo
echo "=== Setup complete ==="
echo "Check everything is in order with: abicheck.py"
echo "Then open Tutorial/Notebooks/abinit_cemdi_workshop.ipynb"
