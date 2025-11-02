"""Tests for limit enforcement logic."""

import tempfile
from io import StringIO
from pathlib import Path

from mdtoken.config import Config
from mdtoken.counter import TokenCounter
from mdtoken.enforcer import EnforcementResult, LimitEnforcer, Violation
from mdtoken.matcher import FileMatcher
from mdtoken.reporter import Reporter


class TestViolation:
    """Test Violation dataclass."""

    def test_violation_creation(self) -> None:
        """Test creating a violation."""
        violation = Violation(file_path=Path("test.md"), actual_tokens=5000, limit=4000)

        assert violation.file_path == Path("test.md")
        assert violation.actual_tokens == 5000
        assert violation.limit == 4000

    def test_violation_excess(self) -> None:
        """Test excess calculation."""
        violation = Violation(file_path=Path("test.md"), actual_tokens=5000, limit=4000)
        assert violation.excess == 1000

    def test_violation_percentage(self) -> None:
        """Test percentage over calculation."""
        violation = Violation(file_path=Path("test.md"), actual_tokens=5000, limit=4000)
        assert violation.percentage_over == 25.0

    def test_violation_str(self) -> None:
        """Test string representation."""
        violation = Violation(file_path=Path("test.md"), actual_tokens=5000, limit=4000)
        string = str(violation)
        assert "test.md" in string
        assert "5000" in string
        assert "4000" in string
        assert "1000" in string


class TestEnforcementResult:
    """Test EnforcementResult dataclass."""

    def test_result_creation(self) -> None:
        """Test creating an enforcement result."""
        violations = [Violation(Path("test.md"), 5000, 4000)]
        result = EnforcementResult(
            passed=False, total_files=2, total_tokens=9000, violations=violations
        )

        assert result.passed is False
        assert result.total_files == 2
        assert result.total_tokens == 9000
        assert len(result.violations) == 1

    def test_violation_count(self) -> None:
        """Test violation count property."""
        violations = [
            Violation(Path("test1.md"), 5000, 4000),
            Violation(Path("test2.md"), 6000, 4000),
        ]
        result = EnforcementResult(
            passed=False, total_files=3, total_tokens=15000, violations=violations
        )

        assert result.violation_count == 2

    def test_passed_result(self) -> None:
        """Test result with no violations."""
        result = EnforcementResult(passed=True, total_files=3, total_tokens=10000, violations=[])

        assert result.passed is True
        assert result.violation_count == 0


class TestLimitEnforcerInitialization:
    """Test LimitEnforcer initialization."""

    def test_init_with_config(self) -> None:
        """Test initialization with config."""
        config = Config()
        enforcer = LimitEnforcer(config)

        assert enforcer.config == config
        assert isinstance(enforcer.counter, TokenCounter)
        assert isinstance(enforcer.matcher, FileMatcher)

    def test_init_with_custom_components(self) -> None:
        """Test initialization with custom counter and matcher."""
        config = Config()
        counter = TokenCounter()
        matcher = FileMatcher(config)

        enforcer = LimitEnforcer(config, counter=counter, matcher=matcher)

        assert enforcer.counter is counter
        assert enforcer.matcher is matcher

    def test_repr(self) -> None:
        """Test string representation."""
        config = Config()
        enforcer = LimitEnforcer(config)
        repr_str = repr(enforcer)

        assert "LimitEnforcer" in repr_str


