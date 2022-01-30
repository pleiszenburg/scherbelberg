.. _command:

Command
=======

The :class:`scherbelberg.Command` class describes shell commands and allows to manipulate and chain them quickly via pipes - very similar to what Python's `pathlib`_ does to paths. It uses the :class:`scherbelberg.Process` class to actually run the commands asynchronously.

.. _pathlib: https://docs.python.org/3/library/pathlib.html

The ``Command`` Class
---------------------

.. autoclass:: scherbelberg.Command
    :members:
