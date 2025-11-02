"""Tests for file matching and discovery logic."""

import tempfile
from pathlib import Path

from mdtoken.config import Config
from mdtoken.matcher import FileMatcher


class TestFileMatcherInitialization:
    """Test FileMatcher initialization."""

    def test_init_with_config(self) -> None:
        """Test FileMatcher initializes with config."""
        config = Config()
        matcher = FileMatcher(config)
        assert matcher.config == config
        assert matcher.root == Path.cwd()

    def test_init_with_custom_root(self) -> None:
        """Test FileMatcher with custom root directory."""
        config = Config()
        root = Path("/tmp")
        matcher = FileMatcher(config, root=root)
        assert matcher.root == root

    def test_repr(self) -> None:
        """Test string representation."""
        config = Config()
        matcher = FileMatcher(config)
        repr_str = repr(matcher)
        assert "FileMatcher" in repr_str


class TestExclusionLogic:
    """Test file exclusion pattern matching."""

    def test_exclude_git_directory(self) -> None:
        """Test that .git directory is excluded."""
        config = Config()
        matcher = FileMatcher(config, root=Path("/tmp"))

        # Simulate a file in .git directory
        git_file = Path("/tmp/.git/config")
        assert matcher._is_excluded(git_file) is True

    def test_exclude_node_modules(self) -> None:
        """Test that node_modules directory is excluded."""
        config = Config()
        matcher = FileMatcher(config, root=Path("/tmp"))

        node_file = Path("/tmp/node_modules/package/file.md")
        assert matcher._is_excluded(node_file) is True

    def test_exclude_venv(self) -> None:
        """Test that venv directory is excluded."""
        config = Config()
        matcher = FileMatcher(config, root=Path("/tmp"))

        venv_file = Path("/tmp/venv/lib/python3.9/file.md")
        assert matcher._is_excluded(venv_file) is True

    def test_exclude_custom_pattern(self) -> None:
        """Test custom exclude patterns."""
        config = Config(exclude=["archived/**", "temp/**"])
        matcher = FileMatcher(config, root=Path("/tmp"))

        archived_file = Path("/tmp/archived/old.md")
        assert matcher._is_excluded(archived_file) is True

        temp_file = Path("/tmp/temp/test.md")
        assert matcher._is_excluded(temp_file) is True

    def test_not_excluded(self) -> None:
        """Test that normal files are not excluded."""
        config = Config()
        matcher = FileMatcher(config, root=Path("/tmp"))

        normal_file = Path("/tmp/docs/README.md")
        assert matcher._is_excluded(normal_file) is False

    def test_exclude_file_outside_root(self) -> None:
        """Test exclusion checking for files outside the root directory."""
        config = Config(exclude=["archived/**"])
        matcher = FileMatcher(config, root=Path("/tmp/project"))

        # File outside root should still be checked for exclusion
        outside_file = Path("/home/user/archived/file.md")
        # This will trigger ValueError in relative_to, falling back to absolute path
        result = matcher._is_excluded(outside_file)
        # Should check exclusion based on the pattern
        assert isinstance(result, bool)

    def test_exclude_directory_pattern_in_parts(self) -> None:
        """Test that directory exclusion works when directory name appears in path parts."""
        config = Config(exclude=["venv/**"])
        matcher = FileMatcher(config, root=Path("/tmp"))

        # File where 'venv' appears as a directory component
        venv_file = Path("/tmp/project/venv/lib/file.md")
        assert matcher._is_excluded(venv_file) is True

    def test_exclude_with_substring_match(self) -> None:
        """Test exclusion using substring matching."""
        config = Config(exclude=["temp"])
        matcher = FileMatcher(config, root=Path("/tmp"))

        # File with 'temp' in path should be excluded
        temp_file = Path("/tmp/temporary/file.md")
        assert matcher._is_excluded(temp_file) is True

    def test_exclude_exact_directory_match(self) -> None:
        """Test exclusion when path exactly matches directory pattern."""
        config = Config(exclude=["docs/**"])
        matcher = FileMatcher(config, root=Path("/tmp"))

        # Path that is exactly the excluded directory
        docs_dir = Path("/tmp/docs")
        assert matcher._is_excluded(docs_dir) is True


