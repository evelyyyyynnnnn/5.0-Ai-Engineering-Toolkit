# Releasing `spanlineage`

The distribution artifacts are built and validated in this repository, but the
package has **not** been uploaded to PyPI. Uploading requires a PyPI account and
API token belonging to the maintainer, so it is a manual step.

## Build

```bash
cd 1-data-provenance-library
python -m pip install --upgrade build twine
rm -rf dist build *.egg-info
python -m build            # writes dist/spanlineage-0.1.0.tar.gz and the wheel
python -m twine check dist/*
```

Both artifacts currently pass `twine check`.

## Verify the wheel in a clean environment

Never publish a wheel you have not installed from scratch — a package that
imports fine from the source tree can still ship a broken `packages.find`
config or a missing entry point.

```bash
python -m venv /tmp/relcheck && source /tmp/relcheck/bin/activate
pip install dist/*.whl
python -c "import spanlineage; print('import ok')"
spanlineage --help
pip freeze                 # confirm the dependency footprint is what you intended
deactivate
```

## Upload

Test first on TestPyPI, then the real index:

```bash
python -m twine upload --repository testpypi dist/*
python -m twine upload dist/*
```

Authenticate with an API token (username `__token__`). Do not commit the token.

## Name availability

`spanlineage` was available on PyPI when these artifacts were built. Names are claimed
on a first-come basis, so re-check before uploading; if it has been taken, change
`name` in `pyproject.toml` and rebuild.

## After publishing

Update the `tags` and `banner` in `src/site.py` to reflect the real state.
Report download counts only if you cite them as what they are — PyPI download
numbers are dominated by mirrors and CI, and are not a measure of adoption.
