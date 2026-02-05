## ADDED Requirements

### Requirement: Page class for paginated results
The SDK SHALL provide a `Page[T]` class that wraps paginated API responses and provides convenient access to data and pagination metadata.

#### Scenario: Access page data
- **WHEN** user receives a `Page[DocumentType]` from `document_types.list()`
- **THEN** user can access items via `page.data` as a `list[DocumentType]`

#### Scenario: Access pagination info
- **WHEN** user has a `Page` object
- **THEN** user can access `page.total`, `page.page`, and `page.limit` properties

### Requirement: Check for more pages
The SDK SHALL provide a `has_next_page()` method on `Page` that returns True if more pages exist.

#### Scenario: More pages available
- **WHEN** user calls `page.has_next_page()` and current page is not the last
- **THEN** method returns `True`

#### Scenario: No more pages
- **WHEN** user calls `page.has_next_page()` on the last page
- **THEN** method returns `False`

### Requirement: Fetch next page
The SDK SHALL provide a `next_page()` method on `Page` that fetches and returns the next page.

#### Scenario: Fetch next page
- **WHEN** user calls `page.next_page()` and more pages exist
- **THEN** SDK fetches next page from API and returns new `Page` object

#### Scenario: No next page available
- **WHEN** user calls `next_page()` when `has_next_page()` is False
- **THEN** SDK raises `StopIteration` exception

### Requirement: Iterate over all pages
The SDK SHALL provide an `iter_pages()` method that yields each page sequentially.

#### Scenario: Iterate through pages
- **WHEN** user calls `for page in result.iter_pages()`
- **THEN** SDK yields each `Page` object starting from current page until last page

### Requirement: Automatic item iteration
The SDK SHALL provide an `auto_paging_iter()` method that yields individual items across all pages.

#### Scenario: Iterate all items
- **WHEN** user calls `for item in result.auto_paging_iter()`
- **THEN** SDK yields each item from all pages transparently, fetching pages as needed

### Requirement: AsyncPage for async clients
The SDK SHALL provide `AsyncPage[T]` class with async versions of pagination methods for use with `AsyncClient`.

#### Scenario: Async iterate pages
- **WHEN** user calls `async for page in result.iter_pages_async()`
- **THEN** SDK yields each page using async HTTP requests

#### Scenario: Async iterate items
- **WHEN** user calls `async for item in result.auto_paging_iter_async()`
- **THEN** SDK yields each item across all pages using async requests
