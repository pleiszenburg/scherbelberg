# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/command.py: Command wrapper

    Copyright (C) 2021 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

import itertools
from subprocess import Popen, PIPE
from typing import List, Tuple, Union
import shlex

from typeguard import typechecked

from .abc import CommandABC, ProcessABC, SSHConfigABC
from .process import Process

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Command(CommandABC):
    """
    Immutable.
    """

    def __init__(self, cmd: List[List[str]]):

        self._cmd = [fragment.copy() for fragment in cmd]


    def __repr__(self) -> str:

        return "<Command>"


    def __str__(self) -> str:

        return " | ".join([shlex.join(fragment) for fragment in self._cmd])


    def __len__(self) -> int:

        return len(self._cmd)


    def __or__(self, other: CommandABC) -> CommandABC:  # pipe

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


    def launch(self) -> ProcessABC:

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

        return Process(
            procs = procs,
            command = self,
            )


    def run(
        self, returncode: bool = False
    ) -> Union[
        Tuple[List[str], List[str], List[int], Exception],
        Tuple[List[str], List[str]],
    ]:

        return self.launch()(returncode = returncode)


    def on_host(self, host: SSHConfigABC) -> CommandABC:

        if host.name == "localhost":
            return self

        return type(self).from_list([
            "ssh",
            "-T",  # Disable pseudo-terminal allocation
            "-o", "Compression=yes" if host.compression else "Compression=no",
            "-o", "StrictHostKeyChecking=no", # TODO security
            "-o", "UserKnownHostsFile=/dev/null", # TODO security
            "-p", f'{host.port:d}',
            "-c", host.cipher,
            "-i", host.fn_private,
            f'{host.user:s}@{host.name:s}',
            str(self),
        ])


    @property
    def cmd(self) -> List[List[str]]:

        return [fragment.copy() for fragment in self._cmd]


    @classmethod
    def from_str(cls, cmd: str) -> CommandABC:

        return cls(cls._split_list(shlex.split(cmd), "|"))


    @classmethod
    def from_list(cls, cmd: List[str]) -> CommandABC:

        return cls([cmd])


    @classmethod
    def from_scp(cls, source: str, target: str, host: SSHConfigABC) -> CommandABC:

        assert len(source) > 0
        assert len(target) > 0

        return cls.from_list([
            "scp",
            "-o", "Compression=yes" if host.compression else "Compression=no",
            "-o", "StrictHostKeyChecking=no", # TODO security
            "-o", "UserKnownHostsFile=/dev/null", # TODO security
            "-P", f'{host.port:d}',
            "-c", host.cipher,
            "-i", host.fn_private,
            source,
            f'{host.user:s}@{host.name:s}:{target:s}',
        ])
