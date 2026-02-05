## 1. Async Resource Tests

- [x] 1.1 Add async tests for Convert resource (AsyncConvert.run, run_async, get_status)
- [x] 1.2 Add async tests for Identify resource (AsyncIdentify.run, run_async, get_status)
- [x] 1.3 Add async tests for DocumentTypes resource (AsyncDocumentTypes.list, get)
- [x] 1.4 Add async tests for KnowledgeBases resource (all methods including documents sub-resource)
- [x] 1.5 Add async tests for Steps resource (AsyncSteps.list, get)

## 2. WithRawResponse Tests

- [x] 2.1 Add tests for Convert.with_raw_response (verify status_code, headers, parse())
- [x] 2.2 Add tests for Identify.with_raw_response (verify status_code, headers, parse())
- [x] 2.3 Add tests for DocumentTypes.with_raw_response (verify status_code, headers, parse())
- [x] 2.4 Add tests for Steps.with_raw_response (verify status_code, headers, parse())
- [x] 2.5 Add tests for KnowledgeBases.with_raw_response (verify status_code, headers, parse())

## 3. Polling and HTTP Tests

- [x] 3.1 Add async polling tests (wait_for_completion_async success path)
- [x] 3.2 Add async polling timeout test
- [x] 3.3 Add async polling on_status callback test
- [x] 3.4 Add async HTTP request tests
- [x] 3.5 Add async retry behavior tests

## 4. Quality Tools

- [x] 4.1 Create .pre-commit-config.yaml with ruff hooks
- [x] 4.2 Add standard pre-commit hooks (trailing-whitespace, end-of-file-fixer, check-yaml)
- [x] 4.3 Fix any mypy strict mode errors in src/
- [x] 4.4 Fix any ruff check warnings in src/

## 5. Coverage Verification

- [x] 5.1 Run pytest with coverage and verify >80% overall (89%)
- [x] 5.2 Verify _polling.py coverage >80% (92%)
- [x] 5.3 Verify _response.py coverage >80% (80%)
- [x] 5.4 Verify _http.py coverage >80% (91%)
- [x] 5.5 Verify all resource modules coverage >80% (most at 85%+)
