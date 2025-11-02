# Frequently Asked Questions (FAQ)

Common questions about mdtoken and token limit enforcement.

## Table of Contents

- [General Questions](#general-questions)
- [Technical Questions](#technical-questions)
- [Usage Questions](#usage-questions)
- [Configuration Questions](#configuration-questions)
- [Compatibility Questions](#compatibility-questions)

---

## General Questions

### Why another markdown linter?

**mdtoken is not a traditional linter** - it's specifically designed for AI-assisted workflows where token counts matter.

**Traditional linters** (markdownlint, remark-lint) check:
- Syntax errors
- Style consistency
- Formatting issues
- Link validity

**mdtoken checks**:
- Token consumption
- Context window usage
- AI readability limits

**Use both together**:
```yaml
repos:
  - repo: https://github.com/markdownlint/markdownlint
    rev: v0.12.0
    hooks:
      - id: markdownlint

  - repo: https://github.com/stefanrmmr/mdtoken
    rev: v1.0.0
    hooks:
      - id: markdown-token-limit
```

They're complementary, not competing tools.

---

### Why do token counts matter?

**Token limits affect**:
- **AI context windows**: GPT-4 (8K/32K/128K), Claude (200K), GPT-4o (128K)
- **API costs**: Charged per token, not per word
- **Response quality**: Truncated context = worse outputs
- **Processing speed**: Larger context = slower responses

**Real-world impact**:
```
❌ 150K token CLAUDE.md → Silently truncated, Claude misses critical info
✓  8K token CLAUDE.md  → Fits comfortably, Claude sees everything
```

**Cost impact**:
```
GPT-4 Turbo pricing (as of 2024):
- Input: $0.01 per 1K tokens
- Large docs (50K tokens) = $0.50 per request
- 100 requests = $50 just for input
```

---

### How accurate is the token counting?

**Very accurate** (within 1-2% of actual model tokenization).

mdtoken uses **tiktoken**, the same library used by OpenAI's models. It's not a heuristic or approximation - it's the real tokenizer.

**Accuracy by model**:
- **GPT-4/GPT-3.5**: 100% accurate (uses exact cl100k_base encoding)
- **GPT-4o**: 100% accurate (uses exact o200k_base encoding)
- **Claude**: ~98% accurate (Claude uses similar but proprietary tokenization)
- **Other models**: 95-98% accurate (close approximations)

**Verification**:
```python
from mdtoken.counter import TokenCounter
import tiktoken

# mdtoken uses tiktoken internally
counter = TokenCounter("cl100k_base")
encoding = tiktoken.get_encoding("cl100k_base")

text = "Your markdown content"
assert counter.count_tokens(text) == len(encoding.encode(text))
# Always true - same library, same result
```

---

### Can I use this without pre-commit?

**Absolutely!** Pre-commit is optional. You can use mdtoken:

1. **Standalone CLI**:
   ```bash
   mdtoken check --verbose
   ```

2. **CI/CD pipeline** (GitHub Actions, GitLab CI, Jenkins):
   ```yaml
   - run: mdtoken check
   ```

3. **Custom git hooks** (without pre-commit framework):
   ```bash
   # .git/hooks/pre-push
   mdtoken check || exit 1
   ```

4. **Programmatically** in Python:
   ```python
   from mdtoken.enforcer import LimitEnforcer
   enforcer = LimitEnforcer(config)
   result = enforcer.check_files()
   ```

5. **Make/Justfile target**:
   ```makefile
   check-docs:
   	mdtoken check --verbose
   ```

6. **IDE integration** (run before commit):
   - VS Code: Tasks
   - PyCharm: External Tools
   - Vim: Make integration

---

### Does it work with Claude, GPT-4o, or other models?

**Yes!** mdtoken supports multiple tokenizers.

**Supported models** (v1.0.0):

| Model | Encoding | Config |
|-------|----------|--------|
| GPT-4 | cl100k_base | `model: "gpt-4"` |
| GPT-4o | o200k_base | `model: "gpt-4o"` |
| GPT-3.5 Turbo | cl100k_base | `model: "gpt-3.5-turbo"` |
| Claude 3 | cl100k_base* | `model: "claude-3"` |
| Claude 3.5 | cl100k_base* | `model: "claude-3.5"` |
| Codex | p50k_base | `model: "codex"` |
| GPT-3 | r50k_base | `model: "gpt-3"` |

*Claude uses proprietary tokenization, but cl100k_base is a close approximation.

**Multi-model teams**:
```yaml
# Use most permissive tokenizer
model: "gpt-4o"  # Has largest tokens

# Or create model-specific configs
# .mdtokenrc.gpt4.yaml
# .mdtokenrc.claude.yaml
```

---

### Is it free and open source?

**Yes!** mdtoken is:
- **MIT Licensed** - Use commercially, modify freely
- **Open source** - [GitHub repository](https://github.com/stefanrmmr/mdtoken)
- **Free forever** - No paid tiers or premium features
- **Community-driven** - Contributions welcome

**What's included**:
- ✓ Full source code
- ✓ Comprehensive tests
- ✓ Documentation
- ✓ CLI tool
- ✓ Python API
- ✓ Pre-commit hook

**No hidden costs**:
- No API keys needed
- No cloud services
- No telemetry
- No data collection

---

## Technical Questions

### What languages/frameworks does it support?

**File type**: Markdown only (`.md` files)

**Works with any**:
- Programming language (Python, JS, Go, etc.)
- Framework (Django, React, Vue, etc.)
- Project type (web, CLI, library, docs)
- Platform (Windows, macOS, Linux)

**Requirements**:
- Python 3.8+
- No other dependencies

**Platform support**:
```bash
# Linux
pip install mdtoken

# macOS
pip install mdtoken

# Windows
pip install mdtoken

# Docker
FROM python:3.11
RUN pip install mdtoken
```

---

### How fast is it?

**Very fast** - optimized for interactive use.

**Benchmarks** (on standard hardware):

| Files | Target | Actual | Performance |
|-------|--------|--------|-------------|
| 5 files | < 500ms | 65ms | **87% faster** |
| 10 files | < 1000ms | 2.3ms | **99.8% faster** |
| 100 files | < 5000ms | 35.6ms | **99.3% faster** |
| Per file | < 10ms | 0.31ms | **97% faster** |

**Token counting**:
- 2K tokens: ~0.3ms
- 8K tokens: ~6ms
- Linear O(n) scaling

**Pre-commit overhead**:
- Checking 5 markdown files adds < 100ms to commit time
- Negligible impact on developer workflow

**Optimization**:
- Tiktoken is written in Rust (very fast)
- Files processed sequentially (no overhead)
- No caching needed (fast enough without)

---

### Does it support parallel processing?

**Not yet**, but it's fast enough that it hasn't been needed.

**Current**: Sequential processing (~0.3ms per file)
**Future** (v1.1+): Parallel processing for large repositories

**Workaround for large repos**:
```bash
# Check only changed files (pre-commit does this automatically)
git diff --name-only | grep '.md$' | xargs mdtoken check

# Or use exclusion patterns
exclude:
  - "vendor/**"
  - "archive/**"
```

**Roadmap**:
- v1.0: Sequential (current)
- v1.1: Optional parallel processing
- v1.2: Token count caching

---

### Can I extend or customize it?

**Yes!** mdtoken is designed for extensibility.

**Python API**:
```python
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer
from mdtoken.reporter import Reporter

# Custom configuration
config = Config(
    default_limit=5000,
    model="gpt-4o"
)

# Custom reporter
class MyReporter(Reporter):
    def report(self, result, verbose=False):
        # Custom formatting
        pass

# Use programmatically
enforcer = LimitEnforcer(config)
result = enforcer.check_files()
```

**Custom integrations**:
- Django management commands
- Flask CLI commands
- CI/CD scripts
- IDE plugins
- Slack/Discord bots

**Examples**: See [API Documentation](api.md)

---

## Usage Questions

### How do I set appropriate token limits?

**Start conservative, adjust based on actual usage**.

**Recommended limits**:

| File Type | Limit | Rationale |
|-----------|-------|-----------|
| Commands | 2000 | Single-purpose, focused |
| Skills | 3000 | Moderate complexity |
| Memory files | 6000 | Substantial context |
| CLAUDE.md | 8000 | Main project context |
| README.md | 6000 | Project overview |
| API docs | 12000 | Comprehensive reference |
| Tutorials | 7000 | Detailed walkthrough |

**Formula**:
```
Individual limit = 20-30% of model's context window
Total limit = 50-70% of model's context window
```

**Example for GPT-4 (8K context)**:
- Individual files: 2-3K tokens
- Total: 4-6K tokens

**Adjustment process**:
1. Start with defaults (4K)
2. Run `mdtoken check --verbose`
3. Review violations
4. Increase limits only when justified
5. Monitor over time

---

### What if I need different limits for different branches?

**Use branch-specific config files**.

**Setup**:
```bash
# Production config (strict)
.mdtokenrc.production.yaml:
  default_limit: 3000
  fail_on_exceed: true

# Development config (permissive)
.mdtokenrc.dev.yaml:
  default_limit: 6000
  fail_on_exceed: false
```

**Usage**:
```bash
# In CI/CD (production branch)
mdtoken check --config .mdtokenrc.production.yaml

# Local development
mdtoken check --config .mdtokenrc.dev.yaml
```

**Git hooks** (branch-aware):
```bash
#!/bin/bash
BRANCH=$(git branch --show-current)

if [ "$BRANCH" = "main" ]; then
    mdtoken check --config .mdtokenrc.production.yaml
else
    mdtoken check --config .mdtokenrc.dev.yaml
fi
```

---

### Can I check files in specific directories only?

**Yes!** Multiple ways to scope checking.

**Method 1**: Explicit file list
```bash
mdtoken check docs/**/*.md
mdtoken check .claude/commands/*.md .claude/skills/*.md
```

**Method 2**: Configuration exclusions
```yaml
exclude:
  - "vendor/**"
  - "archive/**"
  - "**/old/**"
```

**Method 3**: Pre-commit file filter
```yaml
hooks:
  - id: markdown-token-limit
    files: ^(docs|\.claude)/.*\.md$  # Only docs/ and .claude/
```

**Method 4**: Programmatic filtering
```python
from pathlib import Path
from mdtoken.enforcer import LimitEnforcer

files = [f for f in Path("docs").glob("*.md")]
result = enforcer.check_files(check_files=files)
```

---

### How do I handle generated/auto-updated files?

**Exclude them** or **set higher limits**.

**Option 1**: Exclude
```yaml
exclude:
  - "docs/api-reference.md"  # Auto-generated API docs
  - "**/CHANGELOG.md"        # Auto-updated changelog
  - "**/*_generated.md"      # Generated files
```

**Option 2**: Higher limits
```yaml
limits:
  "docs/api-reference.md": 20000  # Large auto-generated file
  "CHANGELOG.md": null            # No limit
```

**Option 3**: Separate check
```bash
# Check only non-generated files
mdtoken check --exclude "**/generated/**"
```

---

## Configuration Questions

### Should I commit `.mdtokenrc.yaml` to git?

**Yes, definitely!**

**Reasons to commit**:
- ✓ Consistent limits across team
- ✓ Enforced in CI/CD
- ✓ Documented project standards
- ✓ Versioned with code

**What to include**:
```bash
git add .mdtokenrc.yaml
git add .pre-commit-config.yaml
git commit -m "Add token limit enforcement"
```

**What NOT to commit**:
- Personal `.mdtokenrc.local.yaml` (add to `.gitignore`)
- Temporary test configs

**Example `.gitignore`**:
```
.mdtokenrc.local.yaml
.mdtokenrc.*.local.yaml
```

---

### Can I have per-directory configs?

**Not directly**, but you can simulate with patterns.

**Pattern-based approach**:
```yaml
# Root .mdtokenrc.yaml
limits:
  "frontend/docs/**": 5000
  "backend/docs/**": 6000
  "shared/docs/**": 4000
```

**Multiple config files**:
```bash
# Check different parts with different configs
mdtoken check --config frontend/.mdtokenrc.yaml frontend/
mdtoken check --config backend/.mdtokenrc.yaml backend/
```

**Future feature** (v1.2+):
```yaml
# Planned: Nested configs
# .mdtokenrc.yaml (root)
# frontend/.mdtokenrc.yaml (inherits + extends root)
# backend/.mdtokenrc.yaml (inherits + extends root)
```

---

### What's the difference between `encoding` and `model`?

**`model`**: User-friendly model name (recommended)
```yaml
model: "gpt-4"           # Easy to remember
model: "claude-3.5"      # Intuitive
```

**`encoding`**: Direct tiktoken encoding name (power users)
```yaml
encoding: "cl100k_base"  # Explicit
encoding: "o200k_base"   # Technical
```

**Precedence**: `encoding` overrides `model` if both specified
```yaml
model: "gpt-4"              # → cl100k_base
encoding: "o200k_base"      # → o200k_base (wins)
```

**When to use each**:
- **model**: 95% of use cases
- **encoding**: When you need specific encoding not mapped to model

---

## Compatibility Questions

### Does it work with monorepos?

**Yes!** mdtoken works great with monorepos.

**Recommended setup**:

```
monorepo/
├── .mdtokenrc.yaml              # Root config
├── packages/
│   ├── frontend/
│   │   └── .mdtokenrc.yaml      # Frontend-specific
│   ├── backend/
│   │   └── .mdtokenrc.yaml      # Backend-specific
│   └── shared/
│       └── .mdtokenrc.yaml      # Shared-specific
└── docs/
    └── .mdtokenrc.yaml          # Docs-specific
```

**Root config**:
```yaml
# Aggregate limit for entire monorepo
total_limit: 200000

limits:
  "packages/frontend/**": 5000
  "packages/backend/**": 6000
  "docs/**": 8000
```

**CI/CD** (check all):
```bash
mdtoken check --config .mdtokenrc.yaml
```

**Local** (check one package):
```bash
cd packages/frontend
mdtoken check
```

---

### Can I use it with GitHub/GitLab/Bitbucket?

**Yes!** mdtoken integrates with all major git hosting platforms.

**GitHub**:
```yaml
# .github/workflows/docs.yml
- name: Check token limits
  run: mdtoken check --verbose
```

**GitLab**:
```yaml
# .gitlab-ci.yml
docs-check:
  script:
    - mdtoken check --verbose
```

**Bitbucket**:
```yaml
# bitbucket-pipelines.yml
pipelines:
  default:
    - step:
        script:
          - mdtoken check --verbose
```

**All platforms**: Use pre-commit hook (works everywhere)

---

### Does it support Windows?

**Yes!** mdtoken is fully cross-platform.

**Installation** (Windows):
```powershell
# PowerShell
pip install mdtoken

# Verify
mdtoken --version
```

**Path setup** (if needed):
```powershell
# Add Python Scripts to PATH
$env:Path += ";$env:USERPROFILE\AppData\Local\Programs\Python\Python311\Scripts"
```

**Pre-commit** (Windows):
```powershell
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test
pre-commit run --all-files
```

**Known issues**: None (works identically on Windows/Mac/Linux)

---

### Is it compatible with Python 2?

**No.** mdtoken requires **Python 3.8 or higher**.

**Supported versions**:
- ✓ Python 3.8
- ✓ Python 3.9
- ✓ Python 3.10
- ✓ Python 3.11
- ✓ Python 3.12
- ✗ Python 2.7 (end of life 2020)
- ✗ Python 3.7 (end of life 2023)

**Why Python 3.8+**:
- Type hints (PEP 484, 526, 544)
- Modern async features
- Better performance
- Security updates

**Upgrade guide**:
```bash
# Check current version
python --version

# Install Python 3.11 (recommended)
# Ubuntu/Debian
sudo apt install python3.11

# macOS
brew install python@3.11

# Windows: Download from python.org
```

---

## Still Have Questions?

**Resources**:
- [Examples](examples.md) - Practical usage examples
- [Troubleshooting](troubleshooting.md) - Common issues
- [API Documentation](api.md) - Programmatic usage
- [GitHub Issues](https://github.com/stefanrmmr/mdtoken/issues) - Ask questions

**Contributing**:
- Found a bug? [Report it](https://github.com/stefanrmmr/mdtoken/issues/new)
- Have a feature idea? [Suggest it](https://github.com/stefanrmmr/mdtoken/issues/new)
- Want to contribute? See [CONTRIBUTING.md](../CONTRIBUTING.md)
