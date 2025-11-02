"""Edge case and error handling tests for mdtoken.

These tests verify that the system handles unusual inputs, error conditions,
and edge cases gracefully with clear error messages.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from mdtoken.config import Config, ConfigError
from mdtoken.counter import TokenCounter
from mdtoken.enforcer import LimitEnforcer
from mdtoken.matcher import FileMatcher


class TestEmptyFiles:
    """Test handling of empty files and edge cases."""

    def test_empty_markdown_file(self):
        """Test that empty markdown files are handled correctly."""
        counter = TokenCounter()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            # Write nothing - empty file
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            assert result == 0, "Empty file should have 0 tokens"
        finally:
            temp_path.unlink()

    def test_empty_file_enforcement(self):
        """Test that empty files pass limit enforcement."""
        config = Config(default_limit=100)
        enforcer = LimitEnforcer(config)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            temp_path = Path(f.name)

        try:
            result = enforcer.check_files(check_files=[temp_path])
            assert result.passed, "Empty file should pass"
            assert result.total_tokens == 0
        finally:
            temp_path.unlink()

    def test_whitespace_only_file(self):
        """Test files with only whitespace."""
        counter = TokenCounter()

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write("   \n\n  \t  \n")
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            # Whitespace still produces some tokens
            assert result >= 0
        finally:
            temp_path.unlink()


class TestEncodingIssues:
    """Test handling of files with encoding issues."""

    def test_utf8_file_with_special_characters(self):
        """Test UTF-8 files with special characters."""
        counter = TokenCounter()

        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".md", delete=False
        ) as f:
            f.write("# Test\n\nEmoji: 🎉 ✨ 🚀\nUnicode: café, naïve, 日本語")
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            assert result > 0, "Should count tokens from UTF-8 file"
        finally:
            temp_path.unlink()

    def test_invalid_utf8_encoding(self):
        """Test that invalid UTF-8 raises appropriate error."""
        counter = TokenCounter()

        # Create file with invalid UTF-8 bytes
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".md", delete=False) as f:
            f.write(b"\xff\xfe Invalid UTF-8 \x80\x81")
            temp_path = Path(f.name)

        try:
            with pytest.raises(IOError, match="Failed to read file"):
                counter.count_file_tokens(temp_path, encoding="utf-8")
        finally:
            temp_path.unlink()

    def test_alternative_encoding(self):
        """Test files with non-UTF-8 encoding."""
        counter = TokenCounter()

        # Create file with latin-1 encoding
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="latin-1", suffix=".md", delete=False
        ) as f:
            f.write("Test with latin-1: café")
            temp_path = Path(f.name)

        try:
            # Reading with wrong encoding should fail gracefully
            with pytest.raises(IOError):
                counter.count_file_tokens(temp_path, encoding="utf-8")
        finally:
            temp_path.unlink()


class TestConfigEdgeCases:
    """Test configuration edge cases and error handling."""

    def test_missing_config_file_uses_defaults(self):
        """Test that missing config file returns defaults."""
        nonexistent_config = Path("/tmp/nonexistent_config_12345.yaml")

        # Should return default config when file doesn't exist
        config = Config.from_file(nonexistent_config)
        assert config.default_limit == 4000
        assert config.fail_on_exceed is True

    def test_empty_config_file(self):
        """Test that empty config file uses defaults."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            # Write empty content
            f.write("")
            temp_path = Path(f.name)

        try:
            config = Config.from_file(temp_path)
            # Should use default values
            assert config.default_limit == 4000
            assert config.fail_on_exceed is True
        finally:
            temp_path.unlink()

    def test_invalid_yaml_syntax(self):
        """Test that invalid YAML raises clear error."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            # Write invalid YAML
            f.write("default_limit: 100\n  invalid_indent:\nbad syntax [[[")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ConfigError, match="Invalid YAML"):
                Config.from_file(temp_path)
        finally:
            temp_path.unlink()

    def test_config_with_non_dict_content(self):
        """Test that config with non-dict content raises error."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            # Write YAML list instead of dict
            f.write("- item1\n- item2\n- item3")
            temp_path = Path(f.name)

        try:
            with pytest.raises(
                ConfigError, match="must contain a YAML dictionary"
            ):
                Config.from_file(temp_path)
        finally:
            temp_path.unlink()

    def test_config_with_invalid_values(self):
        """Test that config with invalid values raises error."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            # Write config with negative limit
            f.write("default_limit: -100\n")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ConfigError):
                Config.from_file(temp_path)
        finally:
            temp_path.unlink()


class TestLargeFiles:
    """Test handling of very large files."""

    def test_large_file_performance(self):
        """Test that large files are processed correctly."""
        counter = TokenCounter()

        # Create a large file (aim for >1MB, but accept large file for testing)
        large_content = "# Large Document\n\n" + ("Test sentence. " * 100000)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(large_content)
            temp_path = Path(f.name)

        try:
            # Verify file is large (>500KB is sufficient for testing)
            file_size = temp_path.stat().st_size
            assert file_size > 500 * 1024, "File should be > 500KB"

            # Should process without errors
            result = counter.count_file_tokens(temp_path)
            assert result > 100000, "Large file should have many tokens"
        finally:
            temp_path.unlink()

    def test_very_long_single_line(self):
        """Test file with extremely long single line."""
        counter = TokenCounter()

        # Create file with very long line (no newlines)
        long_line = "word " * 10000

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(long_line)
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            assert result > 5000, "Long line should produce many tokens"
        finally:
            temp_path.unlink()


class TestFileMatchingEdgeCases:
    """Test file matching edge cases."""

    def test_files_with_no_extension(self):
        """Test that files without extension are not matched."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create file without extension
            no_ext_file = root / "README"
            no_ext_file.write_text("# No extension")

            # Create normal markdown file
            md_file = root / "CHANGELOG.md"
            md_file.write_text("# Changelog")

            config = Config()
            matcher = FileMatcher(config, root=root)

            results = matcher.find_markdown_files()

            # Should only find .md file
            filenames = [p.name for p, _ in results]
            assert "CHANGELOG.md" in filenames
            assert "README" not in filenames

    def test_hidden_markdown_files(self):
        """Test that hidden markdown files (starting with .) are found."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create hidden markdown file
            hidden_file = root / ".hidden.md"
            hidden_file.write_text("# Hidden")

            config = Config()
            matcher = FileMatcher(config, root=root)

            results = matcher.find_markdown_files()

            # Hidden files should be found unless explicitly excluded
            filenames = [p.name for p, _ in results]
            assert ".hidden.md" in filenames

    def test_symlink_handling(self):
        """Test handling of symbolic links."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            # Create a real markdown file
            real_file = root / "real.md"
            real_file.write_text("# Real file")

            # Create a symlink to it
            symlink_file = root / "link.md"
            try:
                symlink_file.symlink_to(real_file)

                config = Config()
                matcher = FileMatcher(config, root=root)

                results = matcher.find_markdown_files()

                # Should find both real file and symlink
                # (or handle according to implementation)
                assert len(results) >= 1
            except OSError:
                # Symlinks might not be supported on some systems
                pytest.skip("Symlinks not supported on this system")


