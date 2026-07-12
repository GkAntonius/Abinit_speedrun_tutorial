#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.4 (phonons) -- plotting.

Plots the phonon band structure from `task_mgo_anaddb/`, the output of
`run_mgo_anaddb.py`. Several alternative plots (phonon DOS, projected DOS,
colored/matched bands, harmonic thermodynamics, ...) are left commented
out below as a starting point -- uncomment whichever you need.

Usage
-----
    python plot_mgo_phonons.py
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
    workdir = SCRIPT_DIR / 'task_mgo_anaddb'
    out_anaddb_path = workdir / 'outdata' / 'out_anaddb.nc'
    phbst_path = workdir / 'outdata' / 'out_PHBST.nc'
    phdos_path = workdir / 'outdata' / 'out_PHDOS.nc'

    plotdir = Path('Plots')
    plotdir.mkdir(exist_ok=True)
    prefix = plotdir / Path(__file__).name.replace('plot_', '').replace('.py', '.png')

    with abilab.abiopen(str(phbst_path)) as phbst_file:
        phbands = phbst_file.phbands

    with abilab.abiopen(str(phdos_path)) as phdos_file:
        phdos = phdos_file.phdos
        #phbands.read_non_anal_from_file(str(out_anaddb_path))

    #fig = phbands.plot_with_phdos(phdos, units="mev", show=False); fig.savefig(str(prefix) + '_phbs_dos.png', dpi=200)
    #fig = phbands.plot_colored_matched(units="mev", show=False); fig.savefig(str(prefix) + '_phbs_colored.png', dpi=200)
    fig = phbands.plot(units="mev", color='b', show=False)
    ax = fig.gca()
    ax.set_ylim(0, 80)
    fig.savefig(str(prefix) + '_phbands.png', dpi=200)

if __name__ == "__main__":
    main()
