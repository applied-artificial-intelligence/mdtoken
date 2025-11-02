# Exploration Summary: Markdown Token Limit Pre-Commit Hook

## Executive Summary

A standalone, open-source pre-commit hook that enforces token count limits on markdown files. This tool addresses a gap in the pre-commit ecosystem and solves a real problem: preventing markdown documentation from becoming too large and consuming excessive context in AI-assisted development workflows.

**Key Decision**: Build with Python + tiktoken for accuracy, speed, and ecosystem compatibility.

## Problem Statement

### The Challenge
- Markdown documentation files can grow unbounded without clear indicators
- Token counts (not lines or bytes) matter for AI context windows
- No existing tools enforce token limits during git workflow
- Manual monitoring is tedious and error-prone

### The Opportunity
- Fill gap in pre-commit hook ecosystem
- Open source tool with broad applicability
- Solves actual problem for Factory and ML4T projects
- Educational value for tokenization awareness

## Implementation Approach

### Technology Stack ✅

**Language: Python 3.8+**
- Pre-commit ecosystem standard
- Excellent tokenization libraries available
- Easy PyPI distribution
- Good tooling (pytest, black, mypy)

**Token Counter: tiktoken**
- OpenAI's official tokenizer (cl100k_base encoding)
- Fast: 1M+ tokens/second
- Accurate: Within 5-10% of Claude's tokenization
- Well-maintained, stable API
- No API calls required (local computation)

**Configuration: YAML**
- User-friendly, readable format
- Broader adoption than TOML (works for non-Python projects)
- Good Python library support (PyYAML)
- Familiar to pre-commit users

**Distribution: PyPI + GitHub**
- Standard `pip install mdtoken` installation
- GitHub for source and issues
- pre-commit hook via `.pre-commit-hooks.yaml`

### Architecture Design

```
User commits .md files
        ↓
Pre-commit framework detects staged .md files
        ↓
Calls mdtoken hook with file list
        ↓
mdtoken reads .mdtokenrc.yaml config
        ↓
For each file:
    - Read content
    - Count tokens with tiktoken
    - Check against limit (per-file or default)
    - Track violations
        ↓
Generate report with violations/warnings
        ↓
Exit 0 (pass) or 1 (fail)
        ↓
Git commit proceeds or is blocked
```

### Core Components

1. **CLI Entry** (`cli.py`):
   - Parse arguments (--config, --verbose, --help)
   - Orchestrate workflow
   - Format output
   - Set exit code

2. **Token Counter** (`counter.py`):
   - Load tiktoken encoding (cl100k_base)
   - Read markdown file
   - Count tokens
   - Cache encoding instance for performance

3. **Configuration** (`config.py`):
   - Load .mdtokenrc.yaml
   - Parse glob patterns
   - Apply file-specific limits
   - Merge with defaults

4. **Checker** (`checker.py`):
   - Match files to patterns
   - Apply limits
   - Collect violations
   - Generate statistics

### Configuration Design

**Default behavior** (no config file):
```yaml
default_limit: 10000  # Conservative default
fail_on_exceed: true
show_stats: false     # Only show on failure
```

**Full configuration example**:
```yaml
default_limit: 5000

limits:
  "CLAUDE.md": 8000
  "README.md": 3000
  ".claude/memory/*.md": 2000
  ".claude/reference/**/*.md": 10000

exclude:
  - "node_modules/**"
  - ".venv/**"
  - "**/archive/**"

total_limit: 50000
fail_on_exceed: true
show_stats: true
```

**Pattern matching priority**:
1. Exact path match
2. Most specific glob match
3. Default limit
4. Exclude patterns checked first

### User Experience Design

**Error message design** (actionable and helpful):
```
❌ CLAUDE.md: 5,234 tokens (limit: 5,000) [+234 tokens over]
   Suggestions:
   - Consider splitting into multiple files
   - Move historical content to archive
   - Compress verbose sections
```

**Warning indicators** (approaching limit):
```
CLAUDE.md: 4,876 tokens (limit: 5,000) [97% of limit] ⚠️ approaching limit
```

**Success output** (brief when passing):
```
✅ All markdown files within token limits
   Files checked: 3
   Total tokens: 8,121 / 50,000 project limit
```

**Verbose mode** (detailed stats):
```
README.md: 1,245 tokens (limit: 3,000) [41% of limit]
CLAUDE.md: 4,876 tokens (limit: 5,000) [97% of limit] ⚠️
```

