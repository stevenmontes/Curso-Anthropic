import os
import pathlib
import shutil
import pytest

from tools.document import document_path_to_markdown


class TestDocumentPathToMarkdown:
    FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
    DOCX_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.docx")
    PDF_FIXTURE = os.path.join(FIXTURES_DIR, "mcp_docs.pdf")

    def test_converts_pdf_fixture_returns_expected_content(self):
        """Converts a PDF file at the given path to non-empty markdown."""
        result = document_path_to_markdown(self.PDF_FIXTURE)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "#" in result or "-" in result or "*" in result

    def test_converts_docx_fixture_returns_expected_content(self):
        """Converts a DOCX file at the given path to non-empty markdown."""
        result = document_path_to_markdown(self.DOCX_FIXTURE)
        assert isinstance(result, str)
        assert len(result) > 0
        assert "#" in result or "-" in result or "*" in result

    def test_extension_detection_is_case_insensitive_pdf(self, tmp_path):
        """Accepts a PDF file whose extension is uppercase (.PDF)."""
        target = tmp_path / "doc.PDF"
        shutil.copy(self.PDF_FIXTURE, target)
        result = document_path_to_markdown(str(target))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_extension_detection_is_case_insensitive_docx(self, tmp_path):
        """Accepts a DOCX file whose extension is mixed-case (.Docx)."""
        target = tmp_path / "doc.Docx"
        shutil.copy(self.DOCX_FIXTURE, target)
        result = document_path_to_markdown(str(target))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_accepts_relative_path(self, monkeypatch):
        """Accepts a relative path resolved against the current working directory."""
        monkeypatch.chdir(self.FIXTURES_DIR)
        result = document_path_to_markdown("mcp_docs.pdf")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_accepts_absolute_path(self):
        """Accepts a fully-qualified absolute path."""
        absolute = os.path.abspath(self.PDF_FIXTURE)
        result = document_path_to_markdown(absolute)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_accepts_pathlib_path_object(self):
        """Accepts a pathlib.Path in addition to a str."""
        result = document_path_to_markdown(pathlib.Path(self.PDF_FIXTURE))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_raises_file_not_found_for_missing_path(self, tmp_path):
        """Raises FileNotFoundError when the path does not exist."""
        missing = tmp_path / "does_not_exist.pdf"
        with pytest.raises(FileNotFoundError):
            document_path_to_markdown(str(missing))

    def test_raises_error_when_path_is_directory(self, tmp_path):
        """Raises an error when the path refers to a directory, not a file."""
        with pytest.raises((IsADirectoryError, PermissionError, OSError)):
            document_path_to_markdown(str(tmp_path))

    def test_raises_error_for_unsupported_extension(self, tmp_path):
        """Raises an error when the file extension is not a supported document type."""
        target = tmp_path / "doc.xyz"
        target.write_bytes(b"some content")
        with pytest.raises(Exception):
            document_path_to_markdown(str(target))

    def test_raises_error_for_missing_extension(self, tmp_path):
        """Raises an error when the file has no extension at all."""
        target = tmp_path / "noext"
        shutil.copy(self.PDF_FIXTURE, target)
        with pytest.raises(Exception):
            document_path_to_markdown(str(target))

    def test_raises_error_for_empty_file(self, tmp_path):
        """Raises an error when the target file exists but has zero bytes."""
        target = tmp_path / "empty.pdf"
        target.write_bytes(b"")
        with pytest.raises(Exception):
            document_path_to_markdown(str(target))
