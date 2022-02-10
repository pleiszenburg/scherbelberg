![scherbelberg](docs/source/_static/logo01.png?raw=true)

# SCHERBELBERG

*/ˈʃɛʁbɛlbɛʁk/ ([German, toponym, male: "mountain of shards" in Leipzig](https://commons.wikimedia.org/wiki/Category:Rosentalh%C3%BCgel_(Leipzig)))*

<!-- [![build_master](https://github.com/pleiszenburg/scherbelberg/actions/workflows/test.yaml/badge.svg?branch=master "Build Status: master / release")](https://github.com/pleiszenburg/scherbelberg/actions/workflows/test.yaml) -->
[![docs_master](https://readthedocs.org/projects/scherbelberg/badge/?version=latest&style=flat-square "Documentation Status: master / release")](https://scherbelberg.readthedocs.io/en/latest/)
[![license](https://img.shields.io/pypi/l/scherbelberg.svg?style=flat-square "BSD")](https://github.com/pleiszenburg/scherbelberg/blob/master/LICENSE)
[![status](https://img.shields.io/pypi/status/scherbelberg.svg?style=flat-square "Project Development Status")](https://github.com/pleiszenburg/scherbelberg/issues)
[![pypi_version](https://img.shields.io/pypi/v/scherbelberg.svg?style=flat-square "Project Development Status")](https://pypi.python.org/pypi/scherbelberg)
[![conda_version](https://img.shields.io/conda/vn/conda-forge/scherbelberg.svg?style=flat-square "conda version")](https://anaconda.org/conda-forge/scherbelberg)
[![pypi_versions](https://img.shields.io/pypi/pyversions/scherbelberg.svg?style=flat-square "Available on PyPi - the Python Package Index")](https://pypi.python.org/pypi/scherbelberg)
<!-- [![chat](https://img.shields.io/matrix/zugbruecke:matrix.org.svg?style=flat-square "Matrix Chat Room")](https://matrix.to/#/#zugbruecke:matrix.org)
[![mailing_list](https://img.shields.io/badge/mailing%20list-groups.io-8cbcd1.svg?style=flat-square "Mailing List")](https://groups.io/g/zugbruecke-dev) -->

## Synopsis

`scherbelberg` provides both a CLI and an API for deploying and managing small [Dask](https://dask.org/)-based HPC clusters in the [Hetzner cloud](http://cloud.hetzner.com/). Development status *alpha*, stability *acceptable*, security also *acceptable* but implementation needs a review.

## Project's Name

Next to impressive projects like [Fugaku](https://en.wikipedia.org/wiki/Fugaku_(supercomputer)), which is named after [Mount Fuji](https://en.wikipedia.org/wiki/Mount_Fuji), the [TOP500](https://en.wikipedia.org/wiki/TOP500) are clearly missing an entry from the city of [Leipzig](https://en.wikipedia.org/wiki/Leipzig). This project is named after one of the few significant "mountains" in the city, the "Scherbelberg", also known as the "[Rosentalhügel](https://commons.wikimedia.org/wiki/Category:Rosentalh%C3%BCgel_(Leipzig))": 20 meters above the surrounding landscape and 125 meters above sea level. Starting out as a late 19th century landfill, it has since become part of a park-like landscape. As of 1975, a famously shaky steel [observation tower](https://commons.wikimedia.org/wiki/Category:Rosentalturm) with a rather [beautiful view](https://commons.wikimedia.org/wiki/Category:Views_from_Rosentalturm) is located at its top, overlooking not only the [Leipziger Auenwald](https://en.wikipedia.org/wiki/Leipzig_Riverside_Forest) forest but also the city's sewage treatment plant.

## Installation

`scherbelberg` can be installed via `conda` as follows:

```bash
conda install -c conda-forge scherbelberg
```

This package has been tested on Linux and Windows 10. It should work on most Unix-like systems. You must run a `conda` environment based entirely on recent versions of [conda-forge](https://conda-forge.org/) packages with CPython versions 3.8, 3.9 or 3.10. ``ssh`` must be installed separately as a prerequisite. A [Hetzner API token](https://docs.hetzner.cloud/#getting-started) is required. By default, `scherbelberg` expects it to be located in the `HETZNER` environment variable.

See [chapter on installation](https://scherbelberg.readthedocs.io/en/latest/installation.html) in `scherbelberg`'s documentation for further details. Also see [section on how to get started](https://scherbelberg.readthedocs.io/en/latest/gettingstarted.html) for additional steps.

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
  catalog  list data centers and available servers types
  create   create cluster
  destroy  destroy cluster
  ls       list cluster nodes
  nuke     nuke cluster
  scp      scp from/to cluster node
  ssh      ssh into cluster node
```

See [chapter on CLI](https://scherbelberg.readthedocs.io/en/latest/cli.html) in `scherbelberg`'s documentation for further details.

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
dask_client = run(c.get_client(asynchronous = False))
```

See [chapter on API](https://scherbelberg.readthedocs.io/en/latest/api.html) in `scherbelberg`'s documentation for further details.
