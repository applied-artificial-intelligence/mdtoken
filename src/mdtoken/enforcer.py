"""Limit enforcement logic for mdtoken."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from mdtoken.config import Config
from mdtoken.counter import TokenCounter
from mdtoken.matcher import FileMatcher


@dataclass
class Violation:
    """Represents a token limit violation.

    Attributes:
        file_path: Path to the file that violated the limit
        actual_tokens: Actual number of tokens in the file
        limit: Token limit that was exceeded
        excess: Number of tokens over the limit
    """

    file_path: Path
    actual_tokens: int
    limit: int

    @property
    def excess(self) -> int:
        """Calculate tokens over the limit."""
        return self.actual_tokens - self.limit

    @property
    def percentage_over(self) -> float:
        """Calculate percentage over the limit."""
        return (self.excess / self.limit) * 100

    def __str__(self) -> str:
        """String representation of violation."""
        return (
            f"{self.file_path}: {self.actual_tokens} tokens "
            f"(limit: {self.limit}, over by {self.excess})"
        )


@dataclass
class EnforcementResult:
    """Results from limit enforcement check.

    Attributes:
        passed: Whether all files passed the limits
        total_files: Total number of files checked
        total_tokens: Total tokens across all files
        violations: List of limit violations
        total_limit_exceeded: Whether total_limit was exceeded (if configured)
    """

    passed: bool
    total_files: int
    total_tokens: int
    violations: List[Violation]
    total_limit_exceeded: bool = False

    @property
    def violation_count(self) -> int:
        """Number of files with violations."""
        return len(self.violations)


class LimitEnforcer:
    """Enforces token limits on markdown files.

    Attributes:
        config: Configuration with limits
        counter: Token counter
        matcher: File matcher
    """

    def __init__(
        self,
        config: Config,
        counter: Optional[TokenCounter] = None,
        matcher: Optional[FileMatcher] = None,
    ) -> None:
        """Initialize limit enforcer.

        Args:
            config: Configuration object
            counter: Token counter (creates default if not provided)
            matcher: File matcher (creates default if not provided)
        """
        self.config = config
        self.counter = counter or TokenCounter()
        self.matcher = matcher or FileMatcher(config)

    def check_files(
        self, patterns: Optional[List[str]] = None, check_files: Optional[List[Path]] = None
    ) -> EnforcementResult:
        """Check files against token limits.

        Args:
            patterns: Glob patterns to match (defaults to ["**/*.md"])
            check_files: Specific files to check (used by pre-commit)

        Returns:
            EnforcementResult with violations and statistics
        """
        # Find files to check
        files_with_limits = self.matcher.find_markdown_files(
            patterns=patterns, check_files=check_files
        )

        violations: List[Violation] = []
        total_tokens = 0

        # Check each file
        for file_path, limit in files_with_limits:
            try:
                token_count = self.counter.count_file_tokens(file_path)
                total_tokens += token_count

                # Check if file exceeds its limit
                if token_count > limit:
                    violations.append(
                        Violation(file_path=file_path, actual_tokens=token_count, limit=limit)
                    )
            except Exception:
                # If we can't count tokens, treat as a violation
                violations.append(
                    Violation(
                        file_path=file_path,
                        actual_tokens=0,  # Unknown
                        limit=limit,
                    )
                )

        # Check total limit if configured
        total_limit_exceeded = False
        if self.config.total_limit is not None:
            if total_tokens > self.config.total_limit:
                total_limit_exceeded = True

        # Determine if check passed
        passed = len(violations) == 0 and not total_limit_exceeded

        return EnforcementResult(
            passed=passed,
            total_files=len(files_with_limits),
            total_tokens=total_tokens,
            violations=violations,
            total_limit_exceeded=total_limit_exceeded,
        )

    def get_suggestions(self, violation: Violation) -> List[str]:
        """Generate actionable suggestions for fixing a violation.

        Args:
            violation: The violation to generate suggestions for

        Returns:
            List of suggestion strings
        """
        suggestions = []
        excess = violation.excess
        percentage = violation.percentage_over

        # Suggest based on severity
        if percentage > 50:
            suggestions.append("Consider splitting this file into multiple smaller files")
            suggestions.append(f"Target: reduce by ~{excess} tokens to get under the limit")
        elif percentage > 20:
            suggestions.append("Review content and remove unnecessary sections")
            suggestions.append("Consider moving older content to an archived directory")
        else:
            suggestions.append("Minor reduction needed - review and tighten content")

        # Generic suggestions
        suggestions.append("Remove redundant explanations or examples")
        suggestions.append("Consider using more concise language")

        # File-specific suggestions
        if "README" in str(violation.file_path):
            suggestions.append("Move detailed documentation to separate docs/ files")
            suggestions.append("Keep README high-level and link to detailed docs")

        return suggestions

    def __repr__(self) -> str:
        """String representation of LimitEnforcer."""
        return f"LimitEnforcer(config={self.config})"
