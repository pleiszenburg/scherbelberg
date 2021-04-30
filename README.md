# SCHERBELBERG

`scherbelberg` provides both a CLI interface and a library for deploying and managing small [Dask](https://dask.org/)-based HPC clusters in the [Hetzner cloud](http://cloud.hetzner.com/). Development status *alpha*, stability *acceptable*, security at this point *questionable* at best.

## Project's name

Next to impressive projects like [Fugaku](https://en.wikipedia.org/wiki/Fugaku_(supercomputer)), which is named after [Mount Fuji](https://en.wikipedia.org/wiki/Mount_Fuji), the [TOP500](https://en.wikipedia.org/wiki/TOP500) are clearly missing an entry from the city of [Leipzig](https://en.wikipedia.org/wiki/Leipzig). This project is named after one of the few significant "mountains" in the city, the "Scherbelberg", also known as the "[Rosentalhügel](https://commons.wikimedia.org/wiki/Category:Rosentalh%C3%BCgel_(Leipzig))" (20 meters above the surrounding landscape and 125 meters above sea level). Starting out as a late 19th century landfill, it has since become part of a park-like landscape. As of 1975, a famously shaky steel [observation tower](https://commons.wikimedia.org/wiki/Category:Rosentalturm) with a rather [beautiful view](https://commons.wikimedia.org/wiki/Category:Views_from_Rosentalturm) is located at its top, overlooking not only the [Leipziger Auenwald](https://en.wikipedia.org/wiki/Leipzig_Riverside_Forest) forest but also the city's sewage treatment plant.

## Installation

This package has been tested on Linux. It is likely to work on other Unix-like systems. It is unlikely to work on Windows.

Prerequisites:

- `ssh`
- `scp`
- `ssh-keygen`
- `git`

You must run a `conda` environment based entirely on [conda-forge](https://conda-forge.org/) with CPython version 3.8 and `dask` present. Once this environment has been created, configured and activated, you can install `scherbelberg` as follows:

`pip install git+https://github.com/pleiszenburg/scherbelberg.git@master`

`scherbelberg` will create equivalent `conda` environments on every cluster node. Although `scherbelberg` heavily relies on `ssh`, it will **NOT** alter your system's `ssh` configuration.

For running any of the `scherbelberg` commands or routines, a [Hetzner API token](https://docs.hetzner.cloud/#getting-started) is required. `scherbelberg` by default expects it to be located in the `HETZNER` environment variable.

## CLI

Similar to `git`, the CLI is divided into sub-commands. They all come with their own parameters. Information on the latter can be found by using the `--help` option.

```
~> scherbelberg --help
Usage: scherbelberg [OPTIONS] COMMAND [ARGS]...

  HPC cluster deployment and management for the Hetzner Cloud

Options:
  --version
  --help     Show this message and exit.

Commands:
  create   create cluster
  destroy  destroy cluster
  ls       list cluster members
  ssh      ssh into cluster member
```

## API

`scherbelberg` uses `asyncio`. A cluster can basically be created and destroyed, with or without `asyncio`:

```python
from asyncio import run
from scherbelberg import Cluster

c = await Cluster.from_new(**kwargs)
# or
c = run(Cluster.from_new(**kwargs))

await c.destroy()
# or
run(c.destroy())
```

Access to an earlier established cluster can also be gained:

```python
from asyncio import run
from scherbelberg import Cluster

c = await Cluster.from_existing(**kwargs)
# or
c = run(Cluster.from_existing(**kwargs))
```

Once the cluster has been created or gained access to, one can simply request an initialized Dask client object:

```python
dask_client = await c.get_client()
# or
dask_client = run(c.get_client())
```
