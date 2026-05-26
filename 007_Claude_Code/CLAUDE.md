# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# One-time setup
uv venv
.venv\Scripts\Activate.ps1     # PowerShell on Windows (README shows the bash form)
uv pip install -e .

# Run the MCP server (stdio transport, FastMCP)
uv run main.py

# Tests
uv run pytest                                              # all tests
uv run pytest tests/test_document.py                       # one file
uv run pytest tests/test_document.py::TestBinaryDocumentToMarkdown::test_binary_document_to_markdown_with_pdf  # one test
```

## Architecture

Single-process MCP server exposing document/utility tools to AI assistants.

- [main.py](main.py) is the entry point: it constructs `FastMCP("docs")`, registers each tool with `mcp.tool()(fn)`, and calls `mcp.run()`. Adding a new tool means writing the function in [tools/](tools/) and adding one registration line here — there is no auto-discovery.
- [tools/](tools/) holds the tool implementations. Each function is a plain Python callable; MCP introspects its signature, type hints, `Field(description=...)` metadata, and docstring to generate the tool schema sent to clients. Tools must remain importable without side effects (registration happens in `main.py`, not at import time).
- [tools/document.py](tools/document.py) wraps `markitdown.MarkItDown` to convert in-memory binary documents (DOCX, PDF, etc.) to markdown via a `BytesIO` stream and a `StreamInfo(extension=...)` hint. Callers pass raw `bytes` plus an extension string — the function does not touch the filesystem.
- [tests/](tests/) uses pytest with real binary fixtures in [tests/fixtures/](tests/fixtures/) (`mcp_docs.docx`, `mcp_docs.pdf`). Tests read the bytes off disk and feed them through the tool functions directly — they do not spin up the MCP server.

## Defining MCP Tools (from README)

Tools are Python functions registered with the FastMCP server:

```python
mcp.tool()(my_function)
```

Tool descriptions should:

- Begin with a one-line summary
- Provide a detailed explanation of functionality
- Explain when to use (and when not to use) the tool
- Include usage examples with expected input/output

Use `Field` from pydantic for parameter descriptions:

```python
from pydantic import Field

def my_tool(
    param1: str = Field(description="Detailed description of this parameter"),
    param2: int = Field(description="Explain what this parameter does"),
) -> ReturnType:
    """Comprehensive docstring here"""
    # Implementation
```

[tools/math.py](tools/math.py) is the canonical example to mirror: one-line summary, detailed paragraph, explicit "When to use" section, and `>>> ` doctest-style examples in the docstring. Every parameter carries a `Field(description=...)`, and the return type is annotated — both feed directly into the schema the MCP client sees.
