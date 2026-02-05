## Context

The project has an existing `.github/workflows/publish.yml` that publishes to both TestPyPI and PyPI. The current implementation runs both publish jobs in parallel after the build job, with no version validation. This change modifies the existing workflow to add safety mechanisms.

Current state:
- Build job: checkout → uv → build → upload artifact
- TestPyPI job: runs in parallel with PyPI (needs: build)
- PyPI job: runs in parallel with TestPyPI (needs: build)
- Trigger: `v*` tags and `workflow_dispatch`

## Goals / Non-Goals

**Goals:**
- TestPyPI validates the release before PyPI (sequential flow)
- Catch version mismatches early (tag vs pyproject.toml)
- Handle TestPyPI re-runs gracefully (skip-existing)
- Maintain manual trigger capability for re-runs

**Non-Goals:**
- Automated changelog generation
- Automatic version bumping
- Multi-platform wheel builds (pure Python package)
- Separate test job (tests run in CI, not publish workflow)

## Decisions

### 1. Sequential job dependency (TestPyPI → PyPI)

**Decision**: Change `publish-pypi` to depend on `publish-testpypi` instead of `build`.

**Rationale**: TestPyPI acts as a dry-run for PyPI. If TestPyPI fails (bad metadata, invalid package), we don't want PyPI to attempt publishing. The few seconds of additional latency is worth the safety.

**Alternatives considered**:
- Keep parallel: Faster but risky - both could fail or only one succeeds
- Add explicit test job: Overkill for this workflow - TestPyPI IS the test

### 2. Version check in build job

**Decision**: Add version extraction and comparison step in the build job, conditional on `github.event_name == 'push'`.

**Rationale**:
- Build job is the right place (fails fast, before any artifacts)
- Conditional check allows `workflow_dispatch` to work without a tag context
- Shell-based extraction keeps it simple (no Python dependencies)

**Implementation**:
```yaml
- name: Get tag version
  if: github.event_name == 'push'
  id: tag
  run: echo "version=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

- name: Verify version consistency
  if: github.event_name == 'push'
  run: |
    PKG_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
    if [ "${{ steps.tag.outputs.version }}" != "$PKG_VERSION" ]; then
      echo "::error::Tag v${{ steps.tag.outputs.version }} doesn't match pyproject.toml version $PKG_VERSION"
      exit 1
    fi
```

**Alternatives considered**:
- Python script: More robust parsing but adds complexity
- Separate validation job: Adds latency without benefit

### 3. skip-existing for TestPyPI only

**Decision**: Add `skip-existing: true` to TestPyPI job only, not PyPI.

**Rationale**:
- TestPyPI may have the same version from previous failed runs
- PyPI should fail if version exists (indicates release process error)
- This matches the "TestPyPI as dry-run" philosophy

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| TestPyPI outage blocks PyPI release | Use `workflow_dispatch` to manually re-run PyPI job (though it will also re-run TestPyPI with skip-existing) |
| Version check regex fails on edge cases | Simple pattern `version = "X.Y.Z"` matches pyproject.toml standard format |
| Manual trigger publishes wrong version | Acceptable risk - manual trigger is for re-runs, user is responsible for ensuring correct state |

## Migration Plan

1. Update `.github/workflows/publish.yml` with new structure
2. No rollback needed - workflow changes are atomic
3. First test: push a tag to verify sequential flow works
4. External setup (not automated):
   - Configure Trusted Publisher on TestPyPI (environment: `testpypi`)
   - Configure Trusted Publisher on PyPI (environment: `pypi`)
