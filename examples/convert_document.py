"""Example: Convert document and extract data using the docutray SDK."""

import json
from pathlib import Path

from dotenv import load_dotenv

import docutray

load_dotenv()

client = docutray.Client()

# Document type to use for conversion
DOCUMENT_TYPE_CODE = "invoice"

# Test 1: Convert from a local file
print("=" * 50)
print("Test 1: Convert from local file")
print("=" * 50)

document_path = Path("sample_invoice.pdf")

if document_path.exists():
    result = client.convert.run(
        file=document_path,
        document_type_code=DOCUMENT_TYPE_CODE,
    )

    print("Conversion successful!")
    print("\nExtracted data:")
    print(json.dumps(result.data, indent=2, ensure_ascii=False))
else:
    print(f"File not found: {document_path}")

# Test 2: Convert from URL
print("\n" + "=" * 50)
print("Test 2: Convert from URL")
print("=" * 50)

url = "https://storage.googleapis.com/public.docutray.com/api-examples/sample_invoice.pdf"
print(f"URL: {url}")

result = client.convert.run(
    url=url,
    document_type_code=DOCUMENT_TYPE_CODE,
)

print("Conversion successful!")
print("\nExtracted data:")
print(json.dumps(result.data, indent=2, ensure_ascii=False))

# Test 3: Async conversion with polling
print("\n" + "=" * 50)
print("Test 3: Async conversion with polling")
print("=" * 50)


def on_status(status):
    """Callback to track conversion progress."""
    print(f"  Status: {status.status}")


# Start async conversion
status = client.convert.run_async(
    url=url,
    document_type_code=DOCUMENT_TYPE_CODE,
)
print(f"Started async conversion: {status.conversion_id}")

# Wait for completion with progress callback
final_status = status.wait(on_status=on_status)

if final_status.is_success():
    print("\nConversion successful!")
    print("\nExtracted data:")
    print(json.dumps(final_status.data, indent=2, ensure_ascii=False))
elif final_status.is_error():
    print(f"\nConversion failed: {final_status.error}")
