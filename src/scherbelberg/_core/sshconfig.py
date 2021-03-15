# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/sshconfig.py: SSH configuration

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

from typeguard import typechecked

from .abc import SSHConfigABC

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class SSHConfig(SSHConfigABC):
    """
    Holds informaton on an SSH connection.

    Immutable.
    """

    def __init__(
        self,
        name: str,
        user: str,
        port: int = 22,
        compression: bool = True,
        cipher: str = "aes256-gcm@openssh.com",
    ):

        assert len(name) > 0
        assert len(user) > 0
        assert port > 0
        assert len(cipher) > 0

        self._name = name
        self._user = user
        self._port = port
        self._compression = compression
        self._cipher = cipher


    @property
    def name(self) -> str:

        return self._name


    @property
    def user(self) -> str:

        return self._user


    @property
    def port(self) -> int:

        return self._port


    @property
    def compression(self) -> bool:

        return self._compression


    @property
    def cipher(self) -> str:

        return self._cipher
