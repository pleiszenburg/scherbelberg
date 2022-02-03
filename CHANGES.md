# Changes

## 0.0.5 (2022-XX-XX)

- FEATURE: Raise proper exceptions when trying to connect to a broken or not existing cluster.
- FEATURE: CLI shows proper messages when trying to connect to a broken or not existing cluster.
- FIX: Workers and scheduler run same major & minor version of Python as client does.
- FIX: Remove remaining dependencies to Python wheels.
- FIX: Python language server dependency set to up-to-date package.
- FIX: Inconsistent CLI output behavior depending on platform.
- FIX: All error messages go to stderr.

## 0.0.4 (2022-02-02)

- FIX: Remove old and empty `scripts` parameter from `setup.py`.

## 0.0.3 (2022-02-01)

- FIX: Encoding of `README.md` explicitly set to UTF-8. Installation would fail on Windows otherwise.

## 0.0.2 (2022-02-01)

- Include docs into source distribution.

## 0.0.1 (2022-02-01)

- Initial release.
