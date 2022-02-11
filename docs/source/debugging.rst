:github_url:

.. _debugging:

Debugging
=========

Every :ref:`CLI <cli>` command supports the ``-l`` or ``--log_level`` option, which adjusts `log level`_ of the application. Set it to ``INFO`` (i.e. ``20``) for general information on what is happening. Set it to ``DEBUG`` (i.e. ``10``) for full debugging output, e.g. ``scherbelberg create -l 10``.

If *scherbelberg* is used via its :ref:`API <api>`, the log level can be adjusted via Python's standard library's logging module for instance as follows:

.. code:: python

    from logging import basicConfig, INFO

    basicConfig(
        format="%(name)s %(levelname)s %(asctime)-15s: %(message)s",
        level=INFO,
    )

.. note::

    The used logger is, by default, named after the cluster, i.e. its ``prefix``.

For additional insights and debugging output, run-time type checks based on `typeguard`_ can be activated by setting the ``SCHERBELBERG_DEBUG`` environment variable to ``1`` prior to running a CLI command or prior to importing *scherbelberg* in Python. As a side effect, this will also automatically set the log level to ``DEBUG`` (i.e. ``10``) if *scherbelberg* is used via the command line.

.. _log level: https://docs.python.org/3/library/logging.html#levels
.. _typeguard: https://typeguard.readthedocs.io/
