:github_url:

.. _gettingstarted:

Getting Started
===============

Cluster Management via CLI
--------------------------

*scherbelberg* has an extensive :ref:`command line interface (CLI) <cli>`. A cluster can be created simply by running the ``scherbelberg create`` command. Without further options, this will set up the smallest and most simple cluster possible, one scheduler node plus one worker node:

.. code:: bash

    (env) user@computer:~> scherbelberg create
    cluster INFO 2022-01-28 14:24:33,141: Creating cloud client ...
    cluster INFO 2022-01-28 14:24:33,142: Creating ssl certificates ...
    cluster INFO 2022-01-28 14:24:35,778: Creating ssh key ...
    cluster INFO 2022-01-28 14:24:37,786: Uploading ssh key ...
    cluster INFO 2022-01-28 14:24:38,098: Getting handle on ssh key ...
    cluster INFO 2022-01-28 14:24:38,153: Creating network ...
    cluster INFO 2022-01-28 14:24:38,328: Getting handle on network ...
    cluster INFO 2022-01-28 14:24:38,408: Creating firewall ...
    cluster INFO 2022-01-28 14:24:38,508: Getting handle on firewall ...
    cluster INFO 2022-01-28 14:24:38,608: Creating nodes ...
    cluster INFO 2022-01-28 14:24:38,608: Creating node cluster-node-scheduler ...
    cluster INFO 2022-01-28 14:24:40,560: Waiting for node cluster-node-scheduler to become available ...
    cluster INFO 2022-01-28 14:24:40,739: Creating node cluster-node-worker000 ...
    cluster INFO 2022-01-28 14:24:41,709: Waiting for node cluster-node-worker000 to become available ...
    cluster INFO 2022-01-28 14:24:48,465: Attaching network to node cluster-node-scheduler ...
    cluster INFO 2022-01-28 14:24:49,034: Bootstrapping node cluster-node-scheduler ...
    cluster INFO 2022-01-28 14:24:49,034: [scheduler] [root] Waiting for SSH ...
    cluster INFO 2022-01-28 14:24:49,184: Attaching network to node cluster-node-worker000 ...
    cluster INFO 2022-01-28 14:24:49,864: Bootstrapping node cluster-node-worker000 ...
    cluster INFO 2022-01-28 14:24:49,865: [worker000] [root] Waiting for SSH ...
    cluster INFO 2022-01-28 14:24:54,046: [scheduler] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:24:54,882: [worker000] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:24:59,056: [scheduler] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:24:59,895: [worker000] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:25:01,064: [scheduler] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:25:01,905: [worker000] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:25:03,074: [scheduler] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:25:05,082: [scheduler] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:25:05,920: [worker000] [root] SSH up.
    cluster INFO 2022-01-28 14:25:05,920: [worker000] Copying root files to node ...
    cluster INFO 2022-01-28 14:25:06,927: [worker000] Running first bootstrap script ...
    cluster INFO 2022-01-28 14:25:08,091: [scheduler] [root] SSH up.
    cluster INFO 2022-01-28 14:25:08,091: [scheduler] Copying root files to node ...
    cluster INFO 2022-01-28 14:25:10,098: [scheduler] Running first bootstrap script ...
    cluster INFO 2022-01-28 14:25:49,004: [worker000] Rebooting ...
    cluster INFO 2022-01-28 14:25:49,317: [worker000] [root] Waiting for SSH ...
    cluster INFO 2022-01-28 14:25:53,328: [scheduler] Rebooting ...
    cluster INFO 2022-01-28 14:25:53,670: [scheduler] [root] Waiting for SSH ...
    cluster INFO 2022-01-28 14:25:55,431: [worker000] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:25:59,784: [scheduler] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:26:01,447: [worker000] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:26:03,456: [worker000] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:26:05,465: [worker000] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:26:05,801: [scheduler] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:26:06,473: [worker000] [root] SSH up.
    cluster INFO 2022-01-28 14:26:06,473: [worker000] Running second bootstrap script ...
    cluster INFO 2022-01-28 14:26:07,808: [scheduler] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:26:09,815: [scheduler] [root] Continuing to wait for SSH ...
    cluster INFO 2022-01-28 14:26:11,824: [scheduler] [root] SSH up.
    cluster INFO 2022-01-28 14:26:11,824: [scheduler] Running second bootstrap script ...
    cluster INFO 2022-01-28 14:27:00,573: [worker000] [clusteruser] Waiting for SSH ...
    cluster INFO 2022-01-28 14:27:01,581: [worker000] [clusteruser] SSH up.
    cluster INFO 2022-01-28 14:27:01,581: [worker000] Copying user files to node ...
    cluster INFO 2022-01-28 14:27:03,590: [worker000] Running third (user) bootstrap script ...
    cluster INFO 2022-01-28 14:27:06,883: [scheduler] [clusteruser] Waiting for SSH ...
    cluster INFO 2022-01-28 14:27:07,891: [scheduler] [clusteruser] SSH up.
    cluster INFO 2022-01-28 14:27:07,891: [scheduler] Copying user files to node ...
    cluster INFO 2022-01-28 14:27:09,900: [scheduler] Running third (user) bootstrap script ...
    cluster INFO 2022-01-28 14:29:11,100: [scheduler] Bootstrapping done.
    cluster INFO 2022-01-28 14:29:11,101: [scheduler] [clusteruser] Waiting for SSH ...
    cluster INFO 2022-01-28 14:29:11,812: [worker000] Bootstrapping done.
    cluster INFO 2022-01-28 14:29:12,107: [scheduler] [clusteruser] SSH up.
    cluster INFO 2022-01-28 14:29:12,108: [scheduler] Staring dask scheduler ...
    cluster INFO 2022-01-28 14:29:13,114: [scheduler] Dask scheduler started.
    cluster INFO 2022-01-28 14:29:13,115: [worker000] [clusteruser] Waiting for SSH ...
    cluster INFO 2022-01-28 14:29:14,122: [worker000] [clusteruser] SSH up.
    cluster INFO 2022-01-28 14:29:14,123: [worker000] Staring dask worker ...
    cluster INFO 2022-01-28 14:29:15,130: [worker000] Dask worker started.
    cluster INFO 2022-01-28 14:29:15,130: Successfully created new cluster.

