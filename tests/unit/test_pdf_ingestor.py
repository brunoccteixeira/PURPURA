"""
Unit tests for src/ingest/pdf_ingestor.py

Tests cover:
- Page dataclass
- read_pdf function (with mocked PDF)
- concat_pages function
- sha256_text function
"""

import hashlib
import sys
from dataclasses import is_dataclass
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.ingest.pdf_ingestor import Page, concat_pages, read_pdf, sha256_text


# ============================================================================
# Page Dataclass Tests
# ============================================================================

@pytest.mark.unit
class TestPageDataclass:
    """Tests for Page dataclass."""

    def test_page_is_dataclass(self):
        """Test that Page is a dataclass."""
        assert is_dataclass(Page)

    def test_page_creation(self):
        """Test Page dataclass creation."""
        page = Page(page_num=1, text="Test content")

        assert page.page_num == 1
        assert page.text == "Test content"

    def test_page_fields(self):
        """Test Page has expected fields."""
        page = Page(page_num=5, text="Sample text")

        assert hasattr(page, "page_num")
        assert hasattr(page, "text")
        assert isinstance(page.page_num, int)
        assert isinstance(page.text, str)

    def test_page_equality(self):
        """Test Page equality comparison."""
        page1 = Page(page_num=1, text="Same content")
        page2 = Page(page_num=1, text="Same content")
        page3 = Page(page_num=2, text="Different content")

        assert page1 == page2
        assert page1 != page3

    def test_page_immutable_after_creation(self):
        """Test that Page fields can be accessed."""
        page = Page(page_num=10, text="Content")

        # Should be able to read fields
        assert page.page_num == 10
        assert page.text == "Content"


# ============================================================================
# SHA256 Hash Tests
# ============================================================================

@pytest.mark.unit
class TestSha256Text:
    """Tests for sha256_text function."""

    def test_sha256_simple_text(self):
        """Test SHA256 hash of simple text."""
        text = "Hello, World!"
        result = sha256_text(text)

        # Should return hex digest
        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 hex is 64 chars

        # Should be deterministic
        assert result == sha256_text(text)

    def test_sha256_empty_string(self):
        """Test SHA256 hash of empty string."""
        result = sha256_text("")

        assert isinstance(result, str)
        assert len(result) == 64

        # Verify against known hash
        expected = hashlib.sha256("".encode("utf-8")).hexdigest()
        assert result == expected

    def test_sha256_long_text(self):
        """Test SHA256 hash of long text."""
        text = "Lorem ipsum " * 1000
        result = sha256_text(text)

        assert isinstance(result, str)
        assert len(result) == 64

    def test_sha256_unicode_text(self):
        """Test SHA256 hash with unicode characters."""
        text = "Hello 世界! Olá mundo! Привет мир!"
        result = sha256_text(text)

        assert isinstance(result, str)
        assert len(result) == 64

        # Should handle unicode properly
        expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert result == expected

    def test_sha256_special_characters(self):
        """Test SHA256 hash with special characters."""
        text = "Special: @#$%^&*()_+-=[]{}|;:',.<>?/`~"
        result = sha256_text(text)

        assert isinstance(result, str)
        assert len(result) == 64

    def test_sha256_different_texts_different_hashes(self):
        """Test that different texts produce different hashes."""
        hash1 = sha256_text("Text A")
        hash2 = sha256_text("Text B")

        assert hash1 != hash2

    def test_sha256_deterministic(self):
        """Test that hash is deterministic."""
        text = "Deterministic test"

        hash1 = sha256_text(text)
        hash2 = sha256_text(text)
        hash3 = sha256_text(text)

        assert hash1 == hash2 == hash3


# ============================================================================
# Concat Pages Tests
# ============================================================================

@pytest.mark.unit
class TestConcatPages:
    """Tests for concat_pages function."""

    def test_concat_single_page(self):
        """Test concatenating single page."""
        pages = [Page(page_num=1, text="Single page content")]
        result = concat_pages(pages)

        assert result == "Single page content"

    def test_concat_multiple_pages(self):
        """Test concatenating multiple pages."""
        pages = [
            Page(page_num=1, text="Page 1 content"),
            Page(page_num=2, text="Page 2 content"),
            Page(page_num=3, text="Page 3 content"),
        ]
        result = concat_pages(pages)

        # Should join with newlines
        expected = "Page 1 content\n\nPage 2 content\n\nPage 3 content"
        assert result == expected

    def test_concat_empty_list(self):
        """Test concatenating empty list."""
        result = concat_pages([])

        assert result == ""

    def test_concat_preserves_order(self):
        """Test that page order is preserved."""
        pages = [
            Page(page_num=1, text="First"),
            Page(page_num=2, text="Second"),
            Page(page_num=3, text="Third"),
        ]
        result = concat_pages(pages)

        assert "First" in result
        assert result.index("First") < result.index("Second")
        assert result.index("Second") < result.index("Third")

    def test_concat_empty_pages(self):
        """Test concatenating pages with empty text."""
        pages = [
            Page(page_num=1, text=""),
            Page(page_num=2, text="Content"),
            Page(page_num=3, text=""),
        ]
        result = concat_pages(pages)

        assert "Content" in result
        assert result == "\n\nContent\n\n"

    def test_concat_whitespace_handling(self):
        """Test concatenation with whitespace."""
        pages = [
            Page(page_num=1, text="  Text with spaces  "),
            Page(page_num=2, text="\tTab text\t"),
        ]
        result = concat_pages(pages)

        # Should preserve whitespace in original text
        assert "  Text with spaces  " in result

    def test_concat_newlines_in_pages(self):
        """Test concatenation when pages already have newlines."""
        pages = [
            Page(page_num=1, text="Line 1\nLine 2"),
            Page(page_num=2, text="Line 3\nLine 4"),
        ]
        result = concat_pages(pages)

        assert "Line 1\nLine 2" in result
        assert "Line 3\nLine 4" in result


