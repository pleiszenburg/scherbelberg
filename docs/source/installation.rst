:github_url:

.. _installation:

Installation
============

System Requirements
-------------------

*scherbelberg* has been **tested on Linux and Windows** 10. It is likely to work on most Unix-like systems. It is **built on top of conda-forge**.

Quick Install Guide
-------------------

Prerequisite: ``ssh``
~~~~~~~~~~~~~~~~~~~~~

``ssh``, ``scp`` and ``ssh-keygen`` are assumed to be present on the system via ``openssh``.

.. warning::

    Although ``openssh`` is a definitive requirement of *scherbelberg*, the *scherbelberg* package does not specify this dependency explicitly. This is due to vastly different installation methods across different operating systems.

On **Linux**, ``openssh`` can usually be installed best via the operating system's package manager.

By default, **Mac OS X** ships its own version of ``openssh`` as part of the operating system.

Under both **Linux** and **Mac OS X**, a current version of ``openssh`` is also available via ``conda-forge``:

.. code:: bash

    conda install -c conda-forge openssh

.. note::

    One can determine the current ``openssh`` binaries via the ``which`` command:

    .. code:: bash

        which ssh
        which scp
        which ssh-keygen

On **Windows** 10 or greater, ``openssh`` is available as an optional operating system feature and `can be installed via Windows settings`_. The Windows Subsystem for Linux (WSL) or Putty are not required.

.. _can be installed via Windows settings: https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse

Prerequisite: Hetzner Cloud API Token
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*scherbelberg* is built around the the `Hetzner cloud API`_. An API token can be acquired via the `Hetzner cloud console`_.

.. warning::

    Cloud resources might be relatively cheap, but they are not for free. The "end user" remains the sole responsible person for every action taken and needs to pay for rented resources him- or herself. *scherbelberg* merely assists in the process of renting and configuring 3rd-party commercial cloud resources. The authors of *scherbelberg* are neither affiliated nor otherwise related to the Hetzner company. With respect to questions of liability, *scherbelberg* is `licensed under the BSD 3-Clause License`_.

Once an API token has been acquired, *scherbelberg* expects it in an environment variable named ``HETZNER``. Within a ``bash`` session, it can be set as follows:

.. code:: bash

    export HETZNER="xyz123"

Alternatively, it might be a good idea to add this variable to the target conda environment:

.. code:: bash

    conda env config vars set HETZNER="xyz123"

.. _Hetzner cloud API: https://docs.hetzner.cloud/#getting-started
.. _Hetzner cloud console: https://accounts.hetzner.com/login
.. _licensed under the BSD 3-Clause License: https://github.com/pleiszenburg/scherbelberg/blob/master/LICENSE

Install *scherbelberg* via ``conda``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*scherbelberg* heavily relies on the ``conda-forge`` package ecosystem the ``conda`` / ``mamba`` as the package manager. This method is therefore the primary method of installing this package:

.. code:: bash

    conda install -c conda-forge scherbelberg

Install *scherbelberg* via ``pip``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For development purposes, *scherbelberg* can be installed via ``pip``. This method is not recommended for production setups.

The latest version can always be installed from the `Python package index`_:

.. code:: bash

    pip install scherbelberg

Alternatively, the latest development version can be installed from Github:

.. code:: bash

    pip install git+https://github.com/pleiszenburg/scherbelberg.git@develop

.. _Python package index: Python package index

Validate Installation
~~~~~~~~~~~~~~~~~~~~~

The fastest way to test the installation is to create, view and destroy a minimal default cluster (one scheduler node, one worker node, smallest possible compute instances):

.. code:: bash

    scherbelberg create
    scherbelberg ls
    scherbelberg destroy

Beyond that, all the steps described in :ref:`getting started <gettingstarted>` should work right out of the box.
