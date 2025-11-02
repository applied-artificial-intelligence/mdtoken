"""Token counting functionality using tiktoken library."""

from pathlib import Path

import tiktoken


class TokenCounter:
    """Count tokens in text and files using tiktoken's cl100k_base encoding.

    This encoding is used by GPT-4 and GPT-3.5-turbo models.
    """

    def __init__(self, encoding_name: str = "cl100k_base") -> None:
        """Initialize token counter with specified encoding.

        Args:
            encoding_name: Name of tiktoken encoding to use (default: cl100k_base)
        """
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except Exception as e:
            raise ValueError(f"Failed to load tiktoken encoding '{encoding_name}': {e}") from e
        self.encoding_name = encoding_name

    def count_tokens(self, text: str) -> int:
        """Count tokens in the given text.

        Args:
            text: Text string to count tokens for

        Returns:
            Number of tokens in the text

        Raises:
            ValueError: If text cannot be encoded
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}")

        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            raise ValueError(f"Failed to encode text: {e}") from e

    def count_file_tokens(self, path: Path, encoding: str = "utf-8") -> int:
        """Count tokens in a file.

        Args:
            path: Path to file to count tokens for
            encoding: Text encoding to use when reading file (default: utf-8)

        Returns:
            Number of tokens in the file

        Raises:
            FileNotFoundError: If file does not exist
            IOError: If file cannot be read
            ValueError: If file content cannot be encoded to tokens
        """
        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise OSError(f"Not a regular file: {path}")

        try:
            text = path.read_text(encoding=encoding)
        except UnicodeDecodeError as e:
            raise OSError(f"Failed to read file '{path}' with encoding '{encoding}': {e}") from e
        except Exception as e:
            raise OSError(f"Failed to read file '{path}': {e}") from e

        return self.count_tokens(text)

    def __repr__(self) -> str:
        """String representation of the token counter."""
        return f"TokenCounter(encoding='{self.encoding_name}')"
