# Requirements: Markdown Token Limit Pre-Commit Hook

## Overview
Create an open-source pre-commit hook that enforces token count limits on markdown files to prevent context bloat in documentation-heavy projects.

## Functional Requirements

### Core Functionality
1. **Token Counting**
   - Accurately count tokens in markdown files using tiktoken (OpenAI's tokenizer)
   - Handle markdown syntax properly (code blocks, links, tables, etc.)
   - Performance: < 1 second for typical projects (5-10 files)
   - Accuracy: Within 5-10% of Claude's actual tokenization

2. **Configuration System**
   - Per-file token limits via glob patterns
   - Global project token limits (optional)
   - Path-specific overrides for special files
   - Exclude patterns for generated/archived content
   - Sensible defaults when no config present (10,000 tokens per file)

3. **Pre-commit Integration**
   - Standard pre-commit hook interface
   - Process only staged markdown files
   - Clear exit codes: 0 (pass), 1 (fail with violations)
   - Fast execution suitable for git workflow

4. **User Experience**
   - Clear, actionable error messages
   - Show how much over limit (e.g., "+234 tokens over")
   - Helpful suggestions for remediation
   - Optional verbose mode showing all file stats
   - Warning indicators for files approaching limits (>90%)

### Configuration Format

**File**: `.mdtokenrc.yaml` (YAML for broad compatibility)

```yaml
# Default limit for all markdown files
default_limit: 5000

# File-specific limits (glob patterns)
limits:
  "CLAUDE.md": 8000
  "README.md": 3000
  ".claude/memory/*.md": 2000
  ".claude/reference/**/*.md": 10000

# Exclude patterns
exclude:
  - "node_modules/**"
  - ".venv/**"
  - "**/.git/**"
  - "**/archive/**"

# Optional: Total project limit
total_limit: 50000

# Behavior
fail_on_exceed: true   # Fail commit if limits exceeded
show_stats: true       # Show token counts even when passing
```

**Alternative**: Support `pyproject.toml` for Python projects

### Pre-commit Configuration

Users add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/user/markdown-token-limit
    rev: v1.0.0
    hooks:
      - id: markdown-token-limit
        name: Check markdown token counts
        args: ['--config=.mdtokenrc.yaml']
```

## Non-Functional Requirements

### Performance
- **Speed**: Complete checks in < 1 second for typical projects
- **Scalability**: Handle projects with 100+ markdown files
- **Memory**: Reasonable memory usage (< 100MB for large projects)

### Reliability
- **Robustness**: Handle malformed markdown gracefully
- **Edge Cases**: Empty files, binary files, symlinks
- **Error Handling**: Never crash, always provide useful output

### Usability
- **Installation**: Single command: `pip install markdown-token-limit`
- **Configuration**: Works out-of-box with sensible defaults
- **Documentation**: Clear README with examples
- **Error Messages**: Actionable and helpful

### Maintainability
- **Testing**: Comprehensive test coverage (>80%)
- **Code Quality**: Type hints, linting, formatting
- **Documentation**: Inline docs and external guides

## Technical Architecture

### Technology Stack
- **Language**: Python 3.8+ (pre-commit ecosystem standard)
- **Token Counter**: tiktoken library (OpenAI's official tokenizer)
- **Configuration**: YAML (yaml library)
- **Testing**: pytest
- **Distribution**: PyPI package

### Repository Structure
```
markdown-token-limit/
├── .pre-commit-hooks.yaml    # Hook metadata
├── pyproject.toml             # Python packaging
├── README.md                  # Documentation
├── LICENSE                    # MIT or Apache 2.0
├── CHANGELOG.md               # Version history
├── src/
│   └── mdtoken/
│       ├── __init__.py
│       ├── cli.py            # CLI entry point
│       ├── counter.py        # Token counting logic
│       ├── config.py         # Configuration loading
│       └── checker.py        # Main checking logic
├── tests/
│   ├── test_counter.py
│   ├── test_config.py
│   ├── test_checker.py
│   └── fixtures/
│       ├── sample.md
│       └── .mdtokenrc.yaml
└── examples/
    └── .mdtokenrc.yaml
```

### Key Components

**CLI Entry Point** (`cli.py`):
- Parse command-line arguments
- Load configuration
- Process files
- Format output
- Set exit code

**Token Counter** (`counter.py`):
- Use tiktoken with cl100k_base encoding (GPT-4 tokenizer)
- Handle file reading and encoding
- Cache results if needed

**Configuration Loader** (`config.py`):
- Parse YAML configuration
- Apply glob patterns
- Merge with defaults
- Validate configuration

**Checker** (`checker.py`):
- Main orchestration logic
- Check files against limits
- Generate reports
- Return violations

## Output Examples

### Failure Output
```
Checking markdown token counts...

❌ CLAUDE.md: 5,234 tokens (limit: 5,000) [+234 tokens over]
   Suggestions:
   - Consider splitting into multiple files
   - Move historical content to archive
   - Compress verbose sections

✅ README.md: 1,245 tokens (limit: 3,000)
✅ .claude/memory/lessons.md: 1,876 tokens (limit: 2,000)

Summary: 1 file(s) exceed token limits
Total tokens: 8,355 / 50,000 project limit

Run 'mdtoken --help' for more information.
```

### Success Output
```
Checking markdown token counts...

✅ All markdown files within token limits
   Files checked: 3
   Total tokens: 8,121 / 50,000 project limit
```

### Verbose Output (--verbose flag)
```
Checking markdown token counts...

README.md: 1,245 tokens (limit: 3,000) [41% of limit]
CLAUDE.md: 4,876 tokens (limit: 5,000) [97% of limit] ⚠️ approaching limit
.claude/memory/lessons.md: 1,876 tokens (limit: 2,000) [93% of limit] ⚠️ approaching limit

✅ All files within limits
Total: 8,121 / 50,000 project limit (16% used)
```

## Acceptance Criteria

- [ ] Counts tokens accurately using tiktoken
- [ ] Loads configuration from `.mdtokenrc.yaml`
- [ ] Uses sensible defaults when no config present
- [ ] Supports per-file and global limits
- [ ] Supports glob patterns for file matching
- [ ] Supports exclude patterns
- [ ] Integrates with pre-commit framework
- [ ] Provides clear, actionable error messages
- [ ] Shows helpful suggestions when limits exceeded
- [ ] Has verbose mode for detailed stats
- [ ] Warns when files approach limits (>90%)
- [ ] Exits with correct codes (0/1)
- [ ] Performs checks in < 1 second
- [ ] Published to PyPI
- [ ] Has comprehensive README
- [ ] Has test coverage >80%
- [ ] Has example configuration

## MVP Scope (v1.0.0)

**Include**:
- Core token counting with tiktoken
- YAML configuration support
- Pre-commit hook integration
- Clear error messages and suggestions
- Per-file and total project limits
- Glob pattern matching
- Exclude patterns
- PyPI distribution
- Comprehensive documentation
- Test suite

**Defer to v1.1+**:
- Auto-fix/splitting functionality
- Advanced caching mechanisms
- IDE integrations
- Standalone GitHub Action
- Alternative tokenizers
- Multi-format support (rst, txt, etc.)

## Out of Scope

- Automated content compression or splitting (v2 feature)
- Real-time monitoring/watch mode
- Web UI or dashboard
- Cloud-based token counting service
- Support for non-markdown formats (v2 feature)

## Dependencies

### Runtime Dependencies
- Python 3.8+
- tiktoken (OpenAI's tokenizer)
- PyYAML (configuration parsing)
- Standard library: argparse, pathlib, glob

### Development Dependencies
- pytest (testing)
- pytest-cov (coverage)
- black (formatting)
- mypy (type checking)
- pre-commit (development workflow)

### External Dependencies
- pre-commit framework (users must have installed)
- Git (implicit requirement)

## Risks and Assumptions

### Risks
1. **Tokenization Accuracy**: tiktoken may not match Claude exactly
   - Mitigation: Within 5-10% is acceptable, document the limitation

2. **Performance**: Token counting could be slow for large files
   - Mitigation: tiktoken is quite fast, test with 100K+ token files

3. **Configuration Complexity**: Users may find YAML configuration hard
   - Mitigation: Provide clear examples and sensible defaults

4. **Pre-commit Adoption**: Not all projects use pre-commit
   - Mitigation: Support standalone CLI usage, document both modes

### Assumptions
1. Users have Python 3.8+ available
2. Users are familiar with pre-commit framework or can learn it
3. Token counting precision within 5-10% is acceptable
4. YAML is acceptable configuration format
5. PyPI distribution is sufficient (no need for conda, etc.)

## Open Questions

1. **License**: MIT or Apache 2.0? (Recommend MIT for simplicity)
2. **Tokenizer**: tiktoken sufficient or need alternatives? (tiktoken is fine for v1)
3. **Project Name**: `markdown-token-limit`, `mdtoken`, `md-token-check`? (Prefer `mdtoken` - short and clear)
4. **Repository Location**: Personal org or separate dedicated org? (Personal is fine to start)
5. **Cache Strategy**: Cache token counts for unchanged files? (Nice-to-have, defer to v1.1)

## Success Metrics

### Adoption Metrics
- 100+ stars on GitHub within 6 months
- 50+ PyPI downloads per week
- 5+ external contributors

### Quality Metrics
- Test coverage >80%
- Zero critical bugs in first 3 months
- < 5 open issues at any time

### Usage Metrics
- Works correctly on Factory project (primary use case)
- Works on ML4T book project
- Works on general projects (from user reports)
