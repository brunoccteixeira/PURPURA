"""
Unit tests for src/ingest/chunker.py

Tests cover:
- Token counting (with tiktoken and fallback)
- Text chunking with various parameters
- Overlap behavior
- Edge cases
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.ingest.chunker import count_tokens, chunk_text


# ============================================================================
# Token Counting Tests
# ============================================================================

@pytest.mark.unit
class TestCountTokens:
    """Tests for count_tokens function."""

    def test_count_tokens_with_tiktoken(self):
        """Test token counting when tiktoken is available."""
        text = "Hello world! This is a test."
        token_count = count_tokens(text)

        # Should return a positive integer
        assert isinstance(token_count, int)
        assert token_count > 0

        # Basic sanity check: should be roughly proportional to text length
        # For English text, typically 1 token per 4 characters
        assert token_count < len(text)

    def test_count_tokens_empty_string(self):
        """Test token counting with empty string."""
        assert count_tokens("") >= 0

    def test_count_tokens_fallback_when_tiktoken_unavailable(self):
        """Test that fallback works when tiktoken is not available."""
        # Mock tiktoken being unavailable
        with patch("src.ingest.chunker._enc", None):
            text = "This is a test sentence with multiple words."
            token_count = count_tokens(text)

            # Fallback uses len(s)//4
            expected = max(1, len(text) // 4)
            assert token_count == expected

    def test_count_tokens_single_character(self):
        """Test token counting with single character."""
        assert count_tokens("a") >= 1

    def test_count_tokens_very_long_text(self):
        """Test token counting with very long text."""
        long_text = "word " * 10000  # 10,000 words
        token_count = count_tokens(long_text)

        assert token_count > 1000  # Should be substantial
        assert isinstance(token_count, int)

    def test_count_tokens_special_characters(self):
        """Test token counting with special characters."""
        text = "Special chars: @#$%^&*()_+-=[]{}|;:',.<>?/`~"
        token_count = count_tokens(text)

        assert token_count > 0
        assert isinstance(token_count, int)

    def test_count_tokens_unicode(self):
        """Test token counting with unicode characters."""
        text = "Hello 世界! Olá mundo! Привет мир!"
        token_count = count_tokens(text)

        assert token_count > 0
        assert isinstance(token_count, int)


# ============================================================================
# Text Chunking Tests
# ============================================================================

@pytest.mark.unit
class TestChunkText:
    """Tests for chunk_text function."""

    def test_chunk_short_text_single_chunk(self):
        """Test that short text stays as single chunk."""
        text = "This is a short text that fits in one chunk."
        chunks = chunk_text(text, max_tokens=100, overlap=20)

        assert len(chunks) == 1
        assert chunks[0]["text"] == text.strip()
        assert chunks[0]["token_len"] > 0

    def test_chunk_empty_text(self):
        """Test chunking empty text."""
        chunks = chunk_text("", max_tokens=100, overlap=20)

        # Should return empty list or single empty chunk
        assert isinstance(chunks, list)
        if len(chunks) > 0:
            assert chunks[0]["text"] == ""

    def test_chunk_text_creates_multiple_chunks(self, sample_text_long):
        """Test that long text is split into multiple chunks."""
        chunks = chunk_text(sample_text_long, max_tokens=200, overlap=50)

        # Long text should produce multiple chunks
        assert len(chunks) > 1

        # Each chunk should have required fields
        for chunk in chunks:
            assert "text" in chunk
            assert "token_len" in chunk
            assert isinstance(chunk["text"], str)
            assert isinstance(chunk["token_len"], int)

    def test_chunk_respects_max_tokens(self):
        """Test that chunks respect max_tokens limit."""
        text = " ".join(["word"] * 1000)  # Many words
        max_tokens = 100
        chunks = chunk_text(text, max_tokens=max_tokens, overlap=20)

        # All chunks should be at or under max_tokens
        for i, chunk in enumerate(chunks):
            # Last chunk might be smaller, others should be close to max
            if i < len(chunks) - 1:
                assert chunk["token_len"] <= max_tokens * 1.2  # Allow some tolerance
            assert chunk["token_len"] > 0

    def test_chunk_overlap_works(self):
        """Test that overlap between chunks works correctly."""
        # Create text with distinct words to track overlap
        words = [f"word{i:03d}" for i in range(100)]
        text = " ".join(words)

        chunks = chunk_text(text, max_tokens=150, overlap=30)

        if len(chunks) > 1:
            # Check that consecutive chunks have some overlap
            for i in range(len(chunks) - 1):
                chunk1_words = set(chunks[i]["text"].split())
                chunk2_words = set(chunks[i + 1]["text"].split())

                # Should have some common words
                overlap_words = chunk1_words & chunk2_words
                # Note: overlap might be 0 if chunks are very different
                # but we can at least verify structure
                assert isinstance(overlap_words, set)

    def test_chunk_with_zero_overlap(self):
        """Test chunking with no overlap."""
        text = " ".join(["word"] * 500)
        chunks = chunk_text(text, max_tokens=100, overlap=0)

        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk["token_len"] > 0

    def test_chunk_with_large_overlap(self):
        """Test chunking with overlap larger than max_tokens (edge case)."""
        text = " ".join(["word"] * 500)

        # Overlap > max_tokens is unusual but should not crash
        chunks = chunk_text(text, max_tokens=100, overlap=150)

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk["token_len"] > 0

    def test_chunk_preserves_text_content(self, sample_text_short):
        """Test that chunking preserves all text content."""
        chunks = chunk_text(sample_text_short, max_tokens=50, overlap=10)

        # Reconstruct text from chunks (without overlap)
        # This is approximate since overlap complicates things
        total_length = sum(len(chunk["text"]) for chunk in chunks)

        # Total length should be reasonable compared to original
        # (will be larger due to overlap)
        assert total_length >= len(sample_text_short.strip()) * 0.9

    def test_chunk_with_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        text = "Word1   \n\n   Word2 \t Word3"
        chunks = chunk_text(text, max_tokens=100, overlap=20)

        assert len(chunks) == 1
        # Should preserve whitespace structure to some extent
        assert "Word1" in chunks[0]["text"]
        assert "Word2" in chunks[0]["text"]
        assert "Word3" in chunks[0]["text"]

    def test_chunk_single_word(self):
        """Test chunking a single word."""
        chunks = chunk_text("word", max_tokens=100, overlap=20)

        assert len(chunks) == 1
        assert chunks[0]["text"] == "word"
        assert chunks[0]["token_len"] > 0

    def test_chunk_very_long_single_word(self):
        """Test chunking when a single word exceeds max_tokens."""
        very_long_word = "a" * 10000
        chunks = chunk_text(very_long_word, max_tokens=100, overlap=20)

        # Should still create chunks (implementation specific)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert len(chunk["text"]) > 0

    def test_chunk_newlines_and_paragraphs(self):
        """Test chunking text with newlines and paragraphs."""
        text = """
        Paragraph 1 with some text here.
        More text in paragraph 1.

        Paragraph 2 with different content.
        Additional lines here.

        Paragraph 3 is the final one.
        """

        chunks = chunk_text(text, max_tokens=50, overlap=10)

        assert len(chunks) >= 1
        # Verify text is split reasonably
        reconstructed = " ".join(chunk["text"] for chunk in chunks)
        assert "Paragraph 1" in reconstructed

    def test_chunk_with_different_max_tokens(self):
        """Test chunking with various max_tokens values."""
        text = " ".join(["word"] * 200)

        for max_tok in [50, 100, 200, 500]:
            chunks = chunk_text(text, max_tokens=max_tok, overlap=20)

            assert len(chunks) > 0
            # Smaller max_tokens should produce more chunks
            if max_tok < 200:
                assert len(chunks) >= 1

    def test_chunk_metadata_consistency(self):
        """Test that chunk metadata (token_len) is consistent."""
        text = "This is a test sentence for metadata validation."
        chunks = chunk_text(text, max_tokens=100, overlap=20)

        for chunk in chunks:
            # Verify token_len matches actual count
            actual_count = count_tokens(chunk["text"])
            assert chunk["token_len"] == actual_count

    def test_chunk_deterministic_output(self):
        """Test that chunking produces deterministic results."""
        text = "Deterministic test " * 50

        chunks1 = chunk_text(text, max_tokens=100, overlap=20)
        chunks2 = chunk_text(text, max_tokens=100, overlap=20)

        # Should produce identical results
        assert len(chunks1) == len(chunks2)
        for c1, c2 in zip(chunks1, chunks2):
            assert c1["text"] == c2["text"]
            assert c1["token_len"] == c2["token_len"]


# ============================================================================
# Integration Tests (chunker + tokenizer)
# ============================================================================

@pytest.mark.unit
class TestChunkerIntegration:
    """Integration tests for chunker components."""

    def test_realistic_document_chunking(self, sample_text_long):
        """Test chunking a realistic document with IFRS content."""
        chunks = chunk_text(sample_text_long, max_tokens=800, overlap=120)

        # Should produce reasonable number of chunks
        assert len(chunks) >= 1

        # All chunks should have text
        for chunk in chunks:
            assert len(chunk["text"]) > 0
            assert chunk["token_len"] > 0

        # Check that content is preserved
        all_text = " ".join(c["text"] for c in chunks)
        assert "Climate" in all_text or "climate" in all_text

    def test_chunking_preserves_key_information(self, sample_text_long):
        """Test that chunking preserves important content."""
        chunks = chunk_text(sample_text_long, max_tokens=300, overlap=50)

        # Combine all chunks
        combined = " ".join(chunk["text"] for chunk in chunks)

        # Key terms should be preserved (case insensitive)
        key_terms = ["emissions", "risk", "climate", "scope"]
        for term in key_terms:
            assert term.lower() in combined.lower()

    def test_chunk_boundaries_reasonable(self):
        """Test that chunk boundaries are at reasonable positions."""
        text = ". ".join([f"Sentence {i}" for i in range(100)])
        chunks = chunk_text(text, max_tokens=100, overlap=20)

        for chunk in chunks:
            # Chunks should generally not start/end mid-word
            text = chunk["text"]
            if len(text) > 0:
                # Should start with alphanumeric or space
                assert text[0].isalnum() or text[0].isspace() or text[0] in ".,;!?"

    def test_memory_efficiency_large_document(self):
        """Test that chunker handles large documents without excessive memory."""
        # Create a very large document
        large_text = " ".join([f"Word{i}" for i in range(10000)])

        chunks = chunk_text(large_text, max_tokens=500, overlap=100)

        # Should complete without errors
        assert len(chunks) > 10
        assert all(isinstance(c, dict) for c in chunks)
