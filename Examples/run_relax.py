#!/usr/bin/env python
r"""
Relaxation Flow
===============

This script shows how to perform a structural relaxation in two steps:

    1) Relaxation of atomic positions with unit cell parameters fixed.
    2) Full relaxation (atoms + cell) with the initial configuration read from step 1)
"""
from __future__ import division, print_function, unicode_literals, absolute_import

import os
import sys
import abipy.data as abidata
import abipy.abilab as abilab
import abipy.flowtk as flowtk


from myfiles import structure_dir, pseudo_dir #, find_structure, find_pseudos


def build_flow(options):
    # Working directory (default is the name of the script with '.py' removed and "run_" replaced by "flow_")
    if not options.workdir:
        options.workdir = os.path.basename(__file__).replace(".py", "").replace("run_", "flow_")

    #pseudos = data.pseudos("14si.pspnc", "6c.pspnc")
    pseudos = [ os.path.join(pseudo_dir, psp)  for psp in ['Al.psp8']]
    structure = abilab.Structure.from_file(structure_dir + '/Al_mp-134_primitive.json')

    # Initialize the input
    relax_inp = abilab.AbinitInput(structure, pseudos=pseudos)

    # Set variables
    relax_inp.set_vars(
        ecut=6.,
        paral_kgb=1,
        iomode=3,
        # Relaxation part
        ionmov=2,
        optcell=1,
        strfact=100,
        ecutsm=0.5,       # Important!
        dilatmx=1.15,     # Important!
        #toldff=1e-6,
        tolvrs=1e-6,
        tolmxf=1e-5,
        ntime=100,
        occopt=3,
    )

    # K-points sampling
    #shiftk=[
    #    [0.5,0.5,0.5],
    #    [0.5,0.0,0.0],
    #    [0.0,0.5,0.0],
    #    [0.0,0.0,0.5]
    #]
    shiftk = 3 * [0.0]
    relax_inp.set_kmesh(ngkpt=[4, 4, 4], shiftk=shiftk)

    # Initialize the flow
    flow = flowtk.Flow(options.workdir, manager=options.manager)

    # Register the task.
    flow.register_relax_task(relax_inp)

    return flow


@flowtk.flow_main
def main(options):
    return build_flow(options)


if __name__ == "__main__":
    sys.exit(main())
