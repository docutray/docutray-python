"""Example: Identify document type using the docutray SDK."""

from pathlib import Path

from dotenv import load_dotenv

import docutray

load_dotenv()

client = docutray.Client()

# Document type options to consider
DOC_TYPE_OPTIONS = ["invoice"]

# Test 1: Identify from a local file
print("=" * 50)
print("Test 1: Identify from local file")
print("=" * 50)

document_path = Path("sample_invoice.pdf")

if document_path.exists():
    result = client.identify.run(
        file=document_path,
        document_type_code_options=DOC_TYPE_OPTIONS,
    )

    print(f"Identified document type: {result.document_type.name}")
    print(f"Code: {result.document_type.code}")
    print(f"Confidence: {result.document_type.confidence:.2%}")

    if result.alternatives:
        print("\nAlternative matches:")
        for alt in result.alternatives:
            print(f"  - {alt.name}: {alt.confidence:.2%}")
else:
    print(f"File not found: {document_path}")

# Test 2: Identify from URL
print("\n" + "=" * 50)
print("Test 2: Identify from URL")
print("=" * 50)

url = "https://storage.googleapis.com/public.docutray.com/api-examples/sample_invoice.pdf"
print(f"URL: {url}")

result = client.identify.run(
    url=url,
    document_type_code_options=DOC_TYPE_OPTIONS,
)

print(f"Identified document type: {result.document_type.name}")
print(f"Code: {result.document_type.code}")
print(f"Confidence: {result.document_type.confidence:.2%}")

if result.alternatives:
    print("\nAlternative matches:")
    for alt in result.alternatives:
        print(f"  - {alt.name}: {alt.confidence:.2%}")

# Test 3: Async identification with polling
print("\n" + "=" * 50)
print("Test 3: Async identification with polling")
print("=" * 50)


def on_status(status):
    """Callback to track identification progress."""
    print(f"  Status: {status.status}")


# Start async identification
status = client.identify.run_async(
    url=url,
    document_type_code_options=DOC_TYPE_OPTIONS,
)
print(f"Started async identification: {status.identification_id}")

# Wait for completion with progress callback
final_status = status.wait(on_status=on_status)

if final_status.is_success():
    print(f"\nIdentified document type: {final_status.document_type.name}")
    print(f"Code: {final_status.document_type.code}")
    print(f"Confidence: {final_status.document_type.confidence:.2%}")
elif final_status.is_error():
    print(f"\nIdentification failed: {final_status.error}")
