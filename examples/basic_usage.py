"""Basic usage example for the docutray SDK."""

from dotenv import load_dotenv

import docutray

# Load environment variables from .env file
load_dotenv()

# Create a client (requires DOCUTRAY_API_KEY environment variable)
client = docutray.Client()

# Example: List document types
print("Available document types:")
for doc_type in client.document_types.list():
    print(f"  - {doc_type.name}")
