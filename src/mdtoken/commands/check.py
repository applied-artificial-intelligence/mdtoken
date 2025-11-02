"""Check command implementation."""
from pathlib import Path
from typing import List, Optional


def check_files(
    files: List[str],
    config_path: str = '.mdtokenrc.yaml',
    dry_run: bool = False
) -> int:
    """
    Check markdown files against token count limits.

    Args:
        files: List of file paths to check
        config_path: Path to configuration file
        dry_run: If True, don't fail on violations

    Returns:
        Exit code: 0 for success, 1 for violations
    """
    # Placeholder implementation
    # Will be replaced with actual token counting logic in TASK-004-007

    print(f"Checking {len(files) if files else 0} files...")
    print(f"Using config: {config_path}")

    if dry_run:
        print("Dry run mode: will not fail on violations")

    # TODO: Implement actual checking logic
    # 1. Load configuration (TASK-005)
    # 2. Match files if none provided (TASK-006)
    # 3. Count tokens for each file (TASK-004)
    # 4. Enforce limits and report violations (TASK-007)

    return 0
