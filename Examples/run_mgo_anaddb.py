#!/usr/bin/env python
"""
Companion to `2-Existing_flows.ipynb`, section 2.4 (phonons) -- the anaddb
post-processing step.

Builds an `AnaddbInput` (`workshop_lib.get_anaddb_input()`) that
Fourier-interpolates the dynamical matrix from
`flow_mgo_phonons/w1/outdata/out_DDB` (the output of `make_mgo_phonons.py`)
onto a dense q-mesh (for the phonon DOS) and along a high-symmetry q-path
(for the phonon band structure), and runs it as a standalone `AnaddbTask`
-- no `Flow`, no `Work`, same idea as the Task examples in
`1-Task_to_flow.ipynb`. Results are written to `task_mgo_anaddb/` --
`plot_mgo_phonons.py` reads them from there.

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
MGO_CIF = STRUCTURE_DIR / 'mp-1265_MgO.cif'


def get_anaddb_input():

    structure = Structure.from_file(str(MGO_CIF))
    inp = abilab.AnaddbInput.phbands_and_dos(
        structure,
        ngqpt=[2,2,2],
        ndivsm=40,
        line_density=None,
        nqsmall=10,
        qppa=None,
        q1shft=(0, 0, 0),
        qptbounds=None,
        asr=2,
        chneut=1,
        dipdip=1,
        dipquad=0,
        quadquad=0,
        dos_method="tetra",
        lo_to_splitting="automatic",
        with_ifc=False,
        anaddb_kwargs={},
        spell_check=False)

    return inp


def setup_task_manager(task, mpi_procs=4, omp_threads=1, timelimit_hour=2.0):
    """Same as setup_manager(), for a standalone Task instead of a Flow."""
    manager = abilab.TaskManager.from_user_config()
    manager = manager.new_with_fixed_mpi_omp(mpi_procs=mpi_procs, omp_threads=omp_threads)
    manager.qadapter.set_timelimit(3600 * timelimit_hour)
    task.set_manager(manager)
    return task


def main():
    workdir = Path(__file__).name.replace(".py", "").replace("run_", "task_")
    ddb_path = SCRIPT_DIR / 'flow_mgo_phonons' / 'w1' / 'outdata' / 'out_DDB'

    # Make Anaddb task
    inp = get_anaddb_input()
    task = flowtk.AnaddbTask(inp, workdir=workdir, ddb_node=str(ddb_path))
    task = setup_task_manager(task, mpi_procs=1)

    # Remove a previous run, if it exists.
    if Path(workdir).exists():
        print(f'Removing existing directory: {workdir}/')
        task.rmtree()

    # Write files and run the task
    task.build()
    task.make_links()
    task.start_and_wait()
    print(task.check_status())

if __name__ == "__main__":
    main()
