# Installation

This folder contains everything needed to set up your environment on the
CEMDI tutorial cluster (`cemdi.calculquebec.cloud`).

**Quick start:** from a terminal on the cluster (SSH session or JupyterLab
terminal), run:

```
bash ../setup_environment.sh
```

(from `Tutorial/Installation/`; see `Tutorial/setup_environment.sh` for what
it does). It will:

1. Create `~/.abinit/abipy/` and copy ` abinit-config/default/abipy/manager.yml` and
   ` abinit-config/default/abipy/scheduler.yml` there -- this tells AbiPy how to launch
   Abinit runs on this cluster (how many cores, which queue, etc.).
2. Check that the `abinit` executable is on your `$PATH` (loading the
   `abinit` module if needed).
3. Check that the `abipy` Python package is importable. If you are working
   in JupyterLab, it already is. If you connected over plain SSH, the
   script creates a virtual environment and installs `abipy` from the
   cluster's local wheelhouse (`pip install --no-index abipy`), per the
   instructions from the CEMDI organizers.

## Manual setup

If you'd rather do it by hand:

```
mkdir -p ~/.abinit/abipy
cp abinit-config/default/abipy/manager.yml ~/.abinit/abipy/
cp  abinit-config/default/abipy/scheduler.yml ~/.abinit/abipy/
```

Then check your installation with:

```
abicheck.py
```

## About `manager.yml` / `scheduler.yml`

These are the same two files used throughout the tutorial and in
`AbipyExamples`, just resized for the resources allocated per student on
this cluster (8 CPU cores, interactive/shell execution rather than a batch
queue -- see the comments in `abinit/abipy/manager.yml`). If the cluster
turns out to require submitting through Slurm instead, that file has a
pointer to the Slurm-based config used for the Rorqual cluster as a
starting point for adapting it.
