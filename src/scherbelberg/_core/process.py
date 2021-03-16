# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/process.py: Wrapper for Popen

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

from subprocess import Popen
from typing import List, Tuple, Union

from typeguard import typechecked

from .abc import ProcessABC

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Process(ProcessABC):
    """
    Wrapper around a list of Popen objects (pipe).

    Mutable.
    """

    def __init__(self, procs = List[Popen]):

        self._procs = procs
        self._running = True


    def __call__(self, returncode: bool = False) -> Union[
        Tuple[List[str], List[str], List[int], Exception],
        Tuple[List[str], List[str]],
    ]:

        if not self._running:
            raise SystemError('process is done')
        self._running = False

        output, errors, status = [], [], []

        for proc in self._procs[::-1]:  # inverse order, last process first

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