# ============================================================================
# Read PDF Tests
# ============================================================================

@pytest.mark.unit
class TestReadPdf:
    """Tests for read_pdf function."""

    def test_read_pdf_with_mock(self):
        """Test read_pdf with mocked pypdf.PdfReader."""
        # Create mock PDF pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"

        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"

        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            result = read_pdf("/fake/path/test.pdf")

            assert len(result) == 2
            assert result[0].page_num == 1
            assert result[0].text == "Page 1 content"
            assert result[1].page_num == 2
            assert result[1].text == "Page 2 content"

    def test_read_pdf_single_page(self):
        """Test reading PDF with single page."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Single page"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            result = read_pdf("/fake/path/single.pdf")

            assert len(result) == 1
            assert result[0].page_num == 1
            assert result[0].text == "Single page"

    def test_read_pdf_empty_document(self):
        """Test reading PDF with no pages."""
        mock_reader = Mock()
        mock_reader.pages = []

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            result = read_pdf("/fake/path/empty.pdf")

            assert result == []

    def test_read_pdf_page_numbering(self):
        """Test that page numbers are sequential starting from 1."""
        mock_pages = [Mock() for _ in range(5)]
        for page in mock_pages:
            page.extract_text.return_value = "Content"

        mock_reader = Mock()
        mock_reader.pages = mock_pages

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            result = read_pdf("/fake/path/test.pdf")

            assert len(result) == 5
            for i, page in enumerate(result, start=1):
                assert page.page_num == i

    def test_read_pdf_empty_pages(self):
        """Test reading PDF where some pages have no text."""
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = ""

        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 has content"

        mock_page3 = Mock()
        mock_page3.extract_text.return_value = ""

        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2, mock_page3]

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            result = read_pdf("/fake/path/test.pdf")

            assert len(result) == 3
            assert result[0].text == ""
            assert result[1].text == "Page 2 has content"
            assert result[2].text == ""

    def test_read_pdf_returns_page_objects(self):
        """Test that read_pdf returns Page objects."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Content"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            result = read_pdf("/fake/path/test.pdf")

            assert len(result) == 1
            assert isinstance(result[0], Page)

    def test_read_pdf_with_pathlib_path(self):
        """Test read_pdf accepts Path object."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Content"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader) as mock_reader_cls:
            path = Path("/fake/path/test.pdf")
            result = read_pdf(path)

            # Should work with Path object
            assert len(result) == 1
            mock_reader_cls.assert_called_once_with(path)

    def test_read_pdf_unicode_content(self):
        """Test reading PDF with unicode content."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Unicode: 世界 Ñoño Привет"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            result = read_pdf("/fake/path/test.pdf")

            assert len(result) == 1
            assert "世界" in result[0].text
            assert "Ñoño" in result[0].text


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.unit
class TestPdfIngestorIntegration:
    """Integration tests for PDF ingestor components."""

    def test_read_and_concat_workflow(self):
        """Test typical workflow: read PDF then concatenate."""
        # Mock PDF with multiple pages
        mock_pages = []
        for i in range(1, 4):
            page = Mock()
            page.extract_text.return_value = f"Page {i} content"
            mock_pages.append(page)

        mock_reader = Mock()
        mock_reader.pages = mock_pages

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            # Read PDF
            pages = read_pdf("/fake/path/test.pdf")

            # Concatenate
            full_text = concat_pages(pages)

            assert "Page 1 content" in full_text
            assert "Page 2 content" in full_text
            assert "Page 3 content" in full_text

    def test_read_concat_and_hash_workflow(self):
        """Test complete workflow: read, concat, and hash."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Consistent content"

        mock_reader = Mock()
        mock_reader.pages = [mock_page]

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            # Read PDF
            pages = read_pdf("/fake/path/test.pdf")

            # Concatenate
            full_text = concat_pages(pages)

            # Hash
            text_hash = sha256_text(full_text)

            assert isinstance(text_hash, str)
            assert len(text_hash) == 64

            # Should be deterministic
            pages2 = read_pdf("/fake/path/test.pdf")
            full_text2 = concat_pages(pages2)
            text_hash2 = sha256_text(full_text2)

            assert text_hash == text_hash2

    def test_empty_pdf_workflow(self):
        """Test workflow with empty PDF."""
        mock_reader = Mock()
        mock_reader.pages = []

        with patch("src.ingest.pdf_ingestor.PdfReader", return_value=mock_reader):
            pages = read_pdf("/fake/path/empty.pdf")
            full_text = concat_pages(pages)
            text_hash = sha256_text(full_text)

            assert pages == []
            assert full_text == ""
            assert len(text_hash) == 64  # Still produces valid hash
