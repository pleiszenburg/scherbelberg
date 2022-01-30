:github_url:

.. _security:

Security
========

The package's security can be described as "acceptable" but implementation needs a review.

.. warning::

    Do not trust a *scherbelberg* cluster unless you know what you are doing.

Configuration is performed via ``ssh``. *scherbelberg* creates one single 4k RSA key-pair per cluster. The operating system's ssh configuration remains untouched. Once the cluster has been configured, cluster nodes will only allow logins via public key authentication on an unprivileged user account. However, the unprivileged user accounts can run ``sudo`` without password.

Further communication between the user's computer as well as the cluster nodes is secured via TLS/SSL. For this purpose, *scherbelberg* creates one certificate authority (CA) as well as one TLS/SSL certificate per cluster.

Dask worker nodes expose an dashboard via insecure HTTP - no TLS/SSL. This dashboard will be exposed on the internet on a customizable, non-standard port.
