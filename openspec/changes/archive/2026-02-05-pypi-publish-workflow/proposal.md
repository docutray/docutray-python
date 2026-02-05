## Why

The project needs an automated, secure way to publish releases to PyPI. The current workflow exists but has gaps: TestPyPI and PyPI publish in parallel (no validation gate), there's no version consistency check between git tags and `pyproject.toml`, and TestPyPI fails on duplicate versions instead of handling them gracefully.

## What Changes

- Make PyPI publishing sequential: TestPyPI must succeed before PyPI publishes (acts as validation gate)
- Add version consistency verification: git tag must match `pyproject.toml` version (skipped on manual `workflow_dispatch`)
- Add `skip-existing: true` for TestPyPI to handle re-runs gracefully
- Keep `workflow_dispatch` for manual re-runs without version check

## Capabilities

### New Capabilities

- `pypi-publish`: GitHub Actions workflow for automated PyPI publishing with Trusted Publisher (OIDC), sequential TestPyPI→PyPI flow, and version validation

### Modified Capabilities

<!-- None - this is new infrastructure -->

## Impact

- **Files**: `.github/workflows/publish.yml` (modify existing)
- **Dependencies**: None (uses existing GitHub Actions)
- **External Setup Required**:
  - Configure Trusted Publisher on TestPyPI (test.pypi.org) with environment `testpypi`
  - Configure Trusted Publisher on PyPI (pypi.org) with environment `pypi`
  - Both need: owner=`docutray`, repo=`docutray-python`, workflow=`publish.yml`
