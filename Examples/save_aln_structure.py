#!/usr/bin/env python
"""
Companion to `1-Task_to_flow.ipynb`, step 3 (plotting).

Plots the band structure from `flow_si_ebands/`, the output of the `Flow`
version of the same calculation (`run_si_ebands.py`). Compare with
`plot_si_bands_1.py`, which plots the same physics from the two
manually-chained tasks instead.

Usage
-----
    python plot_si_bands_2.py
"""
from pathlib import Path

import abipy.abilab as abilab
import abipy.flowtk as flowtk
from abipy.abilab import Structure

import numpy as np
import matplotlib.pyplot as plt

# This script is meant to be copied -- together with the rest of this
# Tutorial/ directory -- into your own work directory. Data/Pseudos and
# Data/Structures are located relative to *this file*.
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Data"
PSEUDO_DIR = DATA_DIR / "Pseudos"
STRUCTURE_DIR = DATA_DIR / "Structures"

def main():
    # Get flow directory
    dirname = SCRIPT_DIR / 'flow_aln_relax'
    flow = flowtk.Flow.from_file(dirname)     # Open flow object.
    task = flow[0][0]                         # Select the first task of the first work.
    gsr_path = task.outdir.has_abiext('GSR')  # Retrieve output GSR file of this task.
    
    # Extract results
    gsr = abilab.abiopen(str(gsr_path))
    structure = gsr.structure

    # Make file name for figure
    savedir = Path('Data')
    savedir.mkdir(exist_ok=True)
    filename = savedir / 'AlN_relaxed.cif'

    print(structure)
    print(filename)
    structure.to(filename=str(filename))

if __name__ == "__main__":
    main()
