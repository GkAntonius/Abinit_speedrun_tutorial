This directory contains the standalone python scripts 
to follow the tutorial from the shell.

Here is the list of shell commands that you should run in each section of the notebooks.


# 1. From Task to Flow: Silicon band structure

## 1.1 Ground-state density as a single Task

    python run_si_gstate.py

## 1.2 Band structure calculation in a second, dependent Task

    python run_si_nscf.py
    python plot_ebands_1.py

## 1.3 Wrapping both Tasks in a Flow

### Build it, write it, run it

    python run_si_ebands.py
    python plot_ebands_2.py

### Build it now, Run it later

    rm -r flow_si_ebands/
    python make_si_ebands.py

    abirun.py flow_si_ebands/ scheduler

    python plot_ebands_2.py


# 2. Building your flows: GaAs convergence study

# 2.1 Convergence study

## 2.1.1 ecut convergence

    python make_gaas_convecut.py

    abirun.py flow_gaas_convecut/ scheduler

    python plot_gaas_convecut.py

## 2.1.2 k-point convergence

    python make_gaas_convkpt.py

    abirun.py flow_gaas_convkpt/ scheduler

    python plot_gaas_convkpt.py

# 2.2 Band structure

    python make_gaas_ebands.py

    abirun.py flow_gaas_ebands/ scheduler

    plot_gaas_ebands.py



# 3. Relaxation: AlN

    python make_aln_relax.py

    abirun.py flow_aln_relax/ scheduler
    
    python plot_aln_relax.py
    
    python save_aln_structure.py


# 4. Using existing flows: MgO Phonons

    python make_mgo_phonons.py

    abirun.py flow_mgo_phonons/ scheduler

    python run_mgo_anaddb.py

    plot_mgo_phonons.py
