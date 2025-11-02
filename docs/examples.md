# Usage Examples

This guide provides practical examples for using mdtoken in different scenarios and project types.

## Table of Contents

- [Project-Specific Configurations](#project-specific-configurations)
  - [Claude Code Project](#1-claude-code-project)
  - [Documentation-Heavy Project](#2-documentation-heavy-project)
  - [Multi-Model Team](#3-multi-model-team)
  - [Monorepo with Multiple Contexts](#4-monorepo-with-multiple-contexts)
  - [Open Source Project](#5-open-source-project)
  - [Academic Research Project](#6-academic-research-project)
- [Common Workflows](#common-workflows)
  - [Pre-commit Hook Setup](#pre-commit-hook-setup)
  - [CI/CD Integration](#cicd-integration)
  - [Manual Checking](#manual-checking)
  - [Automated Enforcement](#automated-enforcement)
- [Advanced Usage](#advanced-usage)
  - [Custom Reporting](#custom-reporting)
  - [Programmatic Integration](#programmatic-integration)
  - [Git Hook Integration](#git-hook-integration)
- [Migration Scenarios](#migration-scenarios)
  - [From Manual Token Checking](#from-manual-token-checking)
  - [From Other Linters](#from-other-linters)
- [Best Practices](#best-practices)

---

## Project-Specific Configurations

### 1. Claude Code Project

**Scenario**: AI-assisted development with Claude Code, managing commands, skills, and memory files.

**`.mdtokenrc.yaml`**:

```yaml
# Claude Code project configuration
default_limit: 4000
model: "claude-3.5"

# Per-directory limits optimized for Claude Code
limits:
  # Core framework files
  "CLAUDE.md": 8000                    # Main context file
  ".claude/memory/**": 6000            # Memory files can be larger

  # Modular components (keep concise)
  ".claude/commands/**": 2000          # Commands should be focused
  ".claude/skills/**": 3000            # Skills can be slightly larger
  ".claude/agents/**": 4000            # Agent definitions

  # Documentation
  "README.md": 10000                   # Main README can be comprehensive
  "docs/**": 6000                      # Documentation files

  # Work artifacts
  ".claude/work/**": 5000              # Work unit documentation
  ".claude/transitions/**": 8000       # Session handoffs

# Exclude patterns
exclude:
  - ".git/**"
  - "node_modules/**"
  - "venv/**"
  - ".claude/archive/**"               # Archived content
  - "**/scratch/**"                    # Temporary notes

# Aggregate limit (50K tokens total across all files)
total_limit: 50000

# Fail commits that exceed limits
fail_on_exceed: true
```

**Rationale**:
- **Commands**: 2K tokens keeps them focused and single-purpose
- **Skills**: 3K tokens allows for moderate complexity
- **Memory files**: 6K tokens for substantial context preservation
- **CLAUDE.md**: 8K tokens as the main project context file
- **Total limit**: 50K ensures entire context fits comfortably in Claude's window

**Usage**:
```bash
# Check all Claude Code files
mdtoken check

# Check only framework files
mdtoken check .claude/**/*.md

# Verbose output with suggestions
mdtoken check --verbose
```

---

### 2. Documentation-Heavy Project

**Scenario**: Open source project with extensive documentation, guides, and tutorials.

**`.mdtokenrc.yaml`**:

```yaml
# Documentation-focused configuration
default_limit: 6000
model: "gpt-4"

limits:
  # Top-level documentation
  "README.md": 8000
  "CONTRIBUTING.md": 6000
  "CHANGELOG.md": 10000               # Can grow over time

  # Documentation sections
  "docs/getting-started.md": 5000
  "docs/api-reference.md": 12000      # API docs can be comprehensive
  "docs/guides/**": 7000              # Tutorials and guides
  "docs/examples/**": 8000            # Example code and walkthroughs

  # Keep reference docs concise
  "docs/faq.md": 5000
  "docs/troubleshooting.md": 6000

exclude:
  - "docs/archive/**"
  - "docs/drafts/**"
  - "**/old/**"

total_limit: 100000                   # Large documentation set

fail_on_exceed: true
```

**Rationale**:
- **API reference**: 12K allows comprehensive documentation
- **Tutorials**: 7-8K provides room for detailed walkthroughs
- **README**: 8K for complete project overview
- **Large total**: 100K supports extensive documentation

---

### 3. Multi-Model Team

**Scenario**: Team using different AI models (GPT-4, GPT-4o, Claude) for different purposes.

**`.mdtokenrc.yaml`**:

```yaml
# Multi-model team configuration
# Using GPT-4o tokenizer as it's most permissive
model: "gpt-4o"

default_limit: 5000

limits:
  # GPT-4o optimized files (has larger context window)
  "docs/architecture/**": 8000
  "docs/design/**": 8000

  # GPT-4 optimized files (standard context)
  "docs/api/**": 6000
  "docs/guides/**": 6000

  # Claude optimized files
  ".claude/**": 4000
  "CLAUDE.md": 8000

  # Shared files (conservative limits)
  "README.md": 6000
  "CONTRIBUTING.md": 5000

exclude:
  - "**/generated/**"
  - "**/tmp/**"

# Conservative total for cross-model compatibility
total_limit: 80000

fail_on_exceed: true
```

**Usage Pattern**:
```bash
# Different configs for different contexts
mdtoken check --config .mdtokenrc.gpt4o.yaml    # For GPT-4o work
mdtoken check --config .mdtokenrc.claude.yaml   # For Claude work
mdtoken check --config .mdtokenrc.shared.yaml   # For shared docs
```

---

### 4. Monorepo with Multiple Contexts

**Scenario**: Monorepo with multiple projects, each with its own token budget.

**Root `.mdtokenrc.yaml`**:

```yaml
# Monorepo root configuration
default_limit: 4000
model: "gpt-4"

limits:
  # Root documentation
  "README.md": 8000
  "ARCHITECTURE.md": 10000

  # Project A (frontend)
  "packages/frontend/**": 5000
  "packages/frontend/README.md": 6000

  # Project B (backend)
  "packages/backend/**": 5000
  "packages/backend/README.md": 6000

  # Project C (shared)
  "packages/shared/**": 4000

  # Infrastructure docs
  "docs/infrastructure/**": 7000
  "docs/deployment/**": 6000

exclude:
  - "**/node_modules/**"
  - "**/dist/**"
  - "**/build/**"
  - "**/.next/**"

# Large total for entire monorepo
total_limit: 150000

fail_on_exceed: true
```

**Per-Project Configs**:

**`packages/frontend/.mdtokenrc.yaml`**:
```yaml
default_limit: 5000
model: "gpt-4"

limits:
  "README.md": 6000
  "docs/**": 5000
  "stories/**": 4000          # Storybook stories

total_limit: 30000
fail_on_exceed: true
```

---

### 5. Open Source Project

**Scenario**: Public OSS project prioritizing newcomer-friendly documentation.

**`.mdtokenrc.yaml`**:

```yaml
# Open source project configuration
default_limit: 5000
model: "gpt-4"

limits:
  # Newcomer-focused docs (keep concise and scannable)
  "README.md": 6000                   # Quick overview
  "CONTRIBUTING.md": 5000             # Clear contribution guide
  "CODE_OF_CONDUCT.md": 3000          # Concise and clear

  # Detailed technical docs
  "docs/architecture.md": 10000       # Comprehensive system design
  "docs/api.md": 12000                # Complete API reference
  "docs/development.md": 7000         # Development setup

  # Examples and tutorials
  "docs/examples/**": 6000
  "docs/tutorials/**": 7000

  # Community docs
  "docs/faq.md": 5000
  "CHANGELOG.md": 15000               # Full project history

exclude:
  - "vendor/**"
  - "**/third_party/**"
  - "docs/archive/**"

total_limit: 100000

fail_on_exceed: true
```

**Best Practices**:
- Keep README concise (6K) - link to detailed docs
- Comprehensive API docs (12K) for reference
- Focused tutorials (7K each) for learning
- Detailed architecture docs (10K) for contributors

---

### 6. Academic Research Project

**Scenario**: Research project with papers, notes, and literature reviews.

**`.mdtokenrc.yaml`**:

```yaml
# Academic research configuration
default_limit: 8000                   # Academic writing is verbose
model: "gpt-4"

limits:
  # Papers and manuscripts
  "papers/**": 15000                  # Academic papers are long
  "papers/drafts/**": 20000           # Drafts can be longer

  # Research notes
  "notes/**": 6000
  "literature-review/**": 10000       # Literature reviews are comprehensive

  # Methodology and experiments
  "methodology/**": 8000
  "experiments/**": 7000

  # Results and analysis
  "results/**": 10000
  "analysis/**": 10000

  # Documentation
  "README.md": 5000
  "docs/**": 7000

exclude:
  - "data/**"                         # Raw data files
  - "figures/**"                      # Images and plots
  - "**/archive/**"                   # Old versions

total_limit: 200000                   # Large research corpus

fail_on_exceed: false                 # Warn but don't block
```

**Rationale**:
- **Academic papers**: 15-20K tokens for full manuscripts
- **Literature reviews**: 10K for comprehensive coverage
- **Fail_on_exceed: false**: Academic work is less strict, just warn
- **Large total**: 200K supports extensive research documentation

---

## Common Workflows

### Pre-commit Hook Setup

**Complete Setup**:

```bash
# 1. Install pre-commit framework
pip install pre-commit

# 2. Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/stefanrmmr/mdtoken
    rev: v1.0.0
    hooks:
      - id: markdown-token-limit
        name: Check Markdown Token Limits
        args: ['--verbose']
EOF

# 3. Install the hook
pre-commit install

# 4. Test the hook
pre-commit run --all-files
```

**Selective Checking**:

```yaml
# Only check specific directories
repos:
  - repo: https://github.com/stefanrmmr/mdtoken
    rev: v1.0.0
    hooks:
      - id: markdown-token-limit
        files: ^(docs|\.claude)/.*\.md$
```

**Disable for Specific Commits**:

```bash
# Temporarily skip hook
SKIP=markdown-token-limit git commit -m "Emergency fix"

# Or use --no-verify
git commit --no-verify -m "WIP: large draft"
```

---

### CI/CD Integration

#### GitHub Actions

**`.github/workflows/docs-check.yml`**:

```yaml
name: Documentation Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    paths:
      - '**.md'
      - '.mdtokenrc.yaml'

jobs:
  token-limits:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install mdtoken
        run: pip install mdtoken

      - name: Check token limits
        run: mdtoken check --verbose

      - name: Upload report
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: token-violations
          path: token-report.txt
```

#### GitLab CI

**`.gitlab-ci.yml`**:

```yaml
documentation-quality:
  stage: test
  image: python:3.11
  script:
    - pip install mdtoken
    - mdtoken check --verbose
  only:
    changes:
      - "**/*.md"
      - ".mdtokenrc.yaml"
  allow_failure: false
```

#### Jenkins

**`Jenkinsfile`**:

```groovy
pipeline {
    agent any

    stages {
        stage('Documentation Quality') {
            when {
                changeset "**/*.md"
            }
            steps {
                sh '''
                    pip install mdtoken
                    mdtoken check --verbose || exit 1
                '''
            }
        }
    }

    post {
        failure {
            archiveArtifacts artifacts: 'token-report.txt'
        }
    }
}
```

---

### Manual Checking

**Daily Workflow**:

```bash
# Morning check before starting work
mdtoken check --verbose

# Check specific files after editing
mdtoken check CLAUDE.md .claude/memory/project-context.md

# Dry run to see violations without failing
mdtoken check --dry-run

# Check only changed files
git diff --name-only | grep '.md$' | xargs mdtoken check
```

**Pre-commit Manual Check**:

```bash
# Check staged files only
git diff --cached --name-only --diff-filter=ACM | grep '.md$' | xargs mdtoken check
```

---

### Automated Enforcement

**Git Hook (Without pre-commit framework)**:

**`.git/hooks/pre-commit`**:

```bash
#!/bin/bash
# Manual pre-commit hook for mdtoken

# Get staged markdown files
STAGED_MD=$(git diff --cached --name-only --diff-filter=ACM | grep '.md$')

if [ -n "$STAGED_MD" ]; then
    echo "Checking markdown token limits..."

    # Run mdtoken check
    if ! mdtoken check $STAGED_MD; then
        echo ""
        echo "❌ Token limit violations found!"
        echo "Fix the violations or use 'git commit --no-verify' to bypass"
        exit 1
    fi

    echo "✅ All markdown files within token limits"
fi

exit 0
```

**Make executable**:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Advanced Usage

### Custom Reporting

**JSON Output for Parsing**:

```python
#!/usr/bin/env python3
"""Generate JSON report of token violations."""
import json
import sys
from pathlib import Path
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer

def main():
    config = Config.from_file()
    enforcer = LimitEnforcer(config)
    result = enforcer.check_files()

    # Create JSON report
    report = {
        "passed": result.passed,
        "summary": {
            "total_files": result.total_files,
            "total_tokens": result.total_tokens,
            "violations": result.violation_count,
            "total_limit_exceeded": result.total_limit_exceeded
        },
        "violations": [
            {
                "file": str(v.file_path),
                "actual_tokens": v.actual_tokens,
                "limit": v.limit,
                "excess": v.excess,
                "percentage_over": round(v.percentage_over, 2)
            }
            for v in result.violations
        ]
    }

    # Write to file
    with open("token-report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    sys.exit(0 if result.passed else 1)

if __name__ == "__main__":
    main()
```

**Slack Notification**:

```python
#!/usr/bin/env python3
"""Send Slack notification for token violations."""
import os
import requests
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer

def send_slack_notification(result):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return

    if result.passed:
        message = {
            "text": "✅ Token limits check passed",
            "color": "good",
            "fields": [
                {"title": "Files Checked", "value": str(result.total_files), "short": True},
                {"title": "Total Tokens", "value": f"{result.total_tokens:,}", "short": True}
            ]
        }
    else:
        violations_text = "\n".join([
            f"• `{v.file_path}`: {v.excess:,} tokens over ({v.percentage_over:.1f}%)"
            for v in result.violations[:5]
        ])

        message = {
            "text": "❌ Token limits check failed",
            "color": "danger",
            "fields": [
                {"title": "Violations", "value": str(result.violation_count), "short": True},
                {"title": "Total Tokens", "value": f"{result.total_tokens:,}", "short": True}
            ],
            "attachments": [{
                "text": violations_text,
                "color": "danger"
            }]
        }

    requests.post(webhook_url, json=message)

# Usage
config = Config.from_file()
enforcer = LimitEnforcer(config)
result = enforcer.check_files()
send_slack_notification(result)
```

---

### Programmatic Integration

**Django Management Command**:

```python
# myapp/management/commands/check_docs.py
from django.core.management.base import BaseCommand
from pathlib import Path
from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer
from mdtoken.reporter import Reporter

class Command(BaseCommand):
    help = 'Check documentation token limits'

    def add_arguments(self, parser):
        parser.add_argument(
            '--config',
            type=str,
            help='Path to mdtoken config file'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )

    def handle(self, *args, **options):
        config_path = Path(options.get('config')) if options.get('config') else None
        config = Config.from_file(config_path)

        enforcer = LimitEnforcer(config)
        result = enforcer.check_files()

        reporter = Reporter(enforcer)
        reporter.report(result, verbose=options['verbose'])

        if not result.passed:
            self.stdout.write(self.style.ERROR('Token limit violations found'))
            return 1
        else:
            self.stdout.write(self.style.SUCCESS('All files within limits'))
            return 0
```

**Usage**:
```bash
python manage.py check_docs --verbose
```

---

### Git Hook Integration

**Pre-push Hook** (stricter than pre-commit):

**`.git/hooks/pre-push`**:

```bash
#!/bin/bash
# Check ALL markdown files before push

echo "Running comprehensive token limit check..."

if ! mdtoken check --verbose; then
    echo ""
    echo "❌ Token limit violations found!"
    echo "Fix violations before pushing"
    echo ""
    echo "To bypass this check: git push --no-verify"
    exit 1
fi

echo "✅ All markdown files within token limits"
exit 0
```

---

## Migration Scenarios

### From Manual Token Checking

**Before** (manual process):
```bash
# Old manual workflow
wc -w CLAUDE.md | awk '{print $1 * 1.3}'  # Rough token estimate
# Manually check each file
# No automation, easy to forget
```

**After** (automated with mdtoken):
```bash
# 1. Install mdtoken
pip install mdtoken

# 2. Create config based on your current limits
cat > .mdtokenrc.yaml << EOF
default_limit: 4000
limits:
  "CLAUDE.md": 8000
  "README.md": 6000
fail_on_exceed: true
EOF

# 3. Initial check to see current state
mdtoken check --verbose

# 4. Install pre-commit hook
pip install pre-commit
pre-commit install

# 5. Never manually check again!
```

**Migration Checklist**:
- [ ] Install mdtoken
- [ ] Document current token limits
- [ ] Create `.mdtokenrc.yaml` with current limits
- [ ] Run initial check: `mdtoken check --verbose`
- [ ] Fix any violations
- [ ] Install pre-commit hook
- [ ] Update team documentation
- [ ] Remove manual checking from workflow

---

### From Other Linters

**From markdownlint**:

```yaml
# Can run both linters together
repos:
  - repo: https://github.com/markdownlint/markdownlint
    rev: v0.12.0
    hooks:
      - id: markdownlint
        args: ['--config', '.markdownlint.json']

  - repo: https://github.com/stefanrmmr/mdtoken
    rev: v1.0.0
    hooks:
      - id: markdown-token-limit
```

**Rationale**:
- **markdownlint**: Checks syntax, style, formatting
- **mdtoken**: Checks token consumption
- Complementary, not competing tools

---

## Best Practices

### 1. Setting Appropriate Limits

**Conservative Approach**:
```yaml
# Start with strict limits, relax as needed
default_limit: 3000      # Most files should be concise
limits:
  "CLAUDE.md": 6000      # Main context file
  "README.md": 5000      # Project overview
```

**Generous Approach**:
```yaml
# Start permissive, tighten over time
default_limit: 6000
limits:
  ".claude/commands/**": 3000  # Enforce modularity
```

**Recommendation**: Start conservative, then monitor violations and adjust.

### 2. Model Selection

**Choose tokenizer based on primary AI tool**:

```yaml
# Team primarily uses GPT-4
model: "gpt-4"

# Team primarily uses Claude
model: "claude-3.5"

# Team uses GPT-4o
model: "gpt-4o"

# Power users who want specific encoding
encoding: "cl100k_base"
```

### 3. Exclusion Patterns

**Comprehensive exclusions**:

```yaml
exclude:
  # Version control
  - ".git/**"

  # Dependencies
  - "node_modules/**"
  - "venv/**"
  - ".venv/**"
  - "vendor/**"

  # Build outputs
  - "build/**"
  - "dist/**"
  - "out/**"
  - ".next/**"

  # Archives and backups
  - "**/archive/**"
  - "**/backup/**"
  - "**/*.backup.md"

  # Temporary files
  - "**/tmp/**"
  - "**/temp/**"
  - "**/.scratch/**"

  # Generated files
  - "**/generated/**"
  - "**/.cache/**"
```

### 4. Total Limits

**Set realistic total budgets**:

```yaml
# Small project (< 20 markdown files)
total_limit: 50000

# Medium project (20-50 files)
total_limit: 100000

# Large project (> 50 files)
total_limit: 200000

# Enterprise monorepo
total_limit: 500000
```

### 5. Fail Behavior

**When to fail vs warn**:

```yaml
# Production/main branch - strict
fail_on_exceed: true

# Development branches - permissive
fail_on_exceed: false  # Just warn
```

**Branch-specific configs**:
```bash
# .mdtokenrc.production.yaml
fail_on_exceed: true

# .mdtokenrc.dev.yaml
fail_on_exceed: false
```

### 6. Directory Structure

**Recommended structure**:

```
project/
├── .mdtokenrc.yaml              # Root configuration
├── README.md                     # Main project docs
├── docs/
│   ├── .mdtokenrc.yaml          # Docs-specific config (optional)
│   ├── api.md
│   ├── guides/
│   └── examples/
├── .claude/
│   ├── .mdtokenrc.yaml          # Claude-specific config (optional)
│   ├── CLAUDE.md
│   ├── commands/
│   ├── skills/
│   └── memory/
└── .pre-commit-config.yaml
```

### 7. Team Workflows

**Single developer**:
- Use pre-commit hook
- Run manually before commits
- Adjust limits as needed

**Small team (2-5)**:
- Shared `.mdtokenrc.yaml` in repo
- Pre-commit hook enforced
- Review config changes in PRs

**Large team (5+)**:
- Strict limits enforced
- CI/CD validation required
- Config changes need approval
- Regular limit reviews

### 8. Handling Violations

**When limits are exceeded**:

1. **First, consider splitting**:
   ```bash
   # Large file
   docs/api.md (12,000 tokens)

   # Split into
   docs/api/overview.md (3,000 tokens)
   docs/api/endpoints.md (4,000 tokens)
   docs/api/examples.md (3,000 tokens)
   ```

2. **Second, archive old content**:
   ```bash
   mv docs/2023-roadmap.md docs/archive/
   ```

3. **Third, compress content**:
   - Remove redundant examples
   - Use more concise language
   - Link to external resources instead of embedding

4. **Last resort, increase limit**:
   ```yaml
   limits:
     "docs/api.md": 15000  # Justified exception
   ```

---

## Summary

- **Start simple**: Begin with default limits and adjust based on violations
- **Automate early**: Install pre-commit hook from day one
- **Be consistent**: Use same tokenizer as your primary AI tool
- **Review regularly**: Adjust limits quarterly as project evolves
- **Document exceptions**: Comment why specific files have higher limits
- **Monitor total**: Track aggregate token consumption over time

For more detailed information, see:
- [API Documentation](api.md) - Programmatic usage
- [Troubleshooting](troubleshooting.md) - Common issues
- [FAQ](faq.md) - Frequently asked questions
