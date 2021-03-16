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

from logging import Logger
from subprocess import Popen
from time import sleep
from typing import List, Tuple, Union

from typeguard import typechecked

from .abc import CommandABC, ProcessABC

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Process(ProcessABC):
    """
    Wrapper around a list of Popen objects (pipe).

    Mutable.
    """

    def __init__(self, procs: List[Popen], command: CommandABC):

        self._procs = procs
        self._command = command

        self._completed = False
        self._output = []
        self._errors = []
        self._status = []
        self._exception = None


    def __call__(self, returncode: bool = False) -> Union[
        Tuple[List[str], List[str], List[int], Exception],
        Tuple[List[str], List[str]],
    ]:

        self._complete()

        if returncode:
            return self._output, self._errors, self._status, self._exception

        if any((code != 0 for code in self._status)):
            raise self._exception

        return self._output, self._errors


    @property
    def running(self) -> bool:

        return all((
            proc.poll() is not None
            for proc in self._procs
        ))


    @property
    def command(self) -> CommandABC:

        return self._command


    def _complete(self):

        if self._completed:
            return

        for proc in self._procs[::-1]:  # inverse order, last process first

            out, err = proc.communicate()
            self._output.append(self._com_to_str(out))
            self._errors.append(self._com_to_str(err))
            self._status.append(int(proc.returncode))

        self._output.reverse()
        self._errors.reverse()
        self._status.reverse()
        self._exception = SystemError(
            "command failed", str(self._command), self._output, self._errors,
        )

        self._completed = True


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
    def wait_for(
        comment: str,
        procs: List[ProcessABC],
        log: Logger,
        wait: float,
        assert_sucess: bool = True,
    ):

        assert wait > 0.0

        log.info(f'Waiting for: {comment:s} ...')

        while True:
            running = len([proc for proc in procs if proc.running])
            if running == 0:
                break
            log.info(f'{running:d} out of {len(procs):d} are still running ...')
            sleep(wait)

        log.info(f'Processes exited: {comment:s}')

        if not assert_sucess:
            log.info(f'Did not assess success of processes: {comment:s}')
            return

        if all((
            all((code == 0 for code in proc(returncode = True)[2]))
            for proc in procs
        )):
            log.info(f'Processes were successful: {comment:s}')
            return

        log.error(f'At least one process failed: {comment:s}')

        for proc in procs:
            if all((code == 0 for code in proc(returncode = True)[2])):
                continue
            log.error(f'Command failed: {str(proc.command):s}')
            for idx, out, err, status, in zip(range(len(proc.command)), *proc(returncode = True)[:3]):
                if status == 0:
                    continue
                log.error(f'Command fragment {idx:d} failed. Output:')
                if len(out.strip()) > 0:
                    log.error(out.strip())
                if len(err.strip()) > 0:
                    log.error(err.strip())

        raise SystemError('A process did not exit with code 0.')