## Repository Structure

```
mdtoken/                           # PyPI package name
├── .github/
│   └── workflows/
│       ├── test.yml              # Run tests on PR
│       └── publish.yml           # Publish to PyPI on tag
├── .pre-commit-hooks.yaml        # Hook definition
├── pyproject.toml                # Package metadata + build config
├── README.md                     # User documentation
├── LICENSE                       # MIT license
├── CHANGELOG.md                  # Version history
├── CONTRIBUTING.md               # Contributor guide
├── src/
│   └── mdtoken/
│       ├── __init__.py           # Package init + version
│       ├── __main__.py           # CLI entry (python -m mdtoken)
│       ├── cli.py                # Argument parsing + main
│       ├── counter.py            # Token counting logic
│       ├── config.py             # Configuration loading
│       ├── checker.py            # File checking logic
│       └── py.typed              # PEP 561 marker
├── tests/
│   ├── __init__.py
│   ├── test_counter.py           # Token counting tests
│   ├── test_config.py            # Configuration tests
│   ├── test_checker.py           # Checker logic tests
│   ├── test_cli.py               # CLI integration tests
│   └── fixtures/
│       ├── sample_small.md       # < limit
│       ├── sample_large.md       # > limit
│       └── .mdtokenrc.yaml       # Sample config
└── examples/
    ├── .mdtokenrc.yaml           # Example configuration
    └── .pre-commit-config.yaml   # Example pre-commit setup
```

## Performance Considerations

### Token Counting Speed
- tiktoken is very fast: ~1M+ tokens/second
- Typical markdown file: 1,000-10,000 tokens
- Expected time per file: < 10ms
- 10 files: < 100ms total
- Well within pre-commit acceptability (< 1 second)

### Optimization Strategies
1. **Lazy loading**: Load tiktoken encoding once, reuse
2. **Early exit**: Stop counting if file exceeds limit (optional)
3. **Parallel processing**: If >10 files, use multiprocessing (defer to v1.1)
4. **Caching**: Cache counts for unchanged files (defer to v1.1)

**For MVP (v1.0.0)**: Simple sequential processing is sufficient.

## Edge Cases & Error Handling

