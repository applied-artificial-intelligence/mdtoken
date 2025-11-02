"""Tests for token counting functionality."""

import tempfile
from pathlib import Path

import pytest

from mdtoken.counter import TokenCounter


class TestTokenCounter:
    """Test TokenCounter class."""

    def test_initialization_default_encoding(self) -> None:
        """Test TokenCounter initializes with default cl100k_base encoding."""
        counter = TokenCounter()
        assert counter.encoding_name == "cl100k_base"
        assert counter.encoding is not None

    def test_initialization_custom_encoding(self) -> None:
        """Test TokenCounter can use custom encoding."""
        counter = TokenCounter(encoding_name="p50k_base")
        assert counter.encoding_name == "p50k_base"

    def test_initialization_invalid_encoding(self) -> None:
        """Test TokenCounter raises error for invalid encoding."""
        with pytest.raises(ValueError, match="Failed to load tiktoken encoding"):
            TokenCounter(encoding_name="invalid_encoding")

    def test_count_tokens_empty_string(self) -> None:
        """Test counting tokens in empty string."""
        counter = TokenCounter()
        assert counter.count_tokens("") == 0

    def test_count_tokens_simple_text(self) -> None:
        """Test counting tokens in simple text.

        The phrase "Hello, world!" encodes to 4 tokens in cl100k_base:
        ["Hello", ",", " world", "!"]
        """
        counter = TokenCounter()
        # Known token count for cl100k_base encoding
        result = counter.count_tokens("Hello, world!")
        assert result == 4

    def test_count_tokens_longer_text(self) -> None:
        """Test counting tokens in longer text."""
        counter = TokenCounter()
        text = "This is a longer sentence with multiple words and punctuation."
        result = counter.count_tokens(text)
        # cl100k_base should encode this to approximately 11 tokens
        assert 10 <= result <= 12

    def test_count_tokens_multiline_text(self) -> None:
        """Test counting tokens in multiline text."""
        counter = TokenCounter()
        text = """Line 1
Line 2
Line 3"""
        result = counter.count_tokens(text)
        # Newlines count as tokens
        assert result >= 6

    def test_count_tokens_with_unicode(self) -> None:
        """Test counting tokens with unicode characters."""
        counter = TokenCounter()
        text = "Hello 👋 World 🌍"
        result = counter.count_tokens(text)
        # Emoji characters typically take multiple tokens
        assert result >= 6

    def test_count_tokens_markdown(self) -> None:
        """Test counting tokens in markdown text."""
        counter = TokenCounter()
        markdown = """# Heading 1

This is a paragraph with **bold** and *italic* text.

- List item 1
- List item 2

```python
def example():
    pass
```
"""
        result = counter.count_tokens(markdown)
        # Markdown formatting adds tokens
        assert result >= 30

    def test_count_tokens_type_error(self) -> None:
        """Test count_tokens raises TypeError for non-string input."""
        counter = TokenCounter()
        with pytest.raises(TypeError, match="Expected str"):
            counter.count_tokens(123)  # type: ignore

    def test_count_file_tokens_basic(self) -> None:
        """Test counting tokens in a file."""
        counter = TokenCounter()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Hello, world!")
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            assert result == 4
        finally:
            temp_path.unlink()

    def test_count_file_tokens_with_path_string(self) -> None:
        """Test count_file_tokens accepts string path."""
        counter = TokenCounter()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            result = counter.count_file_tokens(temp_path)  # Pass string, not Path
            assert result >= 2
        finally:
            Path(temp_path).unlink()

    def test_count_file_tokens_nonexistent_file(self) -> None:
        """Test count_file_tokens raises FileNotFoundError for missing file."""
        counter = TokenCounter()
        with pytest.raises(FileNotFoundError, match="File not found"):
            counter.count_file_tokens(Path("/nonexistent/file.md"))

    def test_count_file_tokens_directory(self) -> None:
        """Test count_file_tokens raises IOError for directory."""
        counter = TokenCounter()
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(IOError, match="Not a regular file"):
                counter.count_file_tokens(Path(temp_dir))

    def test_count_file_tokens_utf8_encoding(self) -> None:
        """Test counting tokens in UTF-8 encoded file."""
        counter = TokenCounter()
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".md", delete=False
        ) as f:
            f.write("Unicode test: café, naïve, 日本語")
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            assert result >= 8
        finally:
            temp_path.unlink()

    def test_count_file_tokens_invalid_encoding(self) -> None:
        """Test count_file_tokens handles encoding errors gracefully."""
        counter = TokenCounter()
        # Create a file with non-UTF-8 content
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False) as f:
            f.write(b"\xff\xfe Invalid UTF-8")
            temp_path = Path(f.name)

        try:
            with pytest.raises(IOError, match="Failed to read file"):
                counter.count_file_tokens(temp_path, encoding="utf-8")
        finally:
            temp_path.unlink()

    def test_count_file_tokens_empty_file(self) -> None:
        """Test counting tokens in empty file."""
        counter = TokenCounter()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            assert result == 0
        finally:
            temp_path.unlink()

    def test_count_file_tokens_large_file(self) -> None:
        """Test counting tokens in a larger file."""
        counter = TokenCounter()
        # Create a file with ~1200 tokens
        large_text = "This is a test sentence. " * 200
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(large_text)
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            # Approximately 1200 tokens (6 tokens per sentence * 200)
            assert 1100 <= result <= 1300
        finally:
            temp_path.unlink()

    def test_repr(self) -> None:
        """Test string representation of TokenCounter."""
        counter = TokenCounter()
        assert repr(counter) == "TokenCounter(encoding='cl100k_base')"

        counter_custom = TokenCounter(encoding_name="p50k_base")
        assert repr(counter_custom) == "TokenCounter(encoding='p50k_base')"

    def test_consistency(self) -> None:
        """Test that counting same text multiple times gives same result."""
        counter = TokenCounter()
        text = "This is a consistency test."
        result1 = counter.count_tokens(text)
        result2 = counter.count_tokens(text)
        result3 = counter.count_tokens(text)
        assert result1 == result2 == result3

    def test_multiple_instances(self) -> None:
        """Test that multiple TokenCounter instances give same results."""
        counter1 = TokenCounter()
        counter2 = TokenCounter()
        text = "Testing multiple instances."
        assert counter1.count_tokens(text) == counter2.count_tokens(text)