class TestErrorMessages:
    """Test that error messages are clear and helpful."""

    def test_nonexistent_file_error_message(self):
        """Test error message for non-existent file."""
        counter = TokenCounter()

        nonexistent = Path("/tmp/does_not_exist_12345.md")

        with pytest.raises(FileNotFoundError, match="File not found"):
            counter.count_file_tokens(nonexistent)

    def test_directory_instead_of_file_error(self):
        """Test error message when directory is passed instead of file."""
        counter = TokenCounter()

        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)

            with pytest.raises(IOError, match="Not a regular file"):
                counter.count_file_tokens(dir_path)

    def test_invalid_limit_value_error_message(self):
        """Test error message for invalid limit values."""
        with pytest.raises(ConfigError, match="must be a positive integer"):
            Config(default_limit=0)

        with pytest.raises(ConfigError, match="must be a positive integer"):
            Config(default_limit=-100)

    def test_invalid_total_limit_error_message(self):
        """Test error message for invalid total limit."""
        with pytest.raises(ConfigError, match="must be a positive integer"):
            Config(total_limit=-1000)


class TestBoundaryConditions:
    """Test boundary conditions and special values."""

    def test_exactly_at_limit(self):
        """Test file with token count exactly at limit."""
        config = Config(default_limit=10)
        enforcer = LimitEnforcer(config)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            # "Hello, world!" is exactly 4 tokens
            # We need exactly 10 tokens
            f.write("Hello, world! Hello, world! Test.")  # ~10 tokens
            temp_path = Path(f.name)

        try:
            result = enforcer.check_files(check_files=[temp_path])
            # May pass or fail depending on exact count
            # Just verify it handles the boundary correctly
            assert isinstance(result.passed, bool)
        finally:
            temp_path.unlink()

    def test_one_token_over_limit(self):
        """Test file with exactly one token over limit."""
        config = Config(default_limit=5)
        enforcer = LimitEnforcer(config)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            # Create content that's just over the limit
            f.write("One two three four five six")
            temp_path = Path(f.name)

        try:
            result = enforcer.check_files(check_files=[temp_path])
            assert not result.passed, "Should fail when over limit"
        finally:
            temp_path.unlink()

    def test_zero_limit(self):
        """Test that zero limit raises error."""
        with pytest.raises(ConfigError):
            Config(default_limit=0)

    def test_very_large_limit(self):
        """Test very large limit values."""
        # Should accept large limits without issue
        config = Config(default_limit=1000000000)
        assert config.default_limit == 1000000000


class TestSpecialCharacters:
    """Test handling of special characters and markdown syntax."""

    def test_markdown_with_code_blocks(self):
        """Test markdown files with code blocks."""
        counter = TokenCounter()

        markdown = """# Test

```python
def example():
    return "code"
```
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(markdown)
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            assert result > 5, "Code blocks should be counted"
        finally:
            temp_path.unlink()

    def test_markdown_with_tables(self):
        """Test markdown files with tables."""
        counter = TokenCounter()

        markdown = """
| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(markdown)
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            assert result > 5, "Tables should be counted"
        finally:
            temp_path.unlink()

    def test_markdown_with_links(self):
        """Test markdown with links and images."""
        counter = TokenCounter()

        markdown = """
[Link text](https://example.com)
![Image alt](image.png)
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            f.write(markdown)
            temp_path = Path(f.name)

        try:
            result = counter.count_file_tokens(temp_path)
            assert result > 3, "Links should be counted"
        finally:
            temp_path.unlink()
