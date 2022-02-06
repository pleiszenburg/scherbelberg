:github_url:

.. _about:

.. index::
    single: synopsis
    single: motivation
    single: implementation
    single: use cases

About ``scherbelberg``
======================

.. _synopsis:

Synopsis
--------

*scherbelberg* provides both a :ref:`command line interface (CLI) <cli>` and a :ref:`Python application programming interface (API) <api>` for deploying and managing small `Dask`_-based HPC `clusters`_ in the `Hetzner cloud`_.

.. warning::

    Development status alpha, stability acceptable, :ref:`security <security>` also acceptable but implementation needs a review.

.. _Hetzner cloud: https://www.hetzner.com/cloud
.. _Dask: https://dask.org/
.. _clusters: https://en.wikipedia.org/wiki/Computer_cluster

.. _projectname:

Project's Name
--------------

Next to impressive projects like `Fugaku`_, which is named after `Mount Fuji`_, the `TOP500`_ are clearly missing an entry from the city of `Leipzig`_. This project is named after one of the few significant "mountains" in the city, the "Scherbelberg", also known as the "`Rosentalhügel`_": 20 meters above the surrounding landscape and 125 meters above sea level. Starting out as a late 19th century landfill, it has since become part of a park-like landscape. As of 1975, a famously shaky steel `observation tower`_ with a rather `beautiful view`_ is located at its top, overlooking not only the `Leipziger Auenwald`_ forest but also the city's sewage treatment plant.

.. _Fugaku: https://en.wikipedia.org/wiki/Fugaku_(supercomputer)
.. _Mount Fuji: https://en.wikipedia.org/wiki/Mount_Fuji
.. _TOP500: https://en.wikipedia.org/wiki/TOP500
.. _Leipzig: https://en.wikipedia.org/wiki/Leipzig
.. _Rosentalhügel: https://commons.wikimedia.org/wiki/Category:Rosentalh%C3%BCgel_(Leipzig)
.. _observation tower: https://commons.wikimedia.org/wiki/Category:Rosentalturm
.. _beautiful view: https://commons.wikimedia.org/wiki/Category:Views_from_Rosentalturm
.. _Leipziger Auenwald: https://en.wikipedia.org/wiki/Leipzig_Riverside_Forest

.. _motivation:

Motivation
----------

While Dask is wonderful for automating large, parallel, distributed computations, it can not solve the problem of its own deployment onto computer clusters. Instead, Dask plays nicely with established tools in the arena such as `slurm`_. Deploying Dask onto a custom cluster therefore requires a fair bit of time, background knowledge and technical skills in computer & network administration.

One of the really appealing features of Dask is that it enables users to exploit huge quantities of cloud compute resources really efficiently. Cloud compute instances can usually be rented on a per-hour basis, making them an interesting target for sizable, short-lived, on-demand clusters. For cloud deployments like this, there is the Dask-related `cloud provider package`_, which surprisingly does not solve the entire problem of deployment. At the time of *scherbelberg*'s creation, it was both rather inflexible and lacking support for the Hetzner cloud. Companies like `Coiled`_, which is also the primary developer of Dask, have filled this niche with polished, web-front-end services (and equally polished APIs) for creating clusters on clouds, which effectively makes them resellers of cloud resources. *scherbelberg* aims at eliminating the resellers from the equation while trying to provide a minimal, independent, self-contained, yet fully operational solution.

.. note::

    The idea is to be able to build tools quickly and easily on top of *scherbelberg*. The `nahleberg`_ project aims at using *scherbelberg* to load computations from within `QGIS`_ off to on-demand Dask cluster from within QGIS' GUI - without the user having to write a single line of code.

.. _cloud provider package: https://cloudprovider.dask.org/en/latest/
.. _slurm: https://slurm.schedmd.com/documentation.html
.. _Coiled: https://coiled.io/
.. _nahleberg: https://github.com/pleiszenburg/nahleberg
.. _QGIS: https://www.qgis.org/

.. _implementation:

Implementation
--------------

*scherbelberg* creates clusters on the Hetzner cloud quickly and completely from scratch without any prerequisites on the cloud's side. No pre-configured operating system, virtual machine or docker images are required. *scherbelberg* simply connects to the Hetzner cloud via its `REST API`_, creates the required number and kind of compute instances based on the latest `Ubuntu LTS`_ release, networks as well as secures the compute instances and deploys `mambaforge`_ onto them. Depending on the size of the cluster, creating an entire cluster from scratch with a single command or single API call requires anywhere from two to ten minutes. Destroying a cluster is done in under ten seconds. In many ways, *scherbelberg* is a quick and dirty bare-bones solution. It heavily relies on ``ssh`` and the systems' shell. It does not use any higher-end tools for mass-administration of computers such as `Chef`_ or `Ansible`_.

.. note::

    *scherbelberg*'s' primary objective is to provide a stack of Dask, `conda-forge`_ and Ubuntu as simple and cleanly as possible.

.. note::

    *scherbelberg* is designed as an **asynchronous** package using `asyncio`_.

.. _mambaforge: https://github.com/conda-forge/miniforge#mambaforge
.. _REST API: https://docs.hetzner.cloud/
.. _Ubuntu LTS: https://ubuntu.com/blog/what-is-an-ubuntu-lts-release
.. _Chef: https://www.chef.io/
.. _Ansible: https://www.ansible.com/
.. _conda-forge: https://conda-forge.org/
.. _asyncio: https://docs.python.org/3/library/asyncio.html

.. _usecases:

Use Cases
---------

Anything that Dask can be used for: Parallel & distributed computations, distributed memory, all on demand. In many cases, high-performant computational resources are only needed for short periods of time. In those cases, it might not be worth spending a lot of money on matching hardware. Being able to quickly create and destroy custom-configured computer clusters enables a different, very interesting kind of thinking.
