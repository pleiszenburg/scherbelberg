# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/command.py: Command wrapper

    Copyright (C) 2021-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the BSD 3-Clause License
("License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://github.com/pleiszenburg/scherbelberg/blob/master/LICENSE
Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from asyncio import sleep
import itertools
from subprocess import Popen, PIPE
from typing import List, Tuple, Union
import shlex
from sys import platform
from time import time

from typeguard import typechecked

from .abc import CommandABC, SSHConfigABC
from .const import WAIT
from .process import Process

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Command(CommandABC):
    """
    Representing a chain of commands, connected via pipes. Immutable.

    Args:
        cmd : List of list of strings. Each inner list represents one command compatible to ``subprocess.Popen``.
    """

    def __init__(self, cmd: List[List[str]]):

        self._cmd = [fragment.copy() for fragment in cmd]

    def __repr__(self) -> str:
        """
        Interactive string representation
        """

        return "<Command>"

    def __str__(self) -> str:
        """
        String conversion
        """

        return " | ".join([shlex.join(fragment) for fragment in self._cmd])

    def __len__(self) -> int:
        """
        Number of chained commmands
        """

        return len(self._cmd)

    def __or__(self, other: CommandABC) -> CommandABC:  # pipe
        """
        Pipe
        """

        return type(self)(self.cmd + other.cmd)

    @staticmethod
    def _split_list(data: List, delimiter: str) -> List[List]:

        return [
            list(sub_list)
            for is_delimiter, sub_list in itertools.groupby(
                data, lambda item: item == delimiter
            )
            if not is_delimiter
        ]

    @staticmethod
    def _ssh_options() -> List[str]:

        dev_null = "\\\\.\\NUL" if platform.startswith("win") else "/dev/null"

        return [
            "-o",
            "StrictHostKeyChecking=no",  # TODO security
            "-o",
            f"UserKnownHostsFile={dev_null:s}",  # TODO security
            "-o",
            "BatchMode=yes",
            "-o",
            "ConnectTimeout=5",
        ]

    async def run(
        self,
        returncode: bool = False,
        timeout: Union[float, int, None] = None,
        wait: float = WAIT,
    ) -> Union[
        Tuple[List[str], List[str], List[int], Exception],
        Tuple[List[str], List[str]],
    ]:
        """
        Run command or chain of commands in a :class:`scherbelberg.Process` object.

        Args:
            returncode : If set to ``True``, returns actual return code and does not raise an exception if the command(s) failed. If set to ``False``, a failed command raises an exception and only data from standard output and standard error streams is returned.
            timeout : Total timeout in seconds.
            wait : Interval defining every how many seconds the status of the running process is being observed.
        Returns:
            A tuple, the first two elements containing data from standard output and standard error streams. If ``returncode`` is set to ``True``, the tuple has two additional entries, a list of return codes and an exception object that can be raised by the caller.
        """

        procs = []  # all processes, connected with pipes

        for index, fragment in enumerate(self._cmd):  # create & connect processes

            stdin = None if index == 0 else procs[-1].stdout  # output of last process
            proc = Popen(
                fragment,
                stdout=PIPE,
                stderr=PIPE,
                stdin=stdin,
            )
            procs.append(proc)

        process = Process(
            procs=procs,
            command=self,
        )

        start = time()
        while process.running:
            await sleep(wait)
            if timeout is not None and (time() - start) >= timeout:
                break

        return process.communicate(
            returncode=returncode,
            timeout=0.1 if timeout is not None else None,
        )

    def on_host(self, host: SSHConfigABC) -> CommandABC:
        """
        Adds a ``ssh`` prefix to the command so it can be executed on a remote host.
        Does not change the current command but returns a new one.

        Args:
            host : SSH configuration
        Returns:
            A new :class:`scherbelberg.Command` object which can be executed on the remote host.
        """

        if host.name == "localhost":
            return self

        return type(self).from_list(
            [
                "ssh",
                "-T",  # Disable pseudo-terminal allocation
                "-o",
                "Compression=yes" if host.compression else "Compression=no",
                *self._ssh_options(),
                "-p",
                f"{host.port:d}",
                "-c",
                host.cipher,
                "-i",
                host.fn_private,
                f"{host.user:s}@{host.name:s}",
                str(self),
            ]
        )

    @property
    def cmd(self) -> List[List[str]]:
        """
        List of list of strings. Each inner list represents one command compatible to ``subprocess.Popen``. This interface can not be used to change the command.
        """

        return [fragment.copy() for fragment in self._cmd]

    @classmethod
    def from_str(cls, cmd: str) -> CommandABC:
        """
        Generates a :class:`scherbelberg.Command` object from a single string containing a (shell) command.

        Args:
            cmd : Single string containing a (shell) command.
        Returns:
            New command object.
        """

        return cls(cls._split_list(shlex.split(cmd), "|"))

    @classmethod
    def from_list(cls, cmd: List[str]) -> CommandABC:
        """
        Generates a :class:`scherbelberg.Command` object from a list of strings compatible to ``subprocess.Popen``.

        Args:
            cmd : A list of strings compatible to ``subprocess.Popen``.
        Returns:
            New command object.
        """

        return cls([cmd])

    @classmethod
    def from_scp(cls, *source: str, target: str, host: SSHConfigABC) -> CommandABC:
        """
        Generates a :class:`scherbelberg.Command` object representing an ``scp`` command.
        Only supports copy operations from the local system to the remote host.

        Args:
            source : An arbitrary number of paths on the local system.
            target : Target path on the remote system.
            host : SSH configuration.
        Returns:
            New command object.
        """

        assert len(source) > 0
        assert len(target) > 0

        if platform.startswith("win"):  # Windows scp path fix
            source = [path.replace("\\\\", "/").replace("\\", "/") for path in source]

        return cls.from_list(
            [
                "scp",
                "-o",
                "Compression=yes" if host.compression else "Compression=no",
                *cls._ssh_options(),
                "-P",
                f"{host.port:d}",
                "-c",
                host.cipher,
                "-i",
                host.fn_private,
                *source,
                f"{host.user:s}@{host.name:s}:{target:s}",
            ]
        )