### Edge Cases Handled
1. **Empty files**: 0 tokens, always pass
2. **Binary files**: Skip with warning if matched
3. **Malformed markdown**: Count tokens anyway (don't fail on parse errors)
4. **Symlinks**: Follow symlinks, count actual content
5. **Very large files**: Handle gracefully, warn if >100K tokens
6. **No config file**: Use sensible defaults
7. **Missing limits for file**: Use default_limit
8. **Invalid YAML**: Exit with clear error message
9. **Invalid glob patterns**: Exit with clear error message
10. **No .md files staged**: Exit 0 with "No markdown files to check"

### Error Messages
- Configuration errors: Show YAML path and issue
- File read errors: Show filename and permission/encoding issue
- Token counting errors: Show filename, continue with other files
- Pattern matching errors: Show pattern and issue

## Testing Strategy

### Test Coverage Goals
- Unit tests: >85% coverage
- Integration tests: Happy path + key error scenarios
- Fixture-based tests: Sample markdown files of various sizes

### Test Categories

**Unit Tests** (`test_counter.py`):
- Token counting accuracy
- Edge cases (empty, binary, malformed)
- Performance benchmarks

**Unit Tests** (`test_config.py`):
- YAML loading
- Default application
- Glob pattern matching
- Exclude patterns
- Limit resolution

**Unit Tests** (`test_checker.py`):
- Violation detection
- Statistics calculation
- Report formatting

**Integration Tests** (`test_cli.py`):
- Full workflow with fixtures
- Exit codes
- Output formatting
- Error scenarios

### Test Fixtures
- `sample_small.md`: 500 tokens (well under limits)
- `sample_medium.md`: 4,500 tokens (approaching limit)
- `sample_large.md`: 6,000 tokens (over default 5,000)
- `sample_empty.md`: 0 tokens
- `.mdtokenrc.yaml`: Various limit configurations

## Distribution & Documentation

### PyPI Package
- **Name**: `mdtoken` (short, clear, available)
- **Version**: Start at 1.0.0 (follows semver)
- **Installation**: `pip install mdtoken`
- **CLI command**: `mdtoken`
- **Python package**: `import mdtoken`

### Pre-commit Integration
- **Hook ID**: `markdown-token-limit`
- **Language**: python
- **Entry point**: `mdtoken`
- **File types**: `markdown` (pre-commit will filter .md files)

### README Structure
1. **Overview**: What it does, why it exists
2. **Installation**: PyPI + pre-commit setup
3. **Quick Start**: Minimal example
4. **Configuration**: Full reference with examples
5. **Usage**: CLI flags, verbose mode, stats
6. **Output Examples**: Show actual output
7. **FAQ**: Common questions
8. **Contributing**: How to contribute
9. **License**: MIT

### Documentation Needs
- **README.md**: Primary user documentation
- **CONTRIBUTING.md**: Developer guide
- **CHANGELOG.md**: Version history
- **examples/**: Sample configurations
- **Inline docstrings**: All public functions
- **Type hints**: Complete type coverage

## MVP Scope (v1.0.0)

### Must Have ✅
- Token counting with tiktoken
- YAML configuration (.mdtokenrc.yaml)
- Per-file limits with glob patterns
- Total project limit (optional)
- Exclude patterns
- Sensible defaults
- Pre-commit integration
- Clear error messages + suggestions
- Warning for files approaching limits
- Verbose mode
- PyPI distribution
- Comprehensive README
- Test coverage >80%
- MIT license

### Nice to Have (Defer) 📋
- Auto-fix/splitting (v1.1)
- Token count caching (v1.1)
- Parallel processing (v1.1)
- GitHub Action (v1.2)
- IDE integrations (v2.0)
- Alternative tokenizers (v2.0)
- Support for RST, AsciiDoc (v2.0)
- Web dashboard (v3.0)

## Open Source Strategy

### License
**Recommendation: MIT**
- Most permissive
- Encourages maximum adoption
- Simple and well-understood
- Compatible with commercial use

### Repository
- **Host**: GitHub
- **Organization**: Personal (can transfer later if needed)
- **Name**: `mdtoken` or `markdown-token-limit`
- **Visibility**: Public from day 1

### Community Building
- **README badges**: Build status, coverage, PyPI version
- **Issue templates**: Bug report, feature request
- **Contributing guide**: Clear instructions
- **Code of Conduct**: Contributor Covenant
- **Examples**: Working sample configurations
- **Changelog**: Track all changes

### Release Process
1. Update CHANGELOG.md
2. Bump version in pyproject.toml
3. Tag release: `git tag v1.0.0`
4. Push tag: `git push --tags`
5. GitHub Action builds and publishes to PyPI
6. Create GitHub release with notes

## Next Steps

### Immediate Actions
1. ✅ Requirements documented (this file)
2. ⏭️ Create implementation plan with `/plan`
3. ⏭️ Set up repository structure
4. ⏭️ Implement core token counting
5. ⏭️ Add configuration system
6. ⏭️ Implement pre-commit hook
7. ⏭️ Write tests
8. ⏭️ Write documentation
9. ⏭️ Publish to PyPI
10. ⏭️ Test on Factory project
11. ⏭️ Announce and gather feedback

### Open Questions to Resolve
1. **Package name**: `mdtoken` vs `markdown-token-limit`?
   - Recommendation: `mdtoken` (shorter, clearer CLI command)

2. **Warning threshold**: 90% of limit or configurable?
   - Recommendation: 90% fixed for v1.0, configurable in v1.1

3. **Cache strategy**: File-based or in-memory?
   - Recommendation: Defer to v1.1, not needed for v1.0 performance

4. **Tokenizer**: Only tiktoken or support alternatives?
   - Recommendation: Only tiktoken for v1.0, alternatives in v2.0

5. **Standalone CLI**: Should it work without pre-commit?
   - Recommendation: Yes, support `mdtoken check` for standalone use

## Success Criteria

### Technical Success ✅
- Accurate token counting (within 5-10% of Claude)
- Fast execution (< 1 second for typical projects)
- Reliable pre-commit integration
- Good error handling and messages
- Comprehensive test coverage (>80%)

### Adoption Success 📈
- Used successfully on Factory project
- Used successfully on ML4T book project
- At least 5 external users within 3 months
- At least 1 external contributor within 6 months
- Positive feedback from users

### Quality Success 🏆
- Zero critical bugs in first month
- < 5 open issues at any time
- Documentation clear enough that users don't need support
- Code quality: Type hints, linting, formatting all passing
