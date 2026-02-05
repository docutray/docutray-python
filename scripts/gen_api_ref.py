#!/usr/bin/env python3
"""Generate API reference documentation from source code.

This script uses griffe to parse Python source files and generate
Markdown documentation for the DocuTray SDK public API.

Usage:
    python scripts/gen_api_ref.py

Output:
    docs/api/index.md - Module overview
    docs/api/client.md - Client and AsyncClient documentation
    docs/api/exceptions.md - Exception hierarchy documentation
    docs/api/resources/*.md - Resource class documentation
    docs/api/types/*.md - Type definition documentation
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import griffe
except ImportError:
    print("Error: griffe is required for API reference generation.")
    print("Install it with: pip install docutray[docs]")
    sys.exit(1)


def is_public(name: str) -> bool:
    """Check if a name represents a public API member."""
    return not name.startswith("_")


def format_signature(obj: griffe.Function | griffe.Class) -> str:
    """Format a function or class signature for documentation."""
    if isinstance(obj, griffe.Class):
        return f"class {obj.name}"

    params = []
    for param in obj.parameters:
        param_str = param.name
        if param.annotation:
            param_str += f": {param.annotation}"
        if param.default is not None and str(param.default) != "":
            param_str += f" = {param.default}"
        params.append(param_str)

    returns = ""
    if obj.returns:
        returns = f" -> {obj.returns}"

    return f"def {obj.name}({', '.join(params)}){returns}"


def extract_docstring_sections(docstring: str | None) -> dict[str, str]:
    """Extract Google-style docstring sections."""
    if not docstring:
        return {"description": "", "args": "", "returns": "", "raises": "", "example": ""}

    sections: dict[str, str] = {
        "description": "",
        "args": "",
        "returns": "",
        "raises": "",
        "example": "",
    }

    current_section = "description"
    current_content: list[str] = []

    for line in docstring.split("\n"):
        stripped = line.strip()

        # Check for section headers
        if stripped.lower() in ("args:", "arguments:"):
            sections[current_section] = "\n".join(current_content).strip()
            current_section = "args"
            current_content = []
        elif stripped.lower() in ("returns:", "return:"):
            sections[current_section] = "\n".join(current_content).strip()
            current_section = "returns"
            current_content = []
        elif stripped.lower() in ("raises:", "raise:", "exceptions:"):
            sections[current_section] = "\n".join(current_content).strip()
            current_section = "raises"
            current_content = []
        elif stripped.lower() in ("example:", "examples:"):
            sections[current_section] = "\n".join(current_content).strip()
            current_section = "example"
            current_content = []
        else:
            current_content.append(line)

    sections[current_section] = "\n".join(current_content).strip()
    return sections


def format_method_doc(method: griffe.Function) -> str:
    """Format a method's documentation as Markdown."""
    lines = []

    # Method signature
    sig = format_signature(method)
    lines.append(f"#### `{method.name}`\n")
    lines.append(f"```python\n{sig}\n```\n")

    # Parse docstring
    docstring = method.docstring.value if method.docstring else None
    sections = extract_docstring_sections(docstring)

    if sections["description"]:
        lines.append(f"{sections['description']}\n")

    if sections["args"]:
        lines.append("**Arguments:**\n")
        lines.append(f"{sections['args']}\n")

    if sections["returns"]:
        lines.append("**Returns:**\n")
        lines.append(f"{sections['returns']}\n")

    if sections["raises"]:
        lines.append("**Raises:**\n")
        lines.append(f"{sections['raises']}\n")

    if sections["example"]:
        lines.append("**Example:**\n")
        lines.append(f"```python\n{sections['example']}\n```\n")

    return "\n".join(lines)


