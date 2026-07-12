#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.4 (phonons) -- the anaddb
post-processing step.

Opens `flow_mgo_phonons/w1/outdata/out_DDB`, the output of
`make_mgo_phonons.py`, and calls `anaget_phbst_and_phdos_files` to
Fourier-interpolate the dynamical matrix onto a dense q-mesh (for the
phonon DOS) and along a high-symmetry q-path (for the phonon band
structure). Results are written to `task_mgo_anaddb/` -- `plot_mgo_phonons.py`
reads them from there.

Usage
-----
    python run_mgo_anaddb.py
"""
from pathlib import Path

import abipy.abilab as abilab
import abipy.flowtk as flowtk
from abipy.abilab import Structure

# This script is meant to be copied -- together with the rest of this
# Tutorial/ directory -- into your own work directory. Data/Pseudos and
# Data/Structures are located relative to *this file*.
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Data"
PSEUDO_DIR = DATA_DIR / "Pseudos"
STRUCTURE_DIR = DATA_DIR / "Structures"


def main():
    ddb_path = SCRIPT_DIR / 'flow_mgo_phonons' / 'w1' / 'outdata' / 'out_DDB'
    workdir = SCRIPT_DIR / 'task_mgo_anaddb'

    with abilab.abiopen(str(ddb_path)) as ddb:
        phbst_file, phdos_file = ddb.anaget_phbst_and_phdos_files(
            workdir=str(workdir),
            nqsmall=10,
            ndivsm=40,
            asr=2,
            chneut=1,
            dipdip=1,
            dos_method='tetra',
            lo_to_splitting='automatic',
            mpi_procs=1,
            verbose=True)

if __name__ == "__main__":
    main()
