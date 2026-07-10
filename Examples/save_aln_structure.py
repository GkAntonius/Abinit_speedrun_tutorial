#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.2 (relaxation).

Opens `flow_aln_relax/`, the output of `make_aln_relax.py`, and saves the
relaxed AlN structure (atomic positions and cell) to a `.cif` file --
useful if you want to reuse the relaxed geometry as the input structure of
a later calculation (e.g. a band structure or phonon flow at the relaxed
volume, instead of the experimental one).

Usage
-----
    python save_aln_structure.py
"""
from pathlib import Path

import abipy.abilab as abilab
import abipy.flowtk as flowtk

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

    # Make file name for the relaxed structure
    savedir = Path('Data')
    savedir.mkdir(exist_ok=True)
    filename = savedir / 'AlN_relaxed.cif'

    print(structure)
    print(filename)
    structure.to(filename=str(filename))

if __name__ == "__main__":
    main()
