# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/sshconfig.py: SSH configuration

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

from typing import Union

from typeguard import typechecked

from .abc import SSHConfigABC

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class SSHConfig(SSHConfigABC):
    """
    Holds configuration for an SSH connection. Immutable.

    Args:
        name : Domain name or IP of remote system.
        user : Remote user name.
        fn_private : Location of private SSH key.
        port : SSH port on remote system.
        compression : Turns SSH compression on or off.
        cipher : Specifies cipher for SSH connection.
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

    def __repr__(self) -> str:
        """
        Interactive string representation
        """

        return f"<SSHConfig {self._user}@{self._name:s}:{self._port:d} compression={'yes' if self._compression else 'no':s} cipher={self._cipher:s}>"

    def new(
        self,
        name: Union[str, None],
        user: Union[str, None],
        fn_private: Union[str, None],
        port: Union[int, None],
        compression: Union[bool, None],
        cipher: Union[str, None],
    ) -> SSHConfigABC:
        """
        Generate a new SSH configuration from present object by changing individual parameters.

        Args:
            name : Domain name or IP of remote system.
            user : Remote user name.
            fn_private : Location of private SSH key.
            port : SSH port on remote system.
            compression : Turns SSH compression on or off.
            cipher : Specifies cipher for SSH connection.
        Returns:
            New SSH configuration object.
        """

        return type(self)(
            name=self._name if name is None else name,
            user=self._user if user is None else user,
            fn_private=self._fn_private if fn_private is None else fn_private,
            port=self._port if port is None else port,
            compression=self._compression if compression is None else compression,
            cipher=self._cipher if cipher is None else cipher,
        )

    @property
    def name(self) -> str:
        """
        Domain name or IP of remote system
        """

        return self._name

    @property
    def user(self) -> str:
        """
        Remote user name
        """

        return self._user

    @property
    def fn_private(self) -> str:
        """
        Location of private SSH key
        """

        return self._fn_private

    @property
    def port(self) -> int:
        """
        SSH port on remote system
        """

        return self._port

    @property
    def compression(self) -> bool:
        """
        Turns SSH compression on or off
        """

        return self._compression

    @property
    def cipher(self) -> str:
        """
        Specifies cipher for SSH connection
        """

        return self._cipher
