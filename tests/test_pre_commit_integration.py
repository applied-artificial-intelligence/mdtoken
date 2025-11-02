"""Integration tests for pre-commit hook."""

import subprocess
import tempfile
from pathlib import Path

import pytest


class TestCLIIntegration:
    """Test CLI behavior when invoked by pre-commit."""

    def test_cli_accepts_file_paths(self) -> None:
        """Test that CLI accepts file paths as positional arguments."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test\n\nSmall file content.")
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                ["mdtoken", "check", str(temp_path)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "within token limits" in result.stdout.lower() or "PASSED" in result.stdout
        finally:
            temp_path.unlink()

    def test_cli_exit_code_pass(self) -> None:
        """Test CLI returns exit code 0 when files pass limits."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Small File\n\nThis is a small test file.")
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                ["mdtoken", "check", str(temp_path)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
        finally:
            temp_path.unlink()

    def test_cli_exit_code_fail(self) -> None:
        """Test CLI returns exit code 1 when files exceed limits."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            # Create a file that exceeds default limit (4000 tokens)
            large_content = "This is a test sentence. " * 2000
            f.write(f"# Large File\n\n{large_content}")
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                ["mdtoken", "check", str(temp_path)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 1
            assert "exceeding token limits" in result.stdout.lower()
        finally:
            temp_path.unlink()

    def test_cli_dry_run_exit_code(self) -> None:
        """Test --dry-run flag exits with 0 even on violations."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            # Create a file that exceeds limits
            large_content = "This is a test sentence. " * 2000
            f.write(f"# Large File\n\n{large_content}")
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                ["mdtoken", "check", "--dry-run", str(temp_path)],
                capture_output=True,
                text=True,
            )

            # Should return 0 even though file exceeds limits
            assert result.returncode == 0
            # But should still show violations
            assert "exceeding token limits" in result.stdout.lower()
        finally:
            temp_path.unlink()

    def test_cli_multiple_files(self) -> None:
        """Test CLI handles multiple file arguments."""
        temp_files = []
        try:
            # Create multiple small files
            for i in range(3):
                f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
                f.write(f"# File {i}\n\nSmall content.")
                f.close()
                temp_files.append(Path(f.name))

            result = subprocess.run(
                ["mdtoken", "check"] + [str(p) for p in temp_files],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0
            assert "Files checked: 3" in result.stdout
        finally:
            for path in temp_files:
                path.unlink()

    def test_cli_with_config_option(self) -> None:
        """Test CLI respects --config option."""
        # Create custom config
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as config_file:
            config_file.write("default_limit: 10\n")  # Very strict limit
            config_path = Path(config_file.name)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as md_file:
            # Create content that exceeds 10 token limit
            md_file.write("# Test\n\nThis will definitely exceed a very strict 10 token limit.")
            md_path = Path(md_file.name)

        try:
            result = subprocess.run(
                ["mdtoken", "check", "--config", str(config_path), str(md_path)],
                capture_output=True,
                text=True,
            )

            # Should fail with strict config
            assert result.returncode == 1
        finally:
            config_path.unlink()
            md_path.unlink()

    def test_cli_verbose_mode(self) -> None:
        """Test CLI verbose mode shows suggestions."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            # Create a file that exceeds limits
            large_content = "This is a test sentence. " * 2000
            f.write(f"# Large File\n\n{large_content}")
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                ["mdtoken", "check", "-v", str(temp_path)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 1
            # Verbose mode should show suggestions
            assert "Suggestions:" in result.stdout or "split" in result.stdout.lower()
        finally:
            temp_path.unlink()

    def test_cli_only_checks_markdown_files(self) -> None:
        """Test that non-markdown files are ignored when passed."""
        # This behavior is actually handled by the click.Path(exists=True) constraint
        # and the fact that our matcher filters by .md extension
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Not a markdown file")
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                ["mdtoken", "check", str(temp_path)],
                capture_output=True,
                text=True,
            )

            # Should complete successfully (0 files checked)
            assert result.returncode == 0
            assert "Files checked: 0" in result.stdout
        finally:
            temp_path.unlink()


class TestPreCommitIntegration:
    """Test integration with pre-commit framework."""

    def test_hook_definition_exists(self) -> None:
        """Test that .pre-commit-hooks.yaml exists and is valid."""
        hook_file = Path(".pre-commit-hooks.yaml")
        assert hook_file.exists(), ".pre-commit-hooks.yaml not found"

        # Validate YAML syntax
        import yaml

        with hook_file.open() as f:
            hooks = yaml.safe_load(f)

        assert isinstance(hooks, list)
        assert len(hooks) > 0

        # Verify hook configuration
        hook = hooks[0]
        assert hook["id"] == "markdown-token-limit"
        assert hook["entry"] == "mdtoken check"
        assert hook["language"] == "python"
        assert hook["files"] == r"\.md$"
        assert hook["pass_filenames"] is True

    def test_hook_entry_point_exists(self) -> None:
        """Test that the hook entry point (mdtoken check) is available."""
        result = subprocess.run(
            ["mdtoken", "check", "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "Check markdown files" in result.stdout

    def test_pre_commit_scenario(self) -> None:
        """Simulate how pre-commit would invoke the hook."""
        # Create a temp directory with a git repo
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Initialize git repo
            subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)

            # Create a markdown file
            md_file = repo_path / "test.md"
            md_file.write_text("# Test\n\nSmall file.")

            # Stage the file
            subprocess.run(["git", "add", "test.md"], cwd=repo_path, capture_output=True)

            # Simulate pre-commit calling mdtoken with the staged file
            result = subprocess.run(
                ["mdtoken", "check", str(md_file)],
                capture_output=True,
                text=True,
            )

            # Should pass
            assert result.returncode == 0

    def test_pre_commit_config_example(self) -> None:
        """Test that example .pre-commit-config.yaml fixture is valid."""
        fixture_path = Path("tests/fixtures/.pre-commit-config.yaml")

        if fixture_path.exists():
            import yaml

            with fixture_path.open() as f:
                config = yaml.safe_load(f)

            assert "repos" in config
            # Verify structure is valid for pre-commit
            assert isinstance(config["repos"], list)