def format_class_doc(cls: griffe.Class) -> str:
    """Format a class's documentation as Markdown."""
    lines = []

    # Class header
    lines.append(f"### `{cls.name}`\n")

    # Class docstring
    if cls.docstring:
        sections = extract_docstring_sections(cls.docstring.value)
        if sections["description"]:
            lines.append(f"{sections['description']}\n")
        if sections["example"]:
            lines.append("**Example:**\n")
            lines.append(f"```python\n{sections['example']}\n```\n")

    # Constructor args (from __init__)
    init_method = cls.members.get("__init__")
    if init_method and isinstance(init_method, griffe.Function):
        if init_method.docstring:
            init_sections = extract_docstring_sections(init_method.docstring.value)
            if init_sections["args"]:
                lines.append("**Arguments:**\n")
                lines.append(f"{init_sections['args']}\n")

    # Public methods
    methods = []
    for name, member in cls.members.items():
        if isinstance(member, griffe.Function) and is_public(name) and name != "__init__":
            methods.append(member)

    if methods:
        lines.append("**Methods:**\n")
        for method in sorted(methods, key=lambda m: m.name):
            lines.append(format_method_doc(method))

    # Public properties
    properties = []
    for name, member in cls.members.items():
        if isinstance(member, griffe.Attribute) and is_public(name):
            if hasattr(member, "labels") and "property" in member.labels:
                properties.append(member)

    if properties:
        lines.append("**Properties:**\n")
        for prop in sorted(properties, key=lambda p: p.name):
            lines.append(f"- `{prop.name}`")
            if prop.docstring:
                lines.append(f": {prop.docstring.value.split(chr(10))[0]}")
            lines.append("\n")

    return "\n".join(lines)


def generate_index(modules: dict[str, griffe.Module]) -> str:
    """Generate the index.md file content."""
    content = """# DocuTray Python SDK API Reference

This is the API reference for the DocuTray Python SDK.

## Installation

```bash
pip install docutray
```

## Modules

### Client

The main entry points for the SDK:

- [`Client`](client.md#client) - Synchronous client
- [`AsyncClient`](client.md#asyncclient) - Asynchronous client

### Exceptions

Error handling classes:

- [Exception Hierarchy](exceptions.md)

### Resources

API resource classes:

- [Convert](resources/convert.md) - Document conversion
- [Identify](resources/identify.md) - Document identification
- [DocumentTypes](resources/document_types.md) - Document type catalog
- [Steps](resources/steps.md) - Step execution
- [KnowledgeBases](resources/knowledge_bases.md) - Knowledge base operations

### Types

Response and model types:

- [Convert Types](types/convert.md)
- [Identify Types](types/identify.md)
- [Document Type Types](types/document_type.md)
- [Step Types](types/step.md)
- [Knowledge Base Types](types/knowledge_base.md)
- [Shared Types](types/shared.md)
"""
    return content


def generate_client_doc(module: griffe.Module) -> str:
    """Generate client.md documentation."""
    lines = ["# Client\n"]
    lines.append("The main client classes for interacting with the DocuTray API.\n")

    for name in ["Client", "AsyncClient"]:
        if name in module.members:
            cls = module.members[name]
            if isinstance(cls, griffe.Class):
                lines.append(format_class_doc(cls))

    return "\n".join(lines)


def generate_exceptions_doc(module: griffe.Module) -> str:
    """Generate exceptions.md documentation."""
    lines = ["# Exceptions\n"]
    lines.append("Exception classes for error handling in the DocuTray SDK.\n")

    lines.append("## Exception Hierarchy\n")
    lines.append("""
```
DocuTrayError (base)
├── APIConnectionError (network errors)
│   └── APITimeoutError (request timeout)
└── APIError (HTTP errors)
    ├── BadRequestError (400)
    ├── AuthenticationError (401)
    ├── PermissionDeniedError (403)
    ├── NotFoundError (404)
    ├── ConflictError (409)
    ├── UnprocessableEntityError (422)
    ├── RateLimitError (429)
    └── InternalServerError (5xx)
```
""")

    exception_order = [
        "DocuTrayError",
        "APIConnectionError",
        "APITimeoutError",
        "APIError",
        "BadRequestError",
        "AuthenticationError",
        "PermissionDeniedError",
        "NotFoundError",
        "ConflictError",
        "UnprocessableEntityError",
        "RateLimitError",
        "InternalServerError",
    ]

    for name in exception_order:
        if name in module.members:
            cls = module.members[name]
            if isinstance(cls, griffe.Class):
                lines.append(format_class_doc(cls))

    return "\n".join(lines)