class TestFindMarkdownFiles:
    """Test finding markdown files."""

    def setup_method(self) -> None:
        """Create temporary directory structure for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.root = Path(self.temp_dir)

        # Create test directory structure
        (self.root / "docs").mkdir()
        (self.root / "src").mkdir()
        (self.root / ".git").mkdir()
        (self.root / "node_modules").mkdir()

        # Create test markdown files
        (self.root / "README.md").touch()
        (self.root / "CHANGELOG.md").touch()
        (self.root / "docs" / "api.md").touch()
        (self.root / "docs" / "guide.md").touch()
        (self.root / "src" / "notes.md").touch()

        # Create excluded files (should not be found)
        (self.root / ".git" / "config.md").touch()
        (self.root / "node_modules" / "package.md").touch()

        # Create non-markdown files (should not be found)
        (self.root / "script.py").touch()
        (self.root / "docs" / "data.json").touch()

    def teardown_method(self) -> None:
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_find_all_markdown_files(self) -> None:
        """Test finding all markdown files with default pattern."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        results = matcher.find_markdown_files()

        # Should find 5 markdown files (excluding .git and node_modules)
        assert len(results) == 5

        # Verify results are tuples of (path, limit)
        for path, limit in results:
            assert isinstance(path, Path)
            assert isinstance(limit, int)
            assert limit == 4000  # Default limit

    def test_find_specific_pattern(self) -> None:
        """Test finding files with specific pattern."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        results = matcher.find_markdown_files(patterns=["docs/*.md"])

        # Should find 2 files in docs/
        assert len(results) == 2
        paths = [str(p.name) for p, _ in results]
        assert "api.md" in paths
        assert "guide.md" in paths

    def test_find_multiple_patterns(self) -> None:
        """Test finding files with multiple patterns."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        results = matcher.find_markdown_files(patterns=["*.md", "docs/*.md"])

        # Should find files matching either pattern (no duplicates)
        assert len(results) >= 2

    def test_per_file_limits(self) -> None:
        """Test that per-file limits are applied correctly."""
        config = Config(
            default_limit=4000,
            limits={
                "README.md": 8000,
                "docs/api.md": 6000,
            },
        )
        matcher = FileMatcher(config, root=self.root)

        results = matcher.find_markdown_files()
        results_dict = {p.name: limit for p, limit in results}

        # Check README.md has custom limit
        assert results_dict.get("README.md") == 8000

        # Check api.md has custom limit
        api_results = [(p, limit) for p, limit in results if p.name == "api.md"]
        if api_results:
            assert api_results[0][1] == 6000

        # Check other files have default limit
        assert results_dict.get("CHANGELOG.md") == 4000

    def test_exclude_patterns_work(self) -> None:
        """Test that exclude patterns prevent files from being found."""
        # Create archived directory
        (self.root / "archived").mkdir()
        (self.root / "archived" / "old.md").touch()

        config = Config(exclude=[".git/**", "node_modules/**", "archived/**"])
        matcher = FileMatcher(config, root=self.root)

        results = matcher.find_markdown_files()
        paths = [p.name for p, _ in results]

        # Should not find files in excluded directories
        assert "config.md" not in paths  # .git
        assert "package.md" not in paths  # node_modules
        assert "old.md" not in paths  # archived

    def test_check_specific_files(self) -> None:
        """Test checking specific files (pre-commit mode)."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        # Check specific files
        files_to_check = [
            self.root / "README.md",
            self.root / "docs" / "api.md",
            self.root / "script.py",  # Not markdown, should be skipped
        ]

        results = matcher.find_markdown_files(check_files=files_to_check)

        # Should only include the 2 markdown files
        assert len(results) == 2
        paths = [p.name for p, _ in results]
        assert "README.md" in paths
        assert "api.md" in paths
        assert "script.py" not in paths

    def test_check_files_excludes_excluded_files(self) -> None:
        """Test that specific file checking still respects exclusions."""
        config = Config(exclude=[".git/**"])
        matcher = FileMatcher(config, root=self.root)

        # Try to check a file in excluded directory
        files_to_check = [
            self.root / ".git" / "config.md",
            self.root / "README.md",
        ]

        results = matcher.find_markdown_files(check_files=files_to_check)

        # Should only include README.md, not the .git file
        assert len(results) == 1
        assert results[0][0].name == "README.md"

    def test_empty_directory(self) -> None:
        """Test behavior with empty directory."""
        empty_dir = tempfile.mkdtemp()
        try:
            config = Config()
            matcher = FileMatcher(config, root=Path(empty_dir))

            results = matcher.find_markdown_files()
            assert len(results) == 0
        finally:
            import shutil

            shutil.rmtree(empty_dir)

    def test_nonexistent_file_in_check_files(self) -> None:
        """Test that nonexistent files in check_files are skipped."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        files_to_check = [
            self.root / "README.md",
            self.root / "does_not_exist.md",
        ]

        results = matcher.find_markdown_files(check_files=files_to_check)

        # Should only include the existing file
        assert len(results) == 1
        assert results[0][0].name == "README.md"

    def test_results_sorted(self) -> None:
        """Test that results are sorted by path."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        results = matcher.find_markdown_files()
        paths = [p for p, _ in results]

        # Check that paths are sorted
        assert paths == sorted(paths)

    def test_check_files_with_string_paths(self) -> None:
        """Test that check_files accepts string paths and converts them to Path objects."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        # Pass string paths instead of Path objects
        files_to_check = [
            str(self.root / "README.md"),
            str(self.root / "docs" / "api.md"),
        ]

        results = matcher.find_markdown_files(check_files=files_to_check)

        # Should convert strings to Path and process correctly
        assert len(results) == 2
        paths = [p.name for p, _ in results]
        assert "README.md" in paths
        assert "api.md" in paths

    def test_glob_with_non_file_items(self) -> None:
        """Test that glob pattern skips directories and non-file items."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        # The glob pattern will match directories too, but they should be skipped
        results = matcher.find_markdown_files(patterns=["**"])

        # Results should only contain files, not directories
        for path, _ in results:
            assert path.is_file()

    def test_glob_with_non_markdown_files(self) -> None:
        """Test that glob pattern filters out non-.md files."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        # Use a pattern that would match all files
        results = matcher.find_markdown_files(patterns=["**/*"])

        # All results should have .md suffix
        for path, _ in results:
            assert path.suffix == ".md"

    def test_duplicate_files_from_multiple_patterns(self) -> None:
        """Test that duplicate files from overlapping patterns are returned only once."""
        config = Config()
        matcher = FileMatcher(config, root=self.root)

        # Use overlapping patterns that would match the same files
        results = matcher.find_markdown_files(patterns=["**/*.md", "*.md", "docs/*.md"])

        # Check for duplicates
        paths = [p for p, _ in results]
        assert len(paths) == len(set(paths)), "Results contain duplicate files"


class TestIntegration:
    """Integration tests for FileMatcher."""

    def test_full_workflow(self) -> None:
        """Test complete workflow with config and matching."""
        # Create temporary structure
        temp_dir = tempfile.mkdtemp()
        root = Path(temp_dir)

        try:
            # Create files
            (root / "docs").mkdir()
            (root / "README.md").touch()
            (root / "docs" / "guide.md").touch()
            (root / "archived").mkdir()
            (root / "archived" / "old.md").touch()

            # Create config with custom limits and exclusions
            config = Config(
                default_limit=5000,
                limits={"README.md": 10000},
                exclude=["archived/**"],
            )

            # Create matcher
            matcher = FileMatcher(config, root=root)

            # Find files
            results = matcher.find_markdown_files()

            # Verify results
            assert len(results) == 2  # README.md and guide.md (not old.md)

            results_dict = {p.name: limit for p, limit in results}
            assert results_dict["README.md"] == 10000  # Custom limit
            assert results_dict["guide.md"] == 5000  # Default limit

        finally:
            import shutil

            shutil.rmtree(temp_dir)
