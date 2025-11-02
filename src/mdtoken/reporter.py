"""Reporting and output formatting for mdtoken."""

import sys
from typing import TextIO

from mdtoken.enforcer import EnforcementResult, LimitEnforcer, Violation


class Reporter:
    """Formats and displays enforcement results.

    Attributes:
        enforcer: LimitEnforcer for generating suggestions
        output: Output stream (defaults to stdout)
        use_color: Whether to use ANSI colors in output
    """

    # ANSI color codes
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"

    def __init__(
        self,
        enforcer: LimitEnforcer = None,
        output: TextIO = None,
        use_color: bool = True,
    ) -> None:
        """Initialize reporter.

        Args:
            enforcer: LimitEnforcer for generating suggestions
            output: Output stream (defaults to stdout)
            use_color: Whether to use ANSI colors (auto-detected if not specified)
        """
        self.enforcer = enforcer
        self.output = output or sys.stdout
        # Auto-detect color support
        if use_color:
            self.use_color = self.output.isatty()
        else:
            self.use_color = False

    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if color is enabled.

        Args:
            text: Text to colorize
            color: ANSI color code

        Returns:
            Colorized text or plain text if colors disabled
        """
        if self.use_color:
            return f"{color}{text}{self.RESET}"
        return text

    def report(self, result: EnforcementResult, verbose: bool = False) -> None:
        """Display enforcement results.

        Args:
            result: Enforcement result to display
            verbose: Whether to show detailed suggestions
        """
        # Header
        if result.passed:
            self._print_success(result)
        else:
            self._print_failures(result, verbose)

        # Summary
        self._print_summary(result)

    def _print_success(self, result: EnforcementResult) -> None:
        """Print success message."""
        check_mark = self._colorize("✓", self.GREEN)
        message = self._colorize("All files within token limits!", self.GREEN)
        self.output.write(f"{check_mark} {message}\n")

    def _print_failures(self, result: EnforcementResult, verbose: bool) -> None:
        """Print failure messages with violations."""
        # Header
        cross = self._colorize("✗", self.RED)
        message = self._colorize(
            f"Found {result.violation_count} file(s) exceeding token limits:", self.RED
        )
        self.output.write(f"{cross} {message}\n\n")

        # List each violation
        for i, violation in enumerate(result.violations, 1):
            self._print_violation(violation, i, verbose)

        # Total limit violation if applicable
        if result.total_limit_exceeded:
            self._print_total_limit_violation(result)

    def _print_violation(self, violation: Violation, number: int, verbose: bool) -> None:
        """Print details for a single violation.

        Args:
            violation: The violation to print
            number: Violation number
            verbose: Whether to show suggestions
        """
        # File header
        file_str = self._colorize(str(violation.file_path), self.BOLD)
        self.output.write(f"{number}. {file_str}\n")

        # Stats
        actual = self._colorize(str(violation.actual_tokens), self.RED)
        limit = self._colorize(str(violation.limit), self.YELLOW)
        excess = self._colorize(str(violation.excess), self.RED)
        percentage = self._colorize(f"{violation.percentage_over:.1f}%", self.RED)

        self.output.write(f"   Tokens: {actual} / {limit}\n")
        self.output.write(f"   Over by: {excess} tokens ({percentage})\n")

        # Suggestions if verbose
        if verbose and self.enforcer:
            suggestions = self.enforcer.get_suggestions(violation)
            if suggestions:
                self.output.write(f"\n   {self._colorize('Suggestions:', self.BLUE)}\n")
                for suggestion in suggestions[:3]:  # Show top 3
                    self.output.write(f"   • {suggestion}\n")

        self.output.write("\n")

    def _print_total_limit_violation(self, result: EnforcementResult) -> None:
        """Print total limit violation warning."""
        warning = self._colorize("⚠", self.YELLOW)
        message = self._colorize(
            f"Total tokens ({result.total_tokens}) exceeds total_limit "
            f"({self.enforcer.config.total_limit if self.enforcer else 'N/A'})",
            self.YELLOW,
        )
        self.output.write(f"{warning} {message}\n\n")

    def _print_summary(self, result: EnforcementResult) -> None:
        """Print summary statistics."""
        self.output.write(self._colorize("Summary:", self.BOLD) + "\n")
        self.output.write(f"  Files checked: {result.total_files}\n")
        self.output.write(f"  Total tokens: {result.total_tokens:,}\n")
        self.output.write(f"  Violations: {result.violation_count}\n")

        if result.passed:
            status = self._colorize("PASSED", self.GREEN)
        else:
            status = self._colorize("FAILED", self.RED)

        self.output.write(f"  Status: {status}\n")

    def get_exit_code(self, result: EnforcementResult, fail_on_exceed: bool) -> int:
        """Determine appropriate exit code.

        Args:
            result: Enforcement result
            fail_on_exceed: Whether to exit with error on violations

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        if result.passed:
            return 0

        if fail_on_exceed:
            return 1

        # If fail_on_exceed is False, we still warn but exit 0
        return 0

    def format_summary_line(self, result: EnforcementResult) -> str:
        """Format a one-line summary of results.

        Args:
            result: Enforcement result

        Returns:
            One-line summary string
        """
        if result.passed:
            return f"✓ {result.total_files} files checked, {result.total_tokens:,} tokens total"
        else:
            return (
                f"✗ {result.violation_count}/{result.total_files} files over limit, "
                f"{result.total_tokens:,} tokens total"
            )
