.. _process:

Process
=======

The :class:`scherbelberg.Process` class asynchronously executes a list `Popen`_ objects liked via pipes. It is used by the :class:`scherbelberg.Command` class for actually running commands. In many ways, :class:`scherbelberg.Process` is a more targeted and sophisticated variation on the `asyncio subprocess implementation`_.

.. _Popen: https://docs.python.org/3/library/subprocess.html#subprocess.Popen
.. _asyncio subprocess implementation: https://docs.python.org/3/library/asyncio-subprocess.html

The ``Process`` Class
---------------------

.. autoclass:: scherbelberg.Process
    :members:
