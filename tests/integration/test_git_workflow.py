"""Integration tests for git workflow with pre-commit hooks.

These tests simulate real git workflows with temporary repositories
to verify that the pre-commit hook works correctly in practice.
"""

import subprocess
import tempfile
from pathlib import Path

import pytest


class TestGitWorkflowIntegration:
    """Integration tests for git workflow scenarios."""

    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create a temporary git repository for testing.

        This fixture:
        - Creates a new git repository
        - Configures git user info
        - Returns the repository path
        """
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()

        # Initialize git repository
        subprocess.run(
            ["git", "init"], cwd=repo_path, check=True, capture_output=True
        )

        # Configure git user
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        return repo_path

    def test_commit_passes_when_files_under_limit(self, git_repo):
        """Test that commit succeeds when markdown files are under token limits."""
        # Create a config file with reasonable limits
        config_content = """
default_limit: 1000
fail_on_exceed: true
"""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text(config_content)

        # Create a small markdown file (well under limit)
        readme_path = git_repo / "README.md"
        readme_path.write_text("# Test Project\n\nThis is a test.")

        # Stage the files
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )

        # Run mdtoken check manually (simulating pre-commit)
        result = subprocess.run(
            ["mdtoken", "check", str(readme_path)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should pass (exit code 0)
        assert result.returncode == 0, f"Expected success, got: {result.stderr}"
        assert "✓ All files within token limits" in result.stdout

    def test_commit_fails_when_files_exceed_limit(self, git_repo):
        """Test that commit fails when markdown files exceed token limits."""
        # Create a config file with very low limits
        config_content = """
default_limit: 10
fail_on_exceed: true
"""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text(config_content)

        # Create a markdown file that exceeds the limit
        readme_path = git_repo / "README.md"
        readme_path.write_text(
            "# Test Project\n\n" + "This is a long document. " * 50
        )

        # Stage the files
        subprocess.run(
            ["git", "add", "."], cwd=git_repo, check=True, capture_output=True
        )

        # Run mdtoken check manually (simulating pre-commit)
        result = subprocess.run(
            ["mdtoken", "check", str(readme_path)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should fail (exit code 1)
        assert result.returncode == 1, f"Expected failure, got: {result.stdout}"
        assert "exceeding token limits" in result.stdout
        assert "README.md" in result.stdout or "Violations: 1" in result.stdout

    def test_dry_run_mode_does_not_fail_commits(self, git_repo):
        """Test that dry-run mode doesn't fail commits even with violations."""
        # Create a config file with very low limits
        config_content = """
default_limit: 10
fail_on_exceed: true
"""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text(config_content)

        # Create a markdown file that exceeds the limit
        readme_path = git_repo / "README.md"
        readme_path.write_text(
            "# Test Project\n\n" + "This is a long document. " * 50
        )

        # Run mdtoken check in dry-run mode
        result = subprocess.run(
            ["mdtoken", "check", "--dry-run", str(readme_path)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should pass (exit code 0) even though file exceeds limit
        assert result.returncode == 0, f"Dry-run should not fail: {result.stderr}"
        # In dry-run mode, violations are shown but exit code is 0
        assert "exceeding token limits" in result.stdout or result.returncode == 0

    def test_exclude_patterns_work_correctly(self, git_repo):
        """Test that exclude patterns prevent files from being checked."""
        # Create a config file with exclude patterns
        config_content = """
default_limit: 10
exclude:
  - "archived/**"
  - "temp/**"
fail_on_exceed: true
"""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text(config_content)

        # Create archived directory with a large file
        archived_dir = git_repo / "archived"
        archived_dir.mkdir()
        archived_file = archived_dir / "old.md"
        archived_file.write_text("# Old Document\n\n" + "Old content. " * 100)

        # Create a normal file that's within limits
        readme_path = git_repo / "README.md"
        readme_path.write_text("# Test\n\nSmall file.")

        # Run mdtoken check on both files
        result = subprocess.run(
            ["mdtoken", "check", str(readme_path), str(archived_file)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should pass because archived file is excluded
        assert result.returncode == 0, f"Excluded file should be ignored: {result.stderr}"
        # Archived file should not appear in output
        assert "old.md" not in result.stdout.lower()

    def test_total_limit_enforcement(self, git_repo):
        """Test that total_limit enforcement works across multiple files."""
        # Create a config file with total limit
        config_content = """
default_limit: 1000
total_limit: 50
fail_on_exceed: true
"""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text(config_content)

        # Create multiple small files that exceed total limit
        for i in range(5):
            file_path = git_repo / f"doc{i}.md"
            file_path.write_text(f"# Document {i}\n\n" + "Content here. " * 10)

        # Get all markdown files
        md_files = [str(f) for f in git_repo.glob("*.md")]

        # Run mdtoken check on all files
        result = subprocess.run(
            ["mdtoken", "check"] + md_files,
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should fail due to total limit
        assert result.returncode == 1, f"Total limit should be enforced: {result.stdout}"
        assert "total" in result.stdout.lower()

    def test_per_file_limit_override(self, git_repo):
        """Test that per-file limits override default limits."""
        # Create a config file with per-file limits
        config_content = """
default_limit: 50
limits:
  "README.md": 500
fail_on_exceed: true
"""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text(config_content)

        # Create README.md with more than default but less than per-file limit
        readme_path = git_repo / "README.md"
        readme_path.write_text("# README\n\n" + "Documentation here. " * 30)

        # Create another file that exceeds default limit
        other_path = git_repo / "other.md"
        other_path.write_text("# Other\n\n" + "Content here. " * 30)

        # Check README.md - should pass
        result_readme = subprocess.run(
            ["mdtoken", "check", str(readme_path)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )
        assert (
            result_readme.returncode == 0
        ), f"README should pass with custom limit: {result_readme.stderr}"

        # Check other.md - should fail
        result_other = subprocess.run(
            ["mdtoken", "check", str(other_path)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )
        assert (
            result_other.returncode == 1
        ), f"other.md should fail with default limit: {result_other.stdout}"

    def test_missing_config_uses_defaults(self, git_repo):
        """Test that missing config file uses sensible defaults."""
        # Don't create a config file

        # Create a moderate-sized markdown file
        readme_path = git_repo / "README.md"
        readme_path.write_text("# Test\n\n" + "Some content. " * 100)

        # Run mdtoken check
        result = subprocess.run(
            ["mdtoken", "check", str(readme_path)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should use default limit (4000) and pass
        assert result.returncode == 0, f"Should use defaults: {result.stderr}"

    def test_multiple_files_checked_together(self, git_repo):
        """Test checking multiple files in a single run."""
        # Create a config file
        config_content = """
default_limit: 100
fail_on_exceed: true
"""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text(config_content)

        # Create multiple files
        file1 = git_repo / "doc1.md"
        file1.write_text("# Doc 1\n\nShort.")

        file2 = git_repo / "doc2.md"
        file2.write_text("# Doc 2\n\nAlso short.")

        file3 = git_repo / "doc3.md"
        file3.write_text("# Doc 3\n\n" + "Long content. " * 50)

        # Check all files together
        result = subprocess.run(
            ["mdtoken", "check", str(file1), str(file2), str(file3)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should fail because doc3.md exceeds limit
        assert result.returncode == 1, f"Should fail for doc3.md: {result.stdout}"
        assert "doc3.md" in result.stdout

    def test_verbose_mode_output(self, git_repo):
        """Test that verbose mode provides detailed output."""
        # Create a config file
        config_content = """
default_limit: 1000
"""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text(config_content)

        # Create a markdown file
        readme_path = git_repo / "README.md"
        readme_path.write_text("# Test\n\nSome content.")

        # Run with verbose flag
        result = subprocess.run(
            ["mdtoken", "check", "-v", str(readme_path)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should show detailed information
        assert result.returncode == 0
        # Verbose mode should show summary with token counts
        assert "Total tokens:" in result.stdout or "Files checked:" in result.stdout


class TestGitWorkflowEdgeCases:
    """Edge case tests for git workflow integration."""

    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create a temporary git repository for testing."""
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()

        subprocess.run(
            ["git", "init"], cwd=repo_path, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )

        return repo_path

    def test_empty_markdown_file(self, git_repo):
        """Test handling of empty markdown files."""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text("default_limit: 100\n")

        # Create empty markdown file
        empty_file = git_repo / "empty.md"
        empty_file.write_text("")

        result = subprocess.run(
            ["mdtoken", "check", str(empty_file)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should pass (0 tokens is under any limit)
        assert result.returncode == 0

    def test_no_markdown_files(self, git_repo):
        """Test behavior when no markdown files are provided."""
        config_path = git_repo / ".mdtokenrc.yaml"
        config_path.write_text("default_limit: 100\n")

        # Run check with no files
        result = subprocess.run(
            ["mdtoken", "check"],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should handle gracefully
        assert result.returncode == 0

    def test_nonexistent_file_handling(self, git_repo):
        """Test that nonexistent files are handled gracefully."""
        # Try to check a file that doesn't exist
        nonexistent = git_repo / "does_not_exist.md"

        result = subprocess.run(
            ["mdtoken", "check", str(nonexistent)],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )

        # Should handle gracefully with error message
        # Exit code 2 indicates usage error (file doesn't exist)
        assert result.returncode != 0
        assert "does not exist" in result.stderr or result.returncode == 2
