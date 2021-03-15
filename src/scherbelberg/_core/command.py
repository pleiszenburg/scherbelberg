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

from .abc import CommandABC, SSHConfigABC

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
    def _com_to_str(com: Union[str, bytes, None]) -> str:

        if com is None:
            return ""

        if isinstance(com, bytes):
            try:
                return com.decode("utf-8")
            except:
                return repr(com)

        return com

    @staticmethod
    def _split_list(data: List, delimiter: str) -> List[List]:

        return [
            list(sub_list)
            for is_delimiter, sub_list in itertools.groupby(
                data, lambda item: item == delimiter
            )
            if not is_delimiter
        ]

    def run(
        self, returncode: bool = False
    ) -> Union[
        Tuple[List[str], List[str], List[int], Exception], Tuple[List[str], List[str]]
    ]:

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

        output, errors, status = [], [], []

        for proc in procs[::-1]:  # inverse order, last process first

            out, err = proc.communicate()
            output.append(self._com_to_str(out))
            errors.append(self._com_to_str(err))
            status.append(int(proc.returncode))

        output.reverse()
        errors.reverse()
        status.reverse()

        exception = SystemError("command failed", str(self), output, errors)

        if returncode:
            return output, errors, status, exception

        if any((code != 0 for code in status)):  # some fragment failed:
            raise exception

        return output, errors

    def on_host(self, host: SSHConfigABC) -> CommandABC:

        if host.name == "localhost":
            return self

        return type(self).from_list([
            "ssh",
            "-T",  # Disable pseudo-terminal allocation
            "-o",  # Option parameter
            "Compression=yes" if host.compression else "Compression=no",
            "-p", f'{host.port:d}',
            "-c", host.cipher,
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
