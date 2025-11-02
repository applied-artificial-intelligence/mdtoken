"""File matching and discovery logic for mdtoken."""

from pathlib import Path
from typing import List, Tuple

from fnmatch import fnmatch

from mdtoken.config import Config


class FileMatcher:
    """Discovers and filters markdown files based on patterns.

    Attributes:
        config: Configuration object with limits and exclusions
        root: Root directory for file discovery
    """

    def __init__(self, config: Config, root: Path = None) -> None:
        """Initialize file matcher.

        Args:
            config: Configuration object
            root: Root directory for file discovery (defaults to current directory)
        """
        self.config = config
        self.root = root or Path.cwd()

    def _is_excluded(self, file_path: Path) -> bool:
        """Check if a file should be excluded based on exclude patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file should be excluded, False otherwise
        """
        # Convert to relative path from root for pattern matching
        try:
            rel_path = file_path.relative_to(self.root)
        except ValueError:
            # File is outside root, use absolute path
            rel_path = file_path

        # Convert to POSIX-style path for consistent pattern matching
        path_str = rel_path.as_posix()

        # Check each exclude pattern
        for pattern in self.config.exclude:
            # Handle directory patterns (ending with /**)
            if pattern.endswith("/**"):
                dir_pattern = pattern[:-3]  # Remove /**
                # Check if path starts with the directory
                if path_str.startswith(dir_pattern + "/") or path_str == dir_pattern:
                    return True
                # Also match the directory itself
                parts = path_str.split("/")
                if dir_pattern in parts:
                    return True

            # Handle glob patterns
            elif fnmatch(path_str, pattern):
                return True

            # Handle simple substring matching
            elif pattern in path_str:
                return True

        return False

    def find_markdown_files(
        self, patterns: List[str] = None, check_files: List[Path] = None
    ) -> List[Tuple[Path, int]]:
        """Find markdown files matching patterns.

        Args:
            patterns: Glob patterns to match (defaults to ["**/*.md"])
            check_files: Specific files to check instead of scanning (used by pre-commit)

        Returns:
            List of tuples (file_path, token_limit) for each matched file
        """
        if patterns is None:
            patterns = ["**/*.md"]

        results: List[Tuple[Path, int]] = []

        # If specific files provided (pre-commit mode), check only those
        if check_files:
            for file_path in check_files:
                # Ensure it's a Path object
                if not isinstance(file_path, Path):
                    file_path = Path(file_path)

                # Check if it's a markdown file
                if not file_path.suffix == ".md":
                    continue

                # Check if it exists
                if not file_path.exists() or not file_path.is_file():
                    continue

                # Check if excluded
                if self._is_excluded(file_path):
                    continue

                # Get limit for this file
                limit = self.config.get_limit(str(file_path))
                results.append((file_path, limit))

            return results

        # Otherwise, scan using glob patterns
        seen_files = set()

        for pattern in patterns:
            # Use glob to find matching files
            for file_path in self.root.glob(pattern):
                # Skip if not a file
                if not file_path.is_file():
                    continue

                # Skip if not markdown
                if file_path.suffix != ".md":
                    continue

                # Skip if already seen
                if file_path in seen_files:
                    continue

                # Skip if excluded
                if self._is_excluded(file_path):
                    continue

                # Get limit for this file
                limit = self.config.get_limit(str(file_path))
                results.append((file_path, limit))
                seen_files.add(file_path)

        # Sort results by path for consistency
        results.sort(key=lambda x: x[0])

        return results

    def __repr__(self) -> str:
        """String representation of FileMatcher."""
        return f"FileMatcher(config={self.config}, root={self.root})"