class TestCheckFiles:
    """Test file checking logic."""

    def setup_method(self) -> None:
        """Create temporary directory with test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.root = Path(self.temp_dir)

        # Create test files with known content
        (self.root / "small.md").write_text("Hello, world!")  # ~4 tokens
        (self.root / "medium.md").write_text("This is a test. " * 100)  # ~500 tokens
        (self.root / "large.md").write_text("This is a test. " * 1000)  # ~5000 tokens

    def teardown_method(self) -> None:
        """Clean up temporary directory."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_all_files_pass(self) -> None:
        """Test when all files are within limits."""
        config = Config(default_limit=10000)  # High limit
        enforcer = LimitEnforcer(config, matcher=FileMatcher(config, root=self.root))

        result = enforcer.check_files()

        assert result.passed is True
        assert result.violation_count == 0
        assert result.total_files == 3

    def test_some_files_fail(self) -> None:
        """Test when some files exceed limits."""
        config = Config(default_limit=1000)  # Medium limit
        enforcer = LimitEnforcer(config, matcher=FileMatcher(config, root=self.root))

        result = enforcer.check_files()

        assert result.passed is False
        assert result.violation_count == 1  # Only large.md exceeds
        assert result.total_files == 3

    def test_all_files_fail(self) -> None:
        """Test when all files exceed limits."""
        config = Config(default_limit=1)  # Very low limit
        enforcer = LimitEnforcer(config, matcher=FileMatcher(config, root=self.root))

        result = enforcer.check_files()

        assert result.passed is False
        assert result.violation_count == 3
        assert result.total_files == 3

    def test_per_file_limits(self) -> None:
        """Test per-file limit enforcement."""
        config = Config(
            default_limit=10000,
            limits={"large.md": 1000},  # Only large.md has strict limit
        )
        enforcer = LimitEnforcer(config, matcher=FileMatcher(config, root=self.root))

        result = enforcer.check_files()

        assert result.passed is False
        assert result.violation_count == 1

        # Verify it's large.md that violated
        violation = result.violations[0]
        assert violation.file_path.name == "large.md"

    def test_total_limit_enforcement(self) -> None:
        """Test total token limit across all files."""
        config = Config(default_limit=10000, total_limit=1000)
        enforcer = LimitEnforcer(config, matcher=FileMatcher(config, root=self.root))

        result = enforcer.check_files()

        # Files individually pass, but total exceeds
        assert result.passed is False
        assert result.total_limit_exceeded is True
        assert result.total_tokens > 1000

    def test_check_specific_files(self) -> None:
        """Test checking specific files (pre-commit mode)."""
        config = Config(default_limit=1000)
        enforcer = LimitEnforcer(config, matcher=FileMatcher(config, root=self.root))

        # Check only large.md
        result = enforcer.check_files(check_files=[self.root / "large.md"])

        assert result.passed is False
        assert result.violation_count == 1
        assert result.total_files == 1

    def test_empty_file_list(self) -> None:
        """Test with no files to check."""
        config = Config()
        enforcer = LimitEnforcer(config, matcher=FileMatcher(config, root=Path("/nonexistent")))

        result = enforcer.check_files()

        assert result.passed is True
        assert result.violation_count == 0
        assert result.total_files == 0


class TestGetSuggestions:
    """Test suggestion generation."""

    def test_suggestions_for_high_excess(self) -> None:
        """Test suggestions for violations >50% over limit."""
        config = Config()
        enforcer = LimitEnforcer(config)

        violation = Violation(Path("test.md"), actual_tokens=8000, limit=4000)
        suggestions = enforcer.get_suggestions(violation)

        assert len(suggestions) > 0
        # Should suggest splitting file
        assert any("split" in s.lower() for s in suggestions)

    def test_suggestions_for_medium_excess(self) -> None:
        """Test suggestions for violations 20-50% over limit."""
        config = Config()
        enforcer = LimitEnforcer(config)

        violation = Violation(Path("test.md"), actual_tokens=5000, limit=4000)
        suggestions = enforcer.get_suggestions(violation)

        assert len(suggestions) > 0
        # Should suggest removing content
        assert any("remove" in s.lower() or "archive" in s.lower() for s in suggestions)

    def test_suggestions_for_low_excess(self) -> None:
        """Test suggestions for violations <20% over limit."""
        config = Config()
        enforcer = LimitEnforcer(config)

        violation = Violation(Path("test.md"), actual_tokens=4500, limit=4000)
        suggestions = enforcer.get_suggestions(violation)

        assert len(suggestions) > 0
        # Should suggest minor reduction
        assert any("minor" in s.lower() or "tighten" in s.lower() for s in suggestions)

    def test_readme_specific_suggestions(self) -> None:
        """Test README-specific suggestions."""
        config = Config()
        enforcer = LimitEnforcer(config)

        violation = Violation(Path("README.md"), actual_tokens=8000, limit=4000)
        suggestions = enforcer.get_suggestions(violation)

        # Should include README-specific advice
        assert any("README" in s or "docs" in s for s in suggestions)


class TestReporter:
    """Test Reporter formatting."""

    def test_reporter_init(self) -> None:
        """Test reporter initialization."""
        output = StringIO()
        reporter = Reporter(output=output, use_color=False)

        assert reporter.output is output
        assert reporter.use_color is False

    def test_success_report(self) -> None:
        """Test reporting successful check."""
        output = StringIO()
        reporter = Reporter(output=output, use_color=False)

        result = EnforcementResult(passed=True, total_files=3, total_tokens=10000, violations=[])

        reporter.report(result)
        output_text = output.getvalue()

        assert "within token limits" in output_text.lower()
        assert "Files checked: 3" in output_text
        assert "PASSED" in output_text

    def test_failure_report(self) -> None:
        """Test reporting check failures."""
        output = StringIO()
        config = Config()
        enforcer = LimitEnforcer(config)
        reporter = Reporter(enforcer=enforcer, output=output, use_color=False)

        violations = [Violation(Path("test.md"), 5000, 4000)]
        result = EnforcementResult(
            passed=False, total_files=2, total_tokens=9000, violations=violations
        )

        reporter.report(result)
        output_text = output.getvalue()

        assert "exceeding token limits" in output_text.lower()
        assert "test.md" in output_text
        assert "5000" in output_text
        assert "FAILED" in output_text

    def test_verbose_report_shows_suggestions(self) -> None:
        """Test that verbose mode shows suggestions."""
        output = StringIO()
        config = Config()
        enforcer = LimitEnforcer(config)
        reporter = Reporter(enforcer=enforcer, output=output, use_color=False)

        violations = [Violation(Path("test.md"), 8000, 4000)]
        result = EnforcementResult(
            passed=False, total_files=1, total_tokens=8000, violations=violations
        )

        reporter.report(result, verbose=True)
        output_text = output.getvalue()

        assert "Suggestions:" in output_text

    def test_get_exit_code_pass(self) -> None:
        """Test exit code for passing check."""
        reporter = Reporter(use_color=False)

        result = EnforcementResult(passed=True, total_files=3, total_tokens=10000, violations=[])

        assert reporter.get_exit_code(result, fail_on_exceed=True) == 0
        assert reporter.get_exit_code(result, fail_on_exceed=False) == 0

    def test_get_exit_code_fail_with_enforcement(self) -> None:
        """Test exit code for failing check with enforcement."""
        reporter = Reporter(use_color=False)

        violations = [Violation(Path("test.md"), 5000, 4000)]
        result = EnforcementResult(
            passed=False, total_files=2, total_tokens=9000, violations=violations
        )

        assert reporter.get_exit_code(result, fail_on_exceed=True) == 1

    def test_get_exit_code_fail_without_enforcement(self) -> None:
        """Test exit code for failing check without enforcement."""
        reporter = Reporter(use_color=False)

        violations = [Violation(Path("test.md"), 5000, 4000)]
        result = EnforcementResult(
            passed=False, total_files=2, total_tokens=9000, violations=violations
        )

        # Should return 0 (warning only) when fail_on_exceed is False
        assert reporter.get_exit_code(result, fail_on_exceed=False) == 0

    def test_format_summary_line_pass(self) -> None:
        """Test one-line summary for passing check."""
        reporter = Reporter(use_color=False)

        result = EnforcementResult(passed=True, total_files=3, total_tokens=10000, violations=[])

        summary = reporter.format_summary_line(result)

        assert "3 files checked" in summary
        assert "10,000 tokens" in summary

    def test_format_summary_line_fail(self) -> None:
        """Test one-line summary for failing check."""
        reporter = Reporter(use_color=False)

        violations = [Violation(Path("test.md"), 5000, 4000)]
        result = EnforcementResult(
            passed=False, total_files=2, total_tokens=9000, violations=violations
        )

        summary = reporter.format_summary_line(result)

        assert "1/2 files over limit" in summary
        assert "9,000 tokens" in summary


class TestEnforcerEncoding:
    """Test that enforcer uses encoding from config."""

    def test_enforcer_uses_config_encoding(self) -> None:
        """Test that LimitEnforcer passes config encoding to TokenCounter."""
        config = Config(encoding="o200k_base")
        enforcer = LimitEnforcer(config)

        # Verify that the counter was created with the correct encoding
        assert enforcer.counter.encoding_name == "o200k_base"

    def test_enforcer_uses_model_encoding(self) -> None:
        """Test that LimitEnforcer works with model-based config."""
        config = Config(model="gpt-4o")
        enforcer = LimitEnforcer(config)

        # Model gpt-4o should resolve to o200k_base encoding
        assert enforcer.counter.encoding_name == "o200k_base"

    def test_enforcer_default_encoding(self) -> None:
        """Test that LimitEnforcer uses default encoding when not specified."""
        config = Config()
        enforcer = LimitEnforcer(config)

        # Should use default cl100k_base encoding
        assert enforcer.counter.encoding_name == "cl100k_base"
