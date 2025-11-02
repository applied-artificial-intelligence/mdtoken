# mdtoken - Markdown Token Limit Pre-commit Hook

[![Tests](https://github.com/stefanrmmr/mdtoken/actions/workflows/test.yml/badge.svg)](https://github.com/stefanrmmr/mdtoken/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/stefanrmmr/mdtoken/branch/main/graph/badge.svg)](https://codecov.io/gh/stefanrmmr/mdtoken)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A pre-commit hook that enforces token count limits on markdown files to prevent unbounded growth and context window bloat in AI-assisted development workflows.

## Problem

Markdown documentation files (like `CLAUDE.md`, memory files, project docs) grow unbounded over time, consuming valuable AI context windows. Manual monitoring is tedious and error-prone.

## Solution

Automated token counting checks during the git workflow with clear, actionable feedback when limits are exceeded.

## Features (Planned for v1.0.0)

- ✅ **Accurate token counting** using tiktoken (GPT-4 tokenizer)
- ✅ **Flexible configuration** with per-file limits and glob patterns
- ✅ **Fast execution** (< 1 second for typical projects)
- ✅ **Clear error messages** with suggestions for remediation
- ✅ **Pre-commit integration** via hooks
- ✅ **PyPI distribution** as `mdtoken` package

## Status

🚧 **In Development** - Requirements and exploration complete, implementation starting soon.

## Documentation

- [Requirements Specification](docs/requirements.md) - Complete functional and technical requirements
- [Technical Exploration](docs/exploration.md) - Architecture decisions and design rationale

## Configuration Example (Planned)

```yaml
# .mdtokenrc.yaml
default_limit: 5000

limits:
  "CLAUDE.md": 8000
  "README.md": 3000
  ".claude/memory/*.md": 2000

exclude:
  - "node_modules/**"
  - "**/archive/**"

total_limit: 50000
fail_on_exceed: true
```

## Pre-commit Integration (Planned)

```yaml
repos:
  - repo: https://github.com/stefanrmmr/mdtoken
    rev: v1.0.0
    hooks:
      - id: markdown-token-limit
        args: ['--config=.mdtokenrc.yaml']
```

## Technology Stack

- **Language**: Python 3.8+
- **Token Counter**: tiktoken (OpenAI's cl100k_base encoding)
- **Configuration**: PyYAML
- **Testing**: pytest
- **Distribution**: PyPI

## Installation (Coming Soon)

```bash
pip install mdtoken
```

## Usage (Coming Soon)

```bash
# Run manually
mdtoken check

# Run with custom config
mdtoken check --config .mdtokenrc.yaml

# Dry run (don't fail)
mdtoken check --dry-run
```

## Development

```bash
# Clone repository
git clone https://github.com/stefanrmmr/mdtoken.git
cd mdtoken

# Install development dependencies (coming soon)
pip install -e .[dev]

# Run tests (coming soon)
pytest
```

## Roadmap

### v1.0.0 (MVP)
- Core token counting functionality
- YAML configuration support
- Pre-commit hook integration
- Clear error messages
- PyPI distribution
- Comprehensive documentation

### v1.1+ (Future)
- Auto-fix/splitting suggestions
- Token count caching
- Parallel processing for large repos
- GitHub Action
- IDE integrations (VS Code extension)
- Support for multiple tokenizers (Claude, LLaMA)

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) (coming soon) for guidelines.

## Author

Stefan Rummer ([@stefanrmmr](https://github.com/stefanrmmr))

## Acknowledgments

- Inspired by real-world challenges in AI-assisted development workflows
- Built with Claude Code as part of the Factory framework project
- Uses OpenAI's tiktoken library for accurate token counting

---

**Note**: This is an early-stage open-source project. Star ⭐ and watch 👀 for updates!
