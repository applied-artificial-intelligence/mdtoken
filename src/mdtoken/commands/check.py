"""Check command implementation."""
from pathlib import Path
from typing import List, Optional

from mdtoken.config import Config, ConfigError
from mdtoken.enforcer import LimitEnforcer
from mdtoken.reporter import Reporter


def check_files(
    files: Optional[List[str]] = None,
    config_path: str = ".mdtokenrc.yaml",
    dry_run: bool = False,
    verbose: bool = False,
) -> int:
    """Check markdown files against token count limits.

    Args:
        files: List of file paths to check (None to check all)
        config_path: Path to configuration file
        dry_run: If True, don't fail on violations
        verbose: Show detailed suggestions

    Returns:
        Exit code: 0 for success, 1 for violations
    """
    try:
        # Load configuration
        config = Config.from_file(Path(config_path) if config_path else None)

        # Override fail_on_exceed if dry_run
        if dry_run:
            config.fail_on_exceed = False

        # Create enforcer and reporter
        enforcer = LimitEnforcer(config)
        reporter = Reporter(enforcer=enforcer)

        # Convert file strings to Path objects if provided
        check_files_list = None
        if files:
            check_files_list = [Path(f) for f in files]

        # Check files
        result = enforcer.check_files(check_files=check_files_list)

        # Report results
        reporter.report(result, verbose=verbose)

        # Return exit code
        return reporter.get_exit_code(result, config.fail_on_exceed)

    except ConfigError as e:
        print(f"Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
