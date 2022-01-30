# -*- coding: utf-8 -*-

"""

SCHERBELBERG
HPC cluster deployment and management for the Hetzner Cloud

https://github.com/pleiszenburg/scherbelberg

    src/scherbelberg/_core/ssl.py: Creating CAs and SSL keys

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

from datetime import datetime, timedelta
from typing import Tuple

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
async def create_ca(
    prefix: str,
    valid_days: int = 365 * 2,
) -> Tuple[rsa.RSAPrivateKey, x509.Certificate]:

    assert valid_days > 0
    assert len(prefix) > 0

    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "GL"),  # Greenland - why not?
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, f"{prefix:s} province"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, f"{prefix:s} locality"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, f"{prefix:s} organization"),
            x509.NameAttribute(NameOID.COMMON_NAME, f"{prefix:s} CA"),
        ]
    )
    issuer = subject  # identical

    key = rsa.generate_private_key(
        public_exponent=65537, key_size=4096, backend=default_backend()
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(days=1))  # HACK
        .not_valid_after(datetime.utcnow() + timedelta(days=valid_days))
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,  # ?
        )
        .sign(key, hashes.SHA256(), default_backend())  # self sign
    )

    return key, cert


@typechecked
async def create_signed_cert(
    ca_key: rsa.RSAPrivateKey,
    ca_cert: x509.Certificate,
    prefix: str,
    valid_days: int = 365 * 2,
) -> Tuple[rsa.RSAPrivateKey, x509.Certificate]:

    assert valid_days > 0
    assert len(prefix) > 0

    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "GL"),  # Greenland - why not?
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, f"{prefix:s} province"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, f"{prefix:s} locality"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, f"{prefix:s} node"),
        ]
    )

    key = rsa.generate_private_key(
        public_exponent=65537, key_size=4096, backend=default_backend()
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow() - timedelta(days=1))  # HACK
        .not_valid_after(datetime.utcnow() + timedelta(days=valid_days))
        .add_extension(
            x509.SubjectAlternativeName(
                [x509.DNSName("scherbelberg.solarsystem")]
            ),  # Dask does not check the domain
            critical=False,
        )
        .sign(ca_key, hashes.SHA256(), default_backend())
    )

    return key, cert


@typechecked
async def write_certs(key: rsa.RSAPrivateKey, cert: x509.Certificate, name: str):

    assert len(name) > 0

    with open(f"{name:s}.key", "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),  # ?
            )
        )

    with open(f"{name:s}.crt", "wb") as f:
        f.write(
            cert.public_bytes(
                encoding=serialization.Encoding.PEM,
            )
        )
