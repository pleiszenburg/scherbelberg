.. _cluster:

Clusters
========

:class:`scherbelberg.Cluster` objects define Dask clusters. The class can be used to create new clusters but also to attach to existing ones. It generates matching `Dask Client`_ objects.

.. _Dask Client: http://distributed.dask.org/en/stable/api.html#distributed.Client

The ``Cluster`` Class
---------------------

.. autoclass:: scherbelberg.Cluster
    :members:
