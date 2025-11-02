# API Reference

This document provides detailed documentation for using `mdtoken` programmatically in your Python code.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Classes](#core-classes)
  - [TokenCounter](#tokencounter)
  - [Config](#config)
  - [LimitEnforcer](#limitenforcer)
  - [FileMatcher](#filematcher)
  - [Reporter](#reporter)
- [Data Classes](#data-classes)
  - [Violation](#violation)
  - [EnforcementResult](#enforcementresult)
- [Complete Examples](#complete-examples)
- [Type Hints](#type-hints)

---

## Installation

```bash
pip install mdtoken
```

For development:

```bash
git clone https://github.com/applied-artificial-intelligence/mdtoken.git
cd mdtoken
pip install -e .
```

## Quick Start

Basic programmatic usage:

```python
from pathlib import Path
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer
from mdtoken.reporter import Reporter

# Load configuration
config = Config.from_file()

# Create enforcer
enforcer = LimitEnforcer(config)

# Check files
result = enforcer.check_files()

# Report results
reporter = Reporter(enforcer)
reporter.report(result, verbose=True)

# Get exit code
exit_code = reporter.get_exit_code(result, config.fail_on_exceed)
```

---

## Core Classes

### TokenCounter

Token counting functionality using the tiktoken library.

#### Constructor

```python
TokenCounter(encoding_name: str = "cl100k_base") -> None
```

**Parameters:**
- `encoding_name` (str): Name of tiktoken encoding to use. Default: `"cl100k_base"` (GPT-4/GPT-3.5-turbo)

**Supported Encodings:**
- `cl100k_base` - GPT-4, GPT-3.5-turbo, Claude 3/3.5
- `o200k_base` - GPT-4o
- `p50k_base` - Codex, text-davinci-003/002
- `r50k_base` - GPT-3 (davinci, curie, babbage, ada)

**Raises:**
- `ValueError`: If encoding name is not recognized by tiktoken

**Example:**

```python
from mdtoken.counter import TokenCounter

# Use default GPT-4 encoding
counter = TokenCounter()

# Use GPT-4o encoding
counter_4o = TokenCounter(encoding_name="o200k_base")
```

#### Methods

##### `count_tokens(text: str) -> int`

Count tokens in a text string.

**Parameters:**
- `text` (str): Text string to count tokens for

**Returns:**
- `int`: Number of tokens in the text

**Raises:**
- `TypeError`: If text is not a string
- `ValueError`: If text cannot be encoded

**Example:**

```python
counter = TokenCounter()
text = "# Hello World\nThis is a markdown file."
token_count = counter.count_tokens(text)
print(f"Token count: {token_count}")
```

##### `count_file_tokens(path: Path, encoding: str = "utf-8") -> int`

Count tokens in a file.

**Parameters:**
- `path` (Path): Path to file to count tokens for
- `encoding` (str): Text encoding to use when reading file. Default: `"utf-8"`

**Returns:**
- `int`: Number of tokens in the file

**Raises:**
- `FileNotFoundError`: If file does not exist
- `OSError`: If file cannot be read or is not a regular file
- `ValueError`: If file content cannot be encoded to tokens

**Example:**

```python
from pathlib import Path
from mdtoken.counter import TokenCounter

counter = TokenCounter()
file_path = Path("README.md")
token_count = counter.count_file_tokens(file_path)
print(f"{file_path}: {token_count} tokens")
```

---

### Config

Configuration loading and validation for mdtoken.

#### Constructor

```python
Config(
    default_limit: int = 4000,
    limits: Optional[Dict[str, int]] = None,
    exclude: Optional[List[str]] = None,
    total_limit: Optional[int] = None,
    fail_on_exceed: bool = True,
    encoding: Optional[str] = None,
    model: Optional[str] = None
) -> None
```

**Parameters:**
- `default_limit` (int): Default token limit for all markdown files. Default: 4000
- `limits` (Dict[str, int], optional): Per-file or per-pattern token limits
- `exclude` (List[str], optional): Glob patterns for files to exclude
- `total_limit` (int, optional): Total token limit across all files
- `fail_on_exceed` (bool): Whether to fail when limits are exceeded. Default: True
- `encoding` (str, optional): Tiktoken encoding name (e.g., "cl100k_base")
- `model` (str, optional): Model name for user-friendly config (e.g., "gpt-4")

**Note:** If both `encoding` and `model` are provided, `encoding` takes precedence.

**Supported Models:**
- `gpt-4` → `cl100k_base`
- `gpt-4o` → `o200k_base`
- `gpt-3.5-turbo` → `cl100k_base`
- `claude-3` → `cl100k_base`
- `claude-3.5` → `cl100k_base`
- `codex` → `p50k_base`
- `text-davinci-003` → `p50k_base`
- `text-davinci-002` → `p50k_base`
- `gpt-3` → `r50k_base`

**Raises:**
- `ConfigError`: If configuration values are invalid

**Example:**

```python
from mdtoken.config import Config

# Basic configuration
config = Config(default_limit=5000)

# With per-file limits
config = Config(
    default_limit=4000,
    limits={
        "README.md": 8000,
        ".claude/commands/**": 2000,
        ".claude/skills/**": 3000,
    },
    exclude=["archive/**"]
)

# Using model name
config = Config(model="gpt-4o")

# Using encoding directly
config = Config(encoding="o200k_base")
```

#### Class Methods

##### `from_file(config_path: Optional[Path] = None) -> Config`

Load configuration from a YAML file.

**Parameters:**
- `config_path` (Path, optional): Path to configuration file. If None, searches for `.mdtokenrc.yaml` in current directory.

**Returns:**
- `Config`: Config instance with loaded configuration

**Raises:**
- `ConfigError`: If file cannot be read or contains invalid YAML/config

**Example:**

```python
from pathlib import Path
from mdtoken.config import Config

# Load from default location (.mdtokenrc.yaml)
config = Config.from_file()

# Load from specific path
config = Config.from_file(Path("config/mdtoken.yaml"))
```

#### Instance Methods

##### `get_limit(file_path: str) -> int`

Get token limit for a specific file.

**Parameters:**
- `file_path` (str): Path to file (can be relative or absolute)

**Returns:**
- `int`: Token limit for the file

**Matching Priority:**
1. Exact path match
2. Pattern match (substring or endswith)
3. Default limit

**Example:**

```python
config = Config(
    default_limit=4000,
    limits={
        "README.md": 8000,
        ".claude/commands/**": 2000,
    }
)

print(config.get_limit("README.md"))  # 8000
print(config.get_limit(".claude/commands/setup.md"))  # 2000
print(config.get_limit("docs/guide.md"))  # 4000 (default)
```

##### `to_dict() -> Dict[str, Any]`

Convert configuration to dictionary.

**Returns:**
- `Dict[str, Any]`: Dictionary representation of configuration

**Example:**

```python
config = Config(default_limit=5000, model="gpt-4o")
config_dict = config.to_dict()
print(config_dict)
# {
#     'default_limit': 5000,
#     'limits': {},
#     'exclude': ['.git/**', 'node_modules/**', ...],
#     'total_limit': None,
#     'fail_on_exceed': True,
#     'encoding': 'o200k_base'
# }
```

#### Attributes

- `default_limit` (int): Default token limit
- `limits` (Dict[str, int]): Per-file/pattern limits
- `exclude` (List[str]): Exclusion patterns
- `total_limit` (Optional[int]): Total token limit
- `fail_on_exceed` (bool): Failure behavior
- `encoding` (str): Tiktoken encoding name

#### Default Exclusions

The following patterns are excluded by default:
- `.git/**`
- `node_modules/**`
- `venv/**`, `.venv/**`
- `build/**`, `dist/**`
- `__pycache__/**`

---

### LimitEnforcer

Enforces token limits on markdown files.

#### Constructor

```python
LimitEnforcer(
    config: Config,
    counter: Optional[TokenCounter] = None,
    matcher: Optional[FileMatcher] = None
) -> None
```

**Parameters:**
- `config` (Config): Configuration object
- `counter` (TokenCounter, optional): Token counter (creates default if not provided)
- `matcher` (FileMatcher, optional): File matcher (creates default if not provided)

**Example:**

```python
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer
from mdtoken.counter import TokenCounter

config = Config.from_file()

# With default counter and matcher
enforcer = LimitEnforcer(config)

# With custom counter
counter = TokenCounter(encoding_name="o200k_base")
enforcer = LimitEnforcer(config, counter=counter)
```

#### Methods

##### `check_files(patterns: Optional[List[str]] = None, check_files: Optional[List[Path]] = None) -> EnforcementResult`

Check files against token limits.

**Parameters:**
- `patterns` (List[str], optional): Glob patterns to match. Default: `["**/*.md"]`
- `check_files` (List[Path], optional): Specific files to check (used by pre-commit)

**Returns:**
- `EnforcementResult`: Result object with violations and statistics

**Example:**

```python
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer

config = Config.from_file()
enforcer = LimitEnforcer(config)

# Check all markdown files
result = enforcer.check_files()

# Check specific pattern
result = enforcer.check_files(patterns=["docs/**/*.md"])

# Check specific files (pre-commit mode)
from pathlib import Path
result = enforcer.check_files(check_files=[
    Path("README.md"),
    Path("CHANGELOG.md")
])
```

##### `get_suggestions(violation: Violation) -> List[str]`

Generate actionable suggestions for fixing a violation.

**Parameters:**
- `violation` (Violation): The violation to generate suggestions for

**Returns:**
- `List[str]`: List of suggestion strings

**Example:**

```python
result = enforcer.check_files()
for violation in result.violations:
    suggestions = enforcer.get_suggestions(violation)
    print(f"\nFile: {violation.file_path}")
    for suggestion in suggestions:
        print(f"  • {suggestion}")
```

#### Attributes

- `config` (Config): Configuration object
- `counter` (TokenCounter): Token counter
- `matcher` (FileMatcher): File matcher

---

### FileMatcher

Discovers and filters markdown files based on patterns.

#### Constructor

```python
FileMatcher(config: Config, root: Path = None) -> None
```

**Parameters:**
- `config` (Config): Configuration object
- `root` (Path, optional): Root directory for file discovery. Default: current directory

**Example:**

```python
from pathlib import Path
from mdtoken.config import Config
from mdtoken.matcher import FileMatcher

config = Config.from_file()

# Use current directory
matcher = FileMatcher(config)

# Use specific root
matcher = FileMatcher(config, root=Path("/path/to/project"))
```

#### Methods

##### `find_markdown_files(patterns: List[str] = None, check_files: List[Path] = None) -> List[Tuple[Path, int]]`

Find markdown files matching patterns.

**Parameters:**
- `patterns` (List[str], optional): Glob patterns to match. Default: `["**/*.md"]`
- `check_files` (List[Path], optional): Specific files to check instead of scanning

**Returns:**
- `List[Tuple[Path, int]]`: List of tuples (file_path, token_limit) for each matched file

**Example:**

```python
from mdtoken.config import Config
from mdtoken.matcher import FileMatcher

config = Config(
    default_limit=4000,
    limits={"README.md": 8000},
    exclude=["archive/**"]
)
matcher = FileMatcher(config)

# Find all markdown files
files = matcher.find_markdown_files()
for file_path, limit in files:
    print(f"{file_path}: limit={limit}")

# Find with pattern
files = matcher.find_markdown_files(patterns=["docs/**/*.md"])
```

#### Attributes

- `config` (Config): Configuration object
- `root` (Path): Root directory

---

### Reporter

Formats and displays enforcement results.

#### Constructor

```python
Reporter(
    enforcer: LimitEnforcer = None,
    output: TextIO = None,
    use_color: bool = True
) -> None
```

**Parameters:**
- `enforcer` (LimitEnforcer, optional): LimitEnforcer for generating suggestions
- `output` (TextIO, optional): Output stream. Default: stdout
- `use_color` (bool): Whether to use ANSI colors. Default: True (auto-detected)

**Example:**

```python
import sys
from mdtoken.enforcer import LimitEnforcer
from mdtoken.reporter import Reporter

enforcer = LimitEnforcer(config)

# Default reporter (stdout with color)
reporter = Reporter(enforcer)

# Custom output stream
with open("report.txt", "w") as f:
    reporter = Reporter(enforcer, output=f, use_color=False)
```

#### Methods

##### `report(result: EnforcementResult, verbose: bool = False) -> None`

Display enforcement results.

**Parameters:**
- `result` (EnforcementResult): Enforcement result to display
- `verbose` (bool): Whether to show detailed suggestions. Default: False

**Example:**

```python
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer
from mdtoken.reporter import Reporter

config = Config.from_file()
enforcer = LimitEnforcer(config)
result = enforcer.check_files()

reporter = Reporter(enforcer)
reporter.report(result, verbose=True)
```

##### `get_exit_code(result: EnforcementResult, fail_on_exceed: bool) -> int`

Determine appropriate exit code.

**Parameters:**
- `result` (EnforcementResult): Enforcement result
- `fail_on_exceed` (bool): Whether to exit with error on violations

**Returns:**
- `int`: Exit code (0 for success, 1 for failure)

**Example:**

```python
result = enforcer.check_files()
exit_code = reporter.get_exit_code(result, config.fail_on_exceed)
sys.exit(exit_code)
```

##### `format_summary_line(result: EnforcementResult) -> str`

Format a one-line summary of results.

**Parameters:**
- `result` (EnforcementResult): Enforcement result

**Returns:**
- `str`: One-line summary string

**Example:**

```python
result = enforcer.check_files()
summary = reporter.format_summary_line(result)
print(summary)
# Output: "✓ 42 files checked, 125,430 tokens total"
```

#### Attributes

- `enforcer` (Optional[LimitEnforcer]): LimitEnforcer for suggestions
- `output` (TextIO): Output stream
- `use_color` (bool): Whether ANSI colors are enabled

---

## Data Classes

### Violation

Represents a token limit violation.

#### Attributes

- `file_path` (Path): Path to the file that violated the limit
- `actual_tokens` (int): Actual number of tokens in the file
- `limit` (int): Token limit that was exceeded

#### Properties

##### `excess -> int`

Number of tokens over the limit.

```python
violation = Violation(file_path=Path("README.md"), actual_tokens=5000, limit=4000)
print(violation.excess)  # 1000
```

##### `percentage_over -> float`

Percentage over the limit.

```python
violation = Violation(file_path=Path("README.md"), actual_tokens=5000, limit=4000)
print(violation.percentage_over)  # 25.0
```

#### Example

```python
from pathlib import Path
from mdtoken.enforcer import Violation

violation = Violation(
    file_path=Path("docs/guide.md"),
    actual_tokens=6500,
    limit=5000
)

print(f"File: {violation.file_path}")
print(f"Tokens: {violation.actual_tokens} / {violation.limit}")
print(f"Excess: {violation.excess} ({violation.percentage_over:.1f}%)")
```

---

### EnforcementResult

Results from limit enforcement check.

#### Attributes

- `passed` (bool): Whether all files passed the limits
- `total_files` (int): Total number of files checked
- `total_tokens` (int): Total tokens across all files
- `violations` (List[Violation]): List of limit violations
- `total_limit_exceeded` (bool): Whether total_limit was exceeded. Default: False

#### Properties

##### `violation_count -> int`

Number of files with violations.

```python
result = enforcer.check_files()
print(f"Violations: {result.violation_count} / {result.total_files}")
```

#### Example

```python
from mdtoken.enforcer import LimitEnforcer, EnforcementResult

enforcer = LimitEnforcer(config)
result = enforcer.check_files()

if result.passed:
    print(f"✓ All {result.total_files} files passed!")
else:
    print(f"✗ {result.violation_count} files exceeded limits")
    for violation in result.violations:
        print(f"  - {violation.file_path}: {violation.excess} tokens over")
```

---

## Complete Examples

### Example 1: Simple Programmatic Check

```python
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer
from mdtoken.reporter import Reporter

# Load config from .mdtokenrc.yaml
config = Config.from_file()

# Create enforcer
enforcer = LimitEnforcer(config)

# Check all markdown files
result = enforcer.check_files()

# Display results
reporter = Reporter(enforcer)
reporter.report(result, verbose=True)

# Exit with appropriate code
import sys
sys.exit(reporter.get_exit_code(result, config.fail_on_exceed))
```

### Example 2: Custom Configuration and Specific Files

```python
from pathlib import Path
from mdtoken.config import Config
from mdtoken.counter import TokenCounter
from mdtoken.enforcer import LimitEnforcer

# Create custom configuration
config = Config(
    default_limit=5000,
    limits={
        "README.md": 10000,
        "docs/**": 8000,
        ".claude/commands/**": 2000,
    },
    exclude=["archive/**", "tmp/**"],
    model="gpt-4o"
)

# Create enforcer
enforcer = LimitEnforcer(config)

# Check specific files
files_to_check = [
    Path("README.md"),
    Path("docs/api.md"),
    Path(".claude/commands/setup.md")
]

result = enforcer.check_files(check_files=files_to_check)

# Process results
if result.passed:
    print(f"✓ All {result.total_files} files within limits")
    print(f"  Total tokens: {result.total_tokens:,}")
else:
    print(f"✗ Found {result.violation_count} violations:")
    for v in result.violations:
        print(f"  {v.file_path}: {v.actual_tokens:,} / {v.limit:,} tokens")
        print(f"    Over by: {v.excess:,} ({v.percentage_over:.1f}%)")
```

### Example 3: Token Counting Only

```python
from pathlib import Path
from mdtoken.counter import TokenCounter

# Create counter with GPT-4o encoding
counter = TokenCounter(encoding_name="o200k_base")

# Count tokens in a string
text = "# My Document\n\nThis is some content."
tokens = counter.count_tokens(text)
print(f"Text tokens: {tokens}")

# Count tokens in files
for md_file in Path(".").glob("*.md"):
    try:
        tokens = counter.count_file_tokens(md_file)
        print(f"{md_file.name}: {tokens:,} tokens")
    except Exception as e:
        print(f"{md_file.name}: Error - {e}")
```

### Example 4: Integration with CI/CD

```python
#!/usr/bin/env python3
"""CI script to check markdown token limits."""
import sys
from pathlib import Path
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer
from mdtoken.reporter import Reporter

def main():
    # Load configuration
    config_path = Path(".mdtokenrc.yaml")
    if not config_path.exists():
        print("ERROR: No .mdtokenrc.yaml found", file=sys.stderr)
        sys.exit(1)

    config = Config.from_file(config_path)

    # Run enforcement
    enforcer = LimitEnforcer(config)
    result = enforcer.check_files()

    # Report results
    reporter = Reporter(enforcer)
    reporter.report(result, verbose=True)

    # Generate JSON report for CI
    import json
    report_data = {
        "passed": result.passed,
        "total_files": result.total_files,
        "total_tokens": result.total_tokens,
        "violations": [
            {
                "file": str(v.file_path),
                "actual": v.actual_tokens,
                "limit": v.limit,
                "excess": v.excess
            }
            for v in result.violations
        ]
    }

    with open("token-report.json", "w") as f:
        json.dump(report_data, f, indent=2)

    # Exit with appropriate code
    sys.exit(reporter.get_exit_code(result, config.fail_on_exceed))

if __name__ == "__main__":
    main()
```

### Example 5: Custom Reporter

```python
import sys
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer, EnforcementResult
from mdtoken.reporter import Reporter

class SlackReporter(Reporter):
    """Custom reporter that formats results for Slack."""

    def format_slack_message(self, result: EnforcementResult) -> dict:
        """Format results as Slack message."""
        if result.passed:
            return {
                "text": ":white_check_mark: Token limits check passed",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*Token Limits Check - PASSED*\n"
                                f"• Files checked: {result.total_files}\n"
                                f"• Total tokens: {result.total_tokens:,}"
                            )
                        }
                    }
                ]
            }
        else:
            violations_text = "\n".join([
                f"• `{v.file_path}`: {v.actual_tokens:,} / {v.limit:,} tokens "
                f"({v.percentage_over:.1f}% over)"
                for v in result.violations[:5]  # Show first 5
            ])

            return {
                "text": ":x: Token limits check failed",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                f"*Token Limits Check - FAILED*\n"
                                f"• Files checked: {result.total_files}\n"
                                f"• Violations: {result.violation_count}\n"
                                f"• Total tokens: {result.total_tokens:,}\n\n"
                                f"*Top Violations:*\n{violations_text}"
                            )
                        }
                    }
                ]
            }

# Usage
config = Config.from_file()
enforcer = LimitEnforcer(config)
result = enforcer.check_files()

slack_reporter = SlackReporter(enforcer)
slack_message = slack_reporter.format_slack_message(result)
print(slack_message)
```

---

## Type Hints

All public APIs in mdtoken use type hints for better IDE support and type checking. Example with mypy:

```bash
# Install mypy
pip install mypy

# Type check your code
mypy your_script.py
```

Example type-checked script:

```python
from pathlib import Path
from typing import List, Tuple
from mdtoken.config import Config
from mdtoken.counter import TokenCounter
from mdtoken.enforcer import LimitEnforcer, EnforcementResult, Violation

def analyze_violations(
    config_path: Path,
    patterns: List[str]
) -> Tuple[int, List[Violation]]:
    """Analyze token violations in markdown files.

    Args:
        config_path: Path to configuration file
        patterns: Glob patterns to match

    Returns:
        Tuple of (total_tokens, violations)
    """
    config: Config = Config.from_file(config_path)
    enforcer: LimitEnforcer = LimitEnforcer(config)
    result: EnforcementResult = enforcer.check_files(patterns=patterns)

    return result.total_tokens, result.violations

# Type checker will validate this usage
total, violations = analyze_violations(
    config_path=Path(".mdtokenrc.yaml"),
    patterns=["docs/**/*.md"]
)
```

---

## Error Handling

### ConfigError

Raised when configuration is invalid or cannot be loaded.

```python
from mdtoken.config import Config, ConfigError

try:
    config = Config(default_limit=-1000)
except ConfigError as e:
    print(f"Configuration error: {e}")
```

### Token Counting Errors

```python
from mdtoken.counter import TokenCounter

counter = TokenCounter()

try:
    # Invalid encoding
    counter = TokenCounter(encoding_name="invalid_encoding")
except ValueError as e:
    print(f"Encoding error: {e}")

try:
    # Invalid file
    tokens = counter.count_file_tokens(Path("nonexistent.md"))
except FileNotFoundError as e:
    print(f"File error: {e}")
```

---

## Performance Considerations

- **Token counting**: ~0.31ms per file (~2000 tokens) with cl100k_base encoding
- **File scanning**: Linear O(n) with number of files
- **Memory usage**: Minimal - files processed individually
- **Caching**: Not implemented in v1.0.0 (files counted on each run)

For large repositories (100+ markdown files), typical runtime is < 100ms.

---

## Thread Safety

**Not thread-safe**: The current implementation is designed for single-threaded use. If you need concurrent processing, create separate instances for each thread:

```python
import concurrent.futures
from pathlib import Path
from mdtoken.config import Config
from mdtoken.counter import TokenCounter

def count_file(file_path: Path, config: Config) -> int:
    """Count tokens in a file (thread-safe)."""
    counter = TokenCounter(encoding_name=config.encoding)
    return counter.count_file_tokens(file_path)

# Parallel processing
config = Config.from_file()
files = list(Path(".").glob("**/*.md"))

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(
        lambda f: count_file(f, config),
        files
    ))
```

---

## See Also

- [README](../README.md) - Overview and quick start guide
- [Examples](examples.md) - Practical usage examples (coming soon)
- [Configuration Guide](../README.md#configuration) - Detailed configuration options
- [GitHub Repository](https://github.com/applied-artificial-intelligence/mdtoken) - Source code and issues

---

**API Version**: 1.0.0
**Last Updated**: 2025-11-02