def generate_resource_doc(module: griffe.Module, resource_name: str) -> str:
    """Generate documentation for a resource module."""
    lines = [f"# {resource_name}\n"]

    # Get module docstring
    if module.docstring:
        lines.append(f"{module.docstring.value}\n")

    # Document public classes
    for name, member in sorted(module.members.items()):
        if isinstance(member, griffe.Class) and is_public(name):
            lines.append(format_class_doc(member))

    return "\n".join(lines)


def generate_types_doc(module: griffe.Module, type_name: str) -> str:
    """Generate documentation for a types module."""
    lines = [f"# {type_name} Types\n"]

    # Get module docstring
    if module.docstring:
        lines.append(f"{module.docstring.value}\n")

    # Document public classes (Pydantic models)
    for name, member in sorted(module.members.items()):
        if isinstance(member, griffe.Class) and is_public(name):
            lines.append(f"### `{name}`\n")
            if member.docstring:
                lines.append(f"{member.docstring.value}\n")

            # Document fields
            fields = []
            for field_name, field in member.members.items():
                if isinstance(field, griffe.Attribute) and is_public(field_name):
                    fields.append((field_name, field))

            if fields:
                lines.append("**Fields:**\n")
                for field_name, field in sorted(fields):
                    annotation = field.annotation if field.annotation else "Any"
                    desc = ""
                    if field.docstring:
                        desc = f" - {field.docstring.value.split(chr(10))[0]}"
                    lines.append(f"- `{field_name}`: `{annotation}`{desc}\n")

    return "\n".join(lines)


def main() -> None:
    """Generate API reference documentation."""
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    src_path = project_root / "src" / "docutray"
    docs_path = project_root / "docs" / "api"

    # Create output directories
    docs_path.mkdir(parents=True, exist_ok=True)
    (docs_path / "resources").mkdir(exist_ok=True)
    (docs_path / "types").mkdir(exist_ok=True)

    print("Loading docutray package...")

    # Load the package using griffe
    try:
        package = griffe.load("docutray", search_paths=[str(project_root / "src")])
    except Exception as e:
        print(f"Error loading package: {e}")
        sys.exit(1)

    print("Generating documentation...")

    # Generate index
    (docs_path / "index.md").write_text(generate_index({}))
    print("  Generated index.md")

    # Generate client documentation
    if "_client" in package.members:
        client_module = package.members["_client"]
        if isinstance(client_module, griffe.Module):
            (docs_path / "client.md").write_text(generate_client_doc(client_module))
            print("  Generated client.md")

    # Generate exceptions documentation
    if "_exceptions" in package.members:
        exc_module = package.members["_exceptions"]
        if isinstance(exc_module, griffe.Module):
            (docs_path / "exceptions.md").write_text(generate_exceptions_doc(exc_module))
            print("  Generated exceptions.md")

    # Generate resource documentation
    resources = {
        "convert": "Convert",
        "identify": "Identify",
        "document_types": "Document Types",
        "steps": "Steps",
        "knowledge_bases": "Knowledge Bases",
    }

    if "resources" in package.members:
        resources_pkg = package.members["resources"]
        if isinstance(resources_pkg, griffe.Module):
            for module_name, display_name in resources.items():
                if module_name in resources_pkg.members:
                    res_module = resources_pkg.members[module_name]
                    if isinstance(res_module, griffe.Module):
                        filename = f"{module_name}.md"
                        (docs_path / "resources" / filename).write_text(
                            generate_resource_doc(res_module, display_name)
                        )
                        print(f"  Generated resources/{filename}")

    # Generate types documentation
    types_modules = {
        "convert": "Convert",
        "identify": "Identify",
        "document_type": "Document Type",
        "step": "Step",
        "knowledge_base": "Knowledge Base",
        "shared": "Shared",
    }

    if "types" in package.members:
        types_pkg = package.members["types"]
        if isinstance(types_pkg, griffe.Module):
            for module_name, display_name in types_modules.items():
                if module_name in types_pkg.members:
                    type_module = types_pkg.members[module_name]
                    if isinstance(type_module, griffe.Module):
                        filename = f"{module_name}.md"
                        (docs_path / "types" / filename).write_text(
                            generate_types_doc(type_module, display_name)
                        )
                        print(f"  Generated types/{filename}")

    print("\nAPI reference generation complete!")
    print(f"Output directory: {docs_path}")


if __name__ == "__main__":
    main()