.. note::

    Creating a cluster requires around 3 to 10 minutes.

Once the cluster has been created, it can be inspected at any time using the ``scherbelberg ls`` command:

.. code:: bash

    (env) user@computer:~> scherbelberg ls
    cluster INFO 2022-01-28 14:34:53,789: Creating cloud client ...
    cluster INFO 2022-01-28 14:34:53,790: Getting handle on scheduler ...
    cluster INFO 2022-01-28 14:34:54,099: Getting handles on workers ...
    cluster INFO 2022-01-28 14:34:54,273: Getting handle on firewall ...
    cluster INFO 2022-01-28 14:34:54,346: Getting handle on network ...
    cluster INFO 2022-01-28 14:34:54,418: Successfully attached to existing cluster.
    <Cluster prefix="cluster" alive=True workers=1 ipc=9753 dash=9756 nanny=9759>
    <node name=cluster-node-worker000 public=188.34.155.13 private=10.0.1.100>
    <node name=cluster-node-scheduler public=78.47.76.87 private=10.0.1.200>

            cluster-node-worker000 dash: http://188.34.155.13:9756/

            cluster-node-scheduler dash: http://78.47.76.87:9756/

Sometimes, it is necessary to log into worker nodes or the scheduler. *scherbelberg* provides a thin wrapper around ``ssh`` for quick logins. Worker nodes are accessible as follows:

.. code:: bash

    (env) user@computer:~> scherbelberg ssh worker000
    cluster INFO 2022-01-28 14:35:49,774: Creating cloud client ...
    cluster INFO 2022-01-28 14:35:49,775: Getting handle on scheduler ...
    cluster INFO 2022-01-28 14:35:49,979: Getting handles on workers ...
    cluster INFO 2022-01-28 14:35:50,157: Getting handle on firewall ...
    cluster INFO 2022-01-28 14:35:50,235: Getting handle on network ...
    cluster INFO 2022-01-28 14:35:50,319: Successfully attached to existing cluster.
    To run a command as administrator (user "root"), use "sudo <command>".
    See "man sudo_root" for details.

    (clusterenv) clusteruser@cluster-node-worker000:~$ exit
    logout
    (env) user@computer:~>

.. note::

    *scherbelberg* does not alter the system's or user's ssh configuration.

The scheduler node is accessible as follows:

.. code:: bash

    (env) user@computer:~> scherbelberg ssh scheduler
    cluster INFO 2022-01-28 14:36:23,019: Creating cloud client ...
    cluster INFO 2022-01-28 14:36:23,019: Getting handle on scheduler ...
    cluster INFO 2022-01-28 14:36:23,243: Getting handles on workers ...
    cluster INFO 2022-01-28 14:36:23,477: Getting handle on firewall ...
    cluster INFO 2022-01-28 14:36:23,543: Getting handle on network ...
    cluster INFO 2022-01-28 14:36:23,618: Successfully attached to existing cluster.
    To run a command as administrator (user "root"), use "sudo <command>".
    See "man sudo_root" for details.

    (clusterenv) clusteruser@cluster-node-scheduler:~$ exit
    logout
    (env) user@computer:~>

Once a cluster is not required anymore, it can be destroyed using the ``scherbelberg destroy`` command:

.. code:: bash

    (env) user@computer:~> scherbelberg destroy
    cluster INFO 2022-01-28 14:37:17,612: Creating cloud client ...
    cluster INFO 2022-01-28 14:37:17,612: Getting handle on scheduler ...
    cluster INFO 2022-01-28 14:37:18,377: Getting handles on workers ...
    cluster INFO 2022-01-28 14:37:18,564: Getting handle on firewall ...
    cluster INFO 2022-01-28 14:37:18,638: Getting handle on network ...
    cluster INFO 2022-01-28 14:37:18,706: Successfully attached to existing cluster.
    cluster INFO 2022-01-28 14:37:18,868: Deleting cluster-node-scheduler ...
    cluster INFO 2022-01-28 14:37:19,221: Deleting cluster-node-worker000 ...
    cluster INFO 2022-01-28 14:37:20,334: Deleting cluster-network ...
    cluster INFO 2022-01-28 14:37:20,647: Deleting cluster-key ...
    cluster INFO 2022-01-28 14:37:20,792: Deleting cluster-firewall ...
    cluster INFO 2022-01-28 14:37:20,913: Cluster cluster destroyed.
    (env) user@computer:~>

Under certain circumstances, the creation or destruction of a cluster may fail or result in an unclean state, for instance due to connectivity issues. In cases like this, it might be necessary to "nuke" the remains of the cluster before it can possibly be recreated:

.. code:: bash

    (env) user@computer:~> scherbelberg nuke
    cluster INFO 2022-01-28 15:43:19,549: Creating cloud client ...
    cluster INFO 2022-01-28 15:43:20,285: Cluster cluster nuked.
    (env) user@computer:~>

Cluster Management via API
--------------------------

Alternatively, also offers an equivalent :ref:`application programming interface (API) <api>`. First, the :class:`scherbelberg.Cluster` class needs to be imported:

.. code:: ipython

    >>>> from scherbelberg import Cluster

Based on that, one can now create a new cluster:

.. code:: ipython

    >>>> cluster = await Cluster.from_new()
    >>>> cluster
    <Cluster prefix="cluster" alive=True workers=1 ipc=9753 dash=9756 nanny=9759>

.. note::

    Most of the *scherbelberg* API is designed to run asynchronously and therefore makes use of ``async`` and ``await``. If *scherbelberg* is used in a synchronous context, asynchronous functions/methods can simply be wrapped in ``asyncio.run`` which executes them as if they were normal, blocking functions/methods:

    .. code:: ipython

        >>>> from asyncio import run
        >>>> cluster = run(Cluster.from_new())

The cluster has one scheduler and a given number of workers, one by default:

.. code:: ipython

    >>>> cluster.scheduler
    <Node name=cluster-node-scheduler public=78.47.76.87 private=10.0.1.200>
    >>>> len(cluster.workers)
    1
    >>>> cluster.workers
    [<Node name=cluster-node-worker000 public=188.34.155.13 private=10.0.1.100>]

The status of the nodes, i.e. scheduler and workers, can be for instance tested by checking their availability via ``ssh``:

.. code:: ipython

    >>>> await cluster.scheduler.ping_ssh()
    True
    >>>> await cluster.workers[0].ping_ssh()
    True

The :class:`scherbelberg.Command` and :class:`scherbelberg.SSHConfig` classes provide basic facilities for executing commands on the nodes, for instance as follows:

