.. _cluster:

Cluster
=======

:class:`scherbelberg.Cluster` objects define Dask clusters and represent the core functionality of *scherbelberg*. The class can be used to create new clusters as well as to attach to existing ones and to destroy them. It generates matching `Dask Client`_ objects.

.. _Dask Client: http://distributed.dask.org/en/stable/api.html#distributed.Client

The ``Cluster`` Class
---------------------

.. autoclass:: scherbelberg.Cluster
    :members:
