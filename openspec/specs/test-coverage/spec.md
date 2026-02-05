# Test Coverage

## Purpose

Define comprehensive test coverage requirements for the DocuTray Python SDK, ensuring async operations, raw response access, polling, and HTTP layer are thoroughly tested.

## Requirements

### Requirement: Async resource method tests
The test suite SHALL include async tests for all resource methods that mirror their sync counterparts.

#### Scenario: Async convert resource tests
- **WHEN** running pytest on test_resources/test_convert.py
- **THEN** async tests exist for AsyncConvert.run(), AsyncConvert.run_async(), AsyncConvert.get_status()

#### Scenario: Async identify resource tests
- **WHEN** running pytest on test_resources/test_identify.py
- **THEN** async tests exist for AsyncIdentify.run(), AsyncIdentify.run_async(), AsyncIdentify.get_status()

#### Scenario: Async document_types resource tests
- **WHEN** running pytest on test_resources/test_document_types.py
- **THEN** async tests exist for AsyncDocumentTypes.list(), AsyncDocumentTypes.get()

#### Scenario: Async knowledge_bases resource tests
- **WHEN** running pytest on test_resources/test_knowledge_bases.py
- **THEN** async tests exist for all AsyncKnowledgeBases methods including documents() sub-resource

#### Scenario: Async steps resource tests
- **WHEN** running pytest on test_resources/test_steps.py
- **THEN** async tests exist for AsyncSteps.list(), AsyncSteps.get()

### Requirement: WithRawResponse tests
The test suite SHALL include tests for the .with_raw_response accessor on all resources.

#### Scenario: Convert WithRawResponse test
- **WHEN** calling client.convert.with_raw_response.run()
- **THEN** the test verifies RawResponse contains status_code, headers, and parse() returns ConversionResult

#### Scenario: Identify WithRawResponse test
- **WHEN** calling client.identify.with_raw_response.run()
- **THEN** the test verifies RawResponse contains status_code, headers, and parse() returns IdentificationResult

#### Scenario: DocumentTypes WithRawResponse test
- **WHEN** calling client.document_types.with_raw_response.list()
- **THEN** the test verifies RawResponse contains status_code, headers, and parse() returns Page[DocumentType]

#### Scenario: Steps WithRawResponse test
- **WHEN** calling client.steps.with_raw_response.list()
- **THEN** the test verifies RawResponse contains status_code, headers, and parse() returns Page[Step]

#### Scenario: KnowledgeBases WithRawResponse test
- **WHEN** calling client.knowledge_bases.with_raw_response.list()
- **THEN** the test verifies RawResponse contains status_code, headers, and parse() returns Page[KnowledgeBase]

### Requirement: Async polling tests
The test suite SHALL include tests for async polling functionality.

#### Scenario: wait_for_completion_async success
- **WHEN** calling status.wait() on AsyncClient with a status that transitions to SUCCESS
- **THEN** the test verifies polling completes and returns the final status with data

#### Scenario: wait_for_completion_async timeout
- **WHEN** calling status.wait(timeout=0.1) on AsyncClient with a status that never completes
- **THEN** the test verifies TimeoutError is raised

#### Scenario: on_status callback with async
- **WHEN** calling status.wait(on_status=callback) on AsyncClient
- **THEN** the callback is invoked for each status change during polling

### Requirement: HTTP layer async tests
The test suite SHALL include tests for async HTTP request methods.

#### Scenario: Async request success
- **WHEN** making an async HTTP request through AsyncClient._http.request()
- **THEN** the test verifies the response is returned correctly

#### Scenario: Async retry on 500
- **WHEN** an async request receives 500 errors followed by success
- **THEN** the test verifies retry logic works with exponential backoff

#### Scenario: Async timeout handling
- **WHEN** an async request times out
- **THEN** the test verifies APITimeoutError is raised with should_retry=True

### Requirement: Coverage threshold
The test suite SHALL achieve at least 80% code coverage across all modules.

#### Scenario: Overall coverage check
- **WHEN** running pytest with --cov=src/docutray --cov-fail-under=80
- **THEN** the command succeeds without coverage failure

#### Scenario: Module coverage above threshold
- **WHEN** examining coverage for _polling.py, _response.py, _http.py, and all resources
- **THEN** each module has at least 80% coverage
