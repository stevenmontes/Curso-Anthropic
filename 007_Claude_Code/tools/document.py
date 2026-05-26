from io import BytesIO
from pathlib import Path
from typing import Union

from markitdown import MarkItDown, StreamInfo
from pydantic import Field

SUPPORTED_EXTENSIONS = {"pdf", "docx"}


def binary_document_to_markdown(binary_data: bytes, file_type: str) -> str:
    """Converts binary document data to markdown-formatted text."""
    md = MarkItDown()
    file_obj = BytesIO(binary_data)
    stream_info = StreamInfo(extension=file_type)
    result = md.convert(file_obj, stream_info=stream_info)
    return result.text_content


def document_path_to_markdown(
    path: Union[str, Path] = Field(
        description="Filesystem path to a PDF or DOCX file to convert to markdown."
    ),
) -> str:
    """Read a PDF or DOCX file from disk and convert its contents to markdown.

    Opens the file at the given path, reads its bytes, and runs them through
    MarkItDown to produce a markdown-formatted string. The file's extension
    determines how the contents are parsed.

    When to use:
    - When you have a path to a local PDF or DOCX document and need its
      contents as markdown text.
    - When the document lives on disk; for in-memory bytes use
      `binary_document_to_markdown` instead.

    Examples:
    >>> document_path_to_markdown("docs/report.pdf")  # doctest: +SKIP
    '# Report\\n...'
    >>> document_path_to_markdown("notes.docx")  # doctest: +SKIP
    '# Notes\\n...'
    """
    path_obj = Path(path)

    if not path_obj.exists():
        raise FileNotFoundError(f"No such file: {path_obj}")
    if path_obj.is_dir():
        raise IsADirectoryError(f"Path is a directory, not a file: {path_obj}")

    extension = path_obj.suffix.lstrip(".").lower()
    if not extension:
        raise ValueError(f"File has no extension: {path_obj}")
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file extension '.{extension}'. "
            f"Supported: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    if path_obj.stat().st_size == 0:
        raise ValueError(f"File is empty: {path_obj}")

    binary_data = path_obj.read_bytes()
    return binary_document_to_markdown(binary_data, extension)
