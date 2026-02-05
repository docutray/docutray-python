## 1. Version Verification

- [x] 1.1 Add step to extract version from git tag (outputs `version`)
- [x] 1.2 Add step to compare tag version with pyproject.toml version
- [x] 1.3 Make version check conditional on `github.event_name == 'push'`

## 2. Sequential Publishing Flow

- [x] 2.1 Change `publish-pypi` job dependency from `needs: [build]` to `needs: [publish-testpypi]`
- [x] 2.2 Add `skip-existing: true` to TestPyPI publish step

## 3. Verification

- [x] 3.1 Review complete workflow for correctness
