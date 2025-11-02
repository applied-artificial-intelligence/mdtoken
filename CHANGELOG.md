# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-02

### Added

#### Core Functionality
- **Token counting engine** using tiktoken library with cl100k_base encoding (GPT-4/GPT-3.5-turbo)
- **Configuration system** with `.mdtokenrc.yaml` support for project-specific token limits
- **Multi-model support** with configurable encodings:
  - GPT-4 and GPT-3.5-turbo (`cl100k_base`)
  - GPT-4o (`o200k_base`)
  - Claude 3 and Claude 3.5 (`cl100k_base` approximation)
  - Codex and text-davinci models (`p50k_base`)
  - GPT-3 models (`r50k_base`)
- **File matching system** with glob patterns and exclude rules
- **Flexible limit configuration**:
  - Default limit for all markdown files
  - Per-file or per-pattern limits
  - Total aggregate token limit
  - Customizable violation handling (fail or warn)

#### Command-Line Interface
- `mdtoken check` - Check markdown files against token limits
- `mdtoken --version` - Display version information
- `mdtoken --help` - Display usage information
- `--config` flag for custom configuration file path
- `--verbose` flag for detailed output
- Support for explicit file arguments and stdin file lists

#### Pre-commit Integration
- Pre-commit hook definition (`.pre-commit-hooks.yaml`)
- Hook ID: `markdown-token-limit`
- Automatic detection and checking of staged markdown files
- Proper exit codes for pre-commit framework integration
- Support for `pass_filenames` mode

#### Quality Assurance
- **182 comprehensive unit tests** with 84% code coverage
- **Integration tests** simulating real git workflows
- **Edge case handling** for empty files, large files, encoding issues
- **Performance benchmarks** (5 files < 500ms, 10 files < 1000ms, 100 files < 5000ms)
- **CI/CD pipeline** with GitHub Actions:
  - Multi-version Python testing (3.8, 3.9, 3.10, 3.11, 3.12)
  - Automated linting (ruff, black)
  - Type checking (mypy)
  - Coverage reporting

#### Documentation
- **Comprehensive README** with installation, usage, and troubleshooting
- **API documentation** (`docs/api.md`) for programmatic usage:
  - TokenCounter, Config, LimitEnforcer, FileMatcher, Reporter classes
  - 50+ code examples
  - Type hints reference
  - Error handling guide
- **Usage examples** (`docs/examples.md`):
  - 6 project-specific configurations
  - 4 common workflows (pre-commit, CI/CD, manual, automated)
  - 3 advanced usage patterns
  - 2 migration scenarios
  - Best practices guide
- **Troubleshooting guide** (`docs/troubleshooting.md`):
  - Installation issues
  - Configuration problems
  - Pre-commit hook debugging
  - Token counting explanations
  - Performance optimization
  - CI/CD integration help
  - 15+ common error messages with solutions
- **FAQ** (`docs/faq.md`):
  - 18 frequently asked questions
  - Accuracy explanations
  - Compatibility information
  - Usage guidance
  - Configuration options

#### Infrastructure
- **Python package structure** following modern standards
- **PyPI packaging** with proper metadata and classifiers
- **MIT License** for open-source use
- **Development environment** with:
  - Virtual environment support
  - Requirements files for core and dev dependencies
  - Makefile for common tasks
  - Code quality tools (black, ruff, mypy)
  - Testing framework (pytest, pytest-cov)

### Features Summary

**What mdtoken does**:
- Prevents context window bloat by enforcing token limits on markdown files
- Integrates seamlessly with pre-commit framework for automated checks
- Provides accurate token counting using the same tokenizer as GPT models
- Offers flexible configuration for different project needs
- Delivers clear, actionable feedback on limit violations

**Use cases**:
- AI-assisted development (Claude Code, GitHub Copilot, Cursor)
- Documentation management for AI tools
- Context window optimization
- Team standardization of documentation size
- Prevention of silently truncated context

**Key metrics**:
- 182 tests, 84% coverage
- Supports Python 3.8+
- Performance: < 1s for typical projects (5-10 files)
- 5 supported tokenizer encodings
- 1,960 lines of documentation

### Technical Details

**Core Dependencies**:
- `tiktoken>=0.5.0` - Token counting
- `PyYAML>=6.0` - Configuration parsing
- `click>=8.0.0` - CLI framework

**Development Status**: Beta (stable for production use)

**Platform Support**: Linux, macOS, Windows

**Integration Points**:
- Pre-commit framework
- GitHub Actions / GitLab CI / Jenkins
- Direct CLI invocation
- Python programmatic API

### Quality Gates Passed

✅ Foundation Complete
  - Project builds and installs with pip
  - CLI can be invoked
  - Development tools configured

✅ Core Implementation Complete
  - Token counting accurate (verified with test files)
  - Configuration loading works
  - Limit enforcement produces correct violations

✅ Testing Complete
  - Test coverage >80%
  - All tests passing
  - CI/CD green
  - Performance benchmarks met

✅ Documentation Complete
  - README comprehensive
  - API documentation complete
  - Examples and troubleshooting available
  - FAQ covers common questions

✅ Release Ready
  - PyPI packaging validated
  - CHANGELOG current
  - All quality gates passed
  - Repository configured

### Known Limitations (Deferred to v1.1+)

- No token count caching (files re-counted on each run)
- Sequential processing only (no parallelization)
- No auto-fix suggestions or file splitting
- No standalone GitHub Action (use pre-commit instead)
- No nested configuration file support

### Migration Notes

**From manual token checking**:
- Install mdtoken via pip
- Create `.mdtokenrc.yaml` with desired limits
- Add to `.pre-commit-config.yaml` or use CLI directly

**From other linters**:
- mdtoken complements (not replaces) traditional markdown linters
- Use alongside markdownlint or remark-lint for complete coverage

### Credits

This project was developed with AI assistance using Claude Code.

**Contributors**:
- Stefan Rummer - Initial implementation and design

**Acknowledgments**:
- OpenAI tiktoken library for accurate token counting
- Pre-commit framework for git hook infrastructure
- Claude Code for AI-assisted development workflow

---

[1.0.0]: https://github.com/applied-artificial-intelligence/mdtoken/releases/tag/v1.0.0