.. code:: ipython

    >>>> out, err = await Command.from_str('uname -a').on_host(await cluster.scheduler.get_sshconfig()).run()
    >>>> out, err
    (['Linux cluster-node-scheduler 5.4.0-96-generic #109-Ubuntu SMP Wed Jan 12 16:49:16 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux\n'],
     ["Warning: Permanently added '78.47.76.87' (ED25519) to the list of known hosts.\r\n"])

.. note::

    Because *scherbelberg* does not touch the system's ``ssh`` configuration, ``ssh`` will keep telling that it "permanently added" keys to the list of known hosts. In reality, *scherbelberg* redirects the list of known hosts to a null device, ``/dev/null`` under Unix-like systems.

At last, a cluster can quickly be destroyed as follows:

 .. code:: ipython

    >>>> await cluster.destroy()
    >>>> cluster
    <Cluster prefix="cluster" alive=False workers=0 ipc=9753 dash=9756 nanny=9759>

Similar to the CLI, it might be necessary to "nuke" the remains of a cluster which ended up in an unclean state:

.. code:: ipython

   >>>> await Cluster.nuke()

.. note::

    "Nuke" is a class method which is directly called on the :class:`scherbelberg.Cluster` class. It is likely that connecting to a broken cluster fails which prohibits the creation of a :class:`scherbelberg.Cluster` object in the first place.

Using a Cluster
---------------

The actual use of Dask requires a ``dask.distributed.Client`` object. It can be obtained from any living :class:`scherbelberg.Cluster` object as follows:

.. code:: ipython

    >>>> cluster = await Cluster.from_existing()
    >>>> client = await cluster.get_client(asynchronous = False)
    >>>> type(client)
    distributed.client.Client
    >>>> client
    <Client: 'tls://78.47.76.87:9753' processes=1 threads=1, memory=1.89 GiB>

.. note::

    Dask fully supports `running asynchronously`_. Dask's mode of operation, synchronous or asynchronous, is specified at the time of creation of the client object. *scherbelberg* will **default to asynchronous Dask client objects**.

.. _running asynchronously: http://distributed.dask.org/en/stable/asynchronous.html

Creating Powerful Clusters
--------------------------

So far, only minimal clusters have been shown for demonstration purposes. In reality, *scherbelberg* can manage much more powerful clusters. This is where the number of workers as well as the types of scheduler and workers becomes relevant. Hetzner offers a `variety of cloud servers`_ from which a potential user can pick.

.. note::

    The Dask scheduler is heavily CPU-bound and does not scale well across many cores. Anywhere from one to two cores is usually enough. Fast, dedicated vCPU cores are better.

.. note::

    Hetzner cloud serves tend to achieve a `network bandwidth`_ of around 300 to 500 Mbit/s. Larger instances might end up with more bandwidth because the underlying host has to deal with fewer instances sharing bandwidth. This has to be kept in mind when designing a cluster and ideally measured as well as monitored afterwards.

.. warning::

    Hetzner has a `per-user limit`_ specifying how many servers can be rented simultaneously at any given time. The limit can be adjusted.

As of February 2022, "ccx52" is one of the most powerful offerings in Hetzner's portfolio. It includes 32 vCPU cores and 128 GB of RAM. A cluster of 8 servers of this kind, totaling 256 vCPU cores and 1 TB of RAM, plus a matching scheduler could for instance be created as follows:

.. code:: bash

    (env) user@computer:~> scherbelberg create --workers 8 --worker ccx52 --scheduler ccx12

.. _variety of cloud servers: https://www.hetzner.com/cloud
.. _per-user limit: https://docs.hetzner.com/cloud/servers/faq#how-many-servers-can-i-create
.. _network bandwidth: https://docs.hetzner.com/cloud/technical-details/faq#what-kind-of-connection-do-the-instances-have

Multiple Clusters Simultaneously
--------------------------------

*scherbelberg* clusters are referred to by their "prefix". The name of every cluster node, virtual network switch, firewall, configuration file and user name will start with the cluster prefix. By default, it is set to "cluster". Multiple clusters can be created, managed and used side by side by using different prefixes for them. Every relevant bit of CLI and API therefore supports a prefix parameter.

In the command line, this may for instance look as follows:

.. code:: bash

    (env) user@computer:~> scherbelberg create --prefix morepower

In terms of an API call, it may look as follows:

.. code:: ipython

    >>>> cluster = await Cluster.from_existing(prefix = "morepower")
