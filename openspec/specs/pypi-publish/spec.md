## ADDED Requirements

### Requirement: Sequential publishing flow
The workflow SHALL publish to TestPyPI first and only proceed to PyPI after TestPyPI succeeds. This ensures TestPyPI acts as a validation gate before production release.

#### Scenario: TestPyPI success enables PyPI publish
- **WHEN** a version tag (v*) is pushed and TestPyPI publish succeeds
- **THEN** the PyPI publish job SHALL start

#### Scenario: TestPyPI failure blocks PyPI publish
- **WHEN** a version tag (v*) is pushed and TestPyPI publish fails
- **THEN** the PyPI publish job SHALL NOT run

### Requirement: Version consistency verification
The workflow SHALL verify that the git tag version matches the version in `pyproject.toml` before building. This prevents releasing mismatched versions.

#### Scenario: Matching versions proceed
- **WHEN** tag `v1.2.3` is pushed and `pyproject.toml` contains `version = "1.2.3"`
- **THEN** the build SHALL proceed

#### Scenario: Mismatched versions fail
- **WHEN** tag `v1.2.3` is pushed and `pyproject.toml` contains `version = "1.2.0"`
- **THEN** the build SHALL fail with an error message indicating the mismatch

#### Scenario: Manual trigger skips version check
- **WHEN** the workflow is triggered via `workflow_dispatch`
- **THEN** the version consistency check SHALL be skipped

### Requirement: TestPyPI duplicate handling
The workflow SHALL use `skip-existing: true` for TestPyPI publishing to handle re-runs gracefully when a version already exists.

#### Scenario: Re-run with existing version succeeds
- **WHEN** TestPyPI already has version 1.2.3 and the workflow runs again for the same version
- **THEN** TestPyPI publish SHALL succeed (skip existing) and proceed to PyPI

### Requirement: Trusted Publisher authentication
The workflow SHALL use PyPI Trusted Publisher (OIDC) for authentication. No API tokens or passwords SHALL be stored in repository secrets.

#### Scenario: OIDC authentication for TestPyPI
- **WHEN** publishing to TestPyPI
- **THEN** the job SHALL use `id-token: write` permission and `testpypi` environment

#### Scenario: OIDC authentication for PyPI
- **WHEN** publishing to PyPI
- **THEN** the job SHALL use `id-token: write` permission and `pypi` environment

### Requirement: Tag-based triggering
The workflow SHALL trigger on version tags matching the pattern `v*` (e.g., v1.0.0, v2.1.0-beta).

#### Scenario: Version tag triggers workflow
- **WHEN** a tag matching `v*` is pushed (e.g., `v1.0.0`)
- **THEN** the workflow SHALL run

#### Scenario: Non-version tags ignored
- **WHEN** a tag not matching `v*` is pushed (e.g., `release-candidate`)
- **THEN** the workflow SHALL NOT run

### Requirement: Manual workflow dispatch
The workflow SHALL support manual triggering via `workflow_dispatch` for re-runs without requiring a new tag.

#### Scenario: Manual trigger without tag
- **WHEN** the workflow is triggered manually via GitHub UI
- **THEN** the workflow SHALL run (version check skipped)
