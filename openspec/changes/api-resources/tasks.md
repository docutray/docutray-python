## 1. Types Layer - Shared Types

- [x] 1.1 Create `types/shared.py` with Pagination model and common types
- [x] 1.2 Add FileInput type alias and content type constants to `_types.py`
- [x] 1.3 Add file handling TypedDicts (FileUploadParams, UrlUploadParams, Base64UploadParams)

## 2. Types Layer - Response Models

- [x] 2.1 Create `types/convert.py` with ConversionResult and ConversionStatus models
- [x] 2.2 Create `types/identify.py` with IdentificationResult, IdentificationStatus, DocumentTypeMatch models
- [x] 2.3 Create `types/document_type.py` with DocumentType and ValidationResult models
- [x] 2.4 Create `types/step.py` with StepExecutionStatus model
- [x] 2.5 Update `types/__init__.py` with all exports

## 3. Types Layer - Request Parameters

- [x] 3.1 Add ConvertParams TypedDict to `_types.py`
- [x] 3.2 Add IdentifyParams TypedDict to `_types.py`
- [x] 3.3 Add DocumentTypesListParams TypedDict to `_types.py`
- [x] 3.4 Add StepsParams TypedDict to `_types.py`

## 4. File Handling Utilities

- [x] 4.1 Create `_files.py` with file input preparation utilities
- [x] 4.2 Implement `prepare_file_upload()` for Path, bytes, BinaryIO inputs
- [x] 4.3 Implement content type detection from file extension
- [x] 4.4 Implement `prepare_url_upload()` for URL inputs
- [x] 4.5 Implement `prepare_base64_upload()` for base64 inputs

## 5. Base Client Enhancement

- [x] 5.1 Add `_request()` method to BaseClient for sync HTTP requests
- [x] 5.2 Add `_request_async()` method to BaseAsyncClient for async HTTP requests
- [x] 5.3 Add multipart form data support to request methods

## 6. Resources - Convert

- [x] 6.1 Create `resources/convert.py` with Convert class
- [x] 6.2 Implement `Convert.run()` for sync conversion
- [x] 6.3 Implement `Convert.run_async()` for async conversion initiation
- [x] 6.4 Implement `Convert.get_status()` for status polling
- [x] 6.5 Create AsyncConvert class with async versions of all methods

## 7. Resources - Identify

- [x] 7.1 Create `resources/identify.py` with Identify class
- [x] 7.2 Implement `Identify.run()` for sync identification
- [x] 7.3 Implement `Identify.run_async()` for async identification initiation
- [x] 7.4 Implement `Identify.get_status()` for status polling
- [x] 7.5 Create AsyncIdentify class with async versions of all methods

## 8. Resources - Document Types

- [x] 8.1 Create `resources/document_types.py` with DocumentTypes class
- [x] 8.2 Implement `DocumentTypes.list()` with pagination support
- [x] 8.3 Implement `DocumentTypes.get()` for single type retrieval
- [x] 8.4 Implement `DocumentTypes.validate()` for JSON validation
- [x] 8.5 Create AsyncDocumentTypes class with async versions of all methods

## 9. Resources - Steps

- [x] 9.1 Create `resources/steps.py` with Steps class
- [x] 9.2 Implement `Steps.run_async()` for async step execution
- [x] 9.3 Implement `Steps.get_status()` for execution status polling
- [x] 9.4 Create AsyncSteps class with async versions of all methods

## 10. Async Polling Helpers

- [x] 10.1 Add `wait()` method to ConversionStatus model
- [x] 10.2 Add `wait()` method to IdentificationStatus model
- [x] 10.3 Add `wait()` method to StepExecutionStatus model
- [x] 10.4 Implement configurable poll_interval and timeout parameters

## 11. Client Integration

- [x] 11.1 Add `convert` property to Client using cached_property
- [x] 11.2 Add `identify` property to Client using cached_property
- [x] 11.3 Add `document_types` property to Client using cached_property
- [x] 11.4 Add `steps` property to Client using cached_property
- [x] 11.5 Add all resource properties to AsyncClient

## 12. Exports and Documentation

- [x] 12.1 Update `resources/__init__.py` with all resource exports
- [x] 12.2 Update main `__init__.py` with public type exports
- [x] 12.3 Add comprehensive docstrings with examples to all public methods

## 13. Testing

- [x] 13.1 Create `tests/test_resources/test_convert.py` with unit tests
- [x] 13.2 Create `tests/test_resources/test_identify.py` with unit tests
- [x] 13.3 Create `tests/test_resources/test_document_types.py` with unit tests
- [x] 13.4 Create `tests/test_resources/test_steps.py` with unit tests
- [x] 13.5 Create `tests/test_files.py` for file handling utilities
- [x] 13.6 Run mypy and fix any type errors
- [x] 13.7 Run ruff and fix any linting issues
