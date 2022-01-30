# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/process.py: Wrapper for Popen

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

from subprocess import Popen, TimeoutExpired
from typing import List, Tuple, Union

from typeguard import typechecked

from .abc import CommandABC, ProcessABC

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Process(ProcessABC):
    """
    Wrapper around a list of ``subprocess.Popen`` objects, managing their life-cycle. Mutable.

    Args:
        procs : A list of ``subprocess.Popen`` objects linked via pipes.
        command : The source :class:`scherbelberg.Command` object.
    """

    def __init__(self, procs: List[Popen], command: CommandABC):

        self._procs = procs
        self._command = command

        self._completed = False
        self._output = []
        self._errors = []
        self._status = []
        self._exception = None

    def __repr__(self) -> str:
        """
        Interactive string representation
        """

        return "<Process>"

    def communicate(
        self,
        returncode: bool = False,
        timeout: Union[float, int, None] = None,
    ) -> Union[
        Tuple[List[str], List[str], List[int], Exception],
        Tuple[List[str], List[str]],
    ]:
        """
        Run process or chain of processes.

        Args:
            returncode : If set to ``True``, returns actual return code and does not raise an exception if the process(es) failed. If set to ``False``, a failed process raises an exception and only data from standard output and standard error streams is returned.
            timeout : Total timeout in seconds.
        Returns:
            A tuple, the first two elements containing data from standard output and standard error streams. If ``returncode`` is set to ``True``, the tuple has two additional entries, a list of return codes and an exception object that can be raised by the caller.
        """

        self._complete(timeout=timeout)

        if returncode:
            return self._output, self._errors, self._status, self._exception

        if any((code != 0 for code in self._status)):
            raise self._exception

        return self._output, self._errors

    @property
    def running(self) -> bool:
        """
        Is any of the processes in the list of ``subprocess.Popen`` objects still running?
        """

        return any((proc.poll() is None for proc in self._procs))

    def _complete(
        self,
        timeout: Union[float, int, None] = None,
    ):

        if self._completed:
            return

        for proc in self._procs[::-1]:  # inverse order, last process first

            try:
                out, err = proc.communicate(timeout=timeout)
            except TimeoutExpired:
                proc.kill()
                out, err = proc.communicate()

            self._output.append(self._com_to_str(out))
            self._errors.append(self._com_to_str(err))
            self._status.append(int(proc.returncode))

        self._output.reverse()
        self._errors.reverse()
        self._status.reverse()
        self._exception = SystemError(
            "command failed",
            str(self._command),
            self._output,
            self._errors,
        )

        self._completed = True

    @staticmethod
    def _com_to_str(com: Union[str, bytes, None]) -> str:

        if com is None:
            return ""

        if isinstance(com, bytes):
            try:
                return com.decode("utf-8")
            except UnicodeDecodeError:
                return repr(com)

        return com
