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

from typing import Union

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
        fn_private: str,
        port: int = 22,
        compression: bool = True,
        cipher: str = "aes256-gcm@openssh.com",
    ):

        assert len(name) > 0
        assert len(user) > 0
        assert len(fn_private) > 0
        assert port > 0
        assert len(cipher) > 0

        self._name = name
        self._user = user
        self._fn_private = fn_private
        self._port = port
        self._compression = compression
        self._cipher = cipher


    def new(
        self,
        name: Union[str, None],
        user: Union[str, None],
        fn_private: Union[str, None],
        port: Union[int, None],
        compression: Union[bool, None],
        cipher: Union[str, None],
    ) -> SSHConfigABC:

        return type(self)(
            name = self._name if name is None else name,
            user = self._user if user is None else user,
            fn_private = self._fn_private if fn_private is None else fn_private,
            port = self._port if port is None else port,
            compression = self._compression if compression is None else compression,
            cipher = self._cipher if cipher is None else cipher,
        )


    @property
    def name(self) -> str:

        return self._name


    @property
    def user(self) -> str:

        return self._user


    @property
    def fn_private(self) -> str:

        return self._fn_private


    @property
    def port(self) -> int:

        return self._port


    @property
    def compression(self) -> bool:

        return self._compression


    @property
    def cipher(self) -> str:

        return self._cipher
