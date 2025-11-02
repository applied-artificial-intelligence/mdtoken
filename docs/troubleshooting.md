# Troubleshooting Guide

Common issues and solutions when using mdtoken.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Problems](#configuration-problems)
- [Pre-commit Hook Issues](#pre-commit-hook-issues)
- [Token Counting Issues](#token-counting-issues)
- [Performance Problems](#performance-problems)
- [CI/CD Integration Issues](#cicd-integration-issues)
- [Error Messages](#common-error-messages)

---

## Installation Issues

### "Command not found: mdtoken"

**Problem**: After installing mdtoken, the command is not available.

**Possible Causes & Solutions**:

1. **Not installed in active environment**:
   ```bash
   # Check if mdtoken is installed
   pip list | grep mdtoken

   # If not found, install it
   pip install mdtoken
   ```

2. **Virtual environment not activated**:
   ```bash
   # Activate your virtual environment
   source venv/bin/activate     # Linux/Mac
   venv\Scripts\activate        # Windows

   # Then install
   pip install mdtoken
   ```

3. **Installation in wrong Python version**:
   ```bash
   # Use specific Python version
   python3.11 -m pip install mdtoken

   # Verify
   python3.11 -m mdtoken --version
   ```

4. **PATH issue**:
   ```bash
   # Use full path
   python -m mdtoken check

   # Or add to PATH
   export PATH="$PATH:$HOME/.local/bin"
   ```

---

### "tiktoken not found" Error

**Problem**: mdtoken depends on tiktoken but it's not installed.

**Solution**:
```bash
# Install with all dependencies
pip install mdtoken

# Or install tiktoken manually
pip install tiktoken
```

**Development Installation**:
```bash
# Install from source with all dependencies
git clone https://github.com/stefanrmmr/mdtoken.git
cd mdtoken
pip install -e ".[dev]"
```

---

## Configuration Problems

### "Config file not found" Warning

**Problem**: mdtoken looks for `.mdtokenrc.yaml` but can't find it.

**Solutions**:

1. **Create config in project root**:
   ```bash
   cat > .mdtokenrc.yaml << EOF
   default_limit: 4000
   model: "gpt-4"
   EOF
   ```

2. **Specify config path explicitly**:
   ```bash
   mdtoken check --config path/to/config.yaml
   ```

3. **Use defaults** (no config needed):
   ```bash
   # mdtoken will use sensible defaults
   mdtoken check
   ```

**Default Configuration**:
```yaml
default_limit: 4000
encoding: "cl100k_base"
exclude:
  - ".git/**"
  - "node_modules/**"
  - "venv/**"
fail_on_exceed: true
```

---

### "Unknown model 'xyz'" Error

**Problem**: Model name in config is not recognized.

**Error Message**:
```
ConfigError: Unknown model 'gpt-5'. Available models: gpt-4, gpt-4o, ...
```

**Solutions**:

1. **Use supported model name**:
   ```yaml
   # Supported models
   model: "gpt-4"           # ✓
   model: "gpt-4o"          # ✓
   model: "claude-3.5"      # ✓
   model: "gpt-5"           # ✗ Not supported
   ```

2. **Use encoding directly**:
   ```yaml
   # Bypass model mapping
   encoding: "cl100k_base"
   ```

3. **Check supported models**:
   ```python
   from mdtoken.config import Config
   print(Config.MODEL_ENCODING_MAP.keys())
   ```

**Supported Models** (v1.0.0):
- `gpt-4` → `cl100k_base`
- `gpt-4o` → `o200k_base`
- `gpt-3.5-turbo` → `cl100k_base`
- `claude-3` → `cl100k_base`
- `claude-3.5` → `cl100k_base`
- `codex` → `p50k_base`
- `text-davinci-003` → `p50k_base`
- `text-davinci-002` → `p50k_base`
- `gpt-3` → `r50k_base`

---

### "Invalid YAML" Error

**Problem**: Configuration file has invalid YAML syntax.

**Common Mistakes**:

1. **Incorrect indentation**:
   ```yaml
   # ✗ Wrong
   limits:
   "README.md": 8000

   # ✓ Correct
   limits:
     "README.md": 8000
   ```

2. **Missing quotes**:
   ```yaml
   # ✗ Wrong (special characters without quotes)
   limits:
     .claude/commands/**: 2000

   # ✓ Correct
   limits:
     ".claude/commands/**": 2000
   ```

3. **Tabs instead of spaces**:
   ```yaml
   # Use spaces, not tabs
   default_limit: 4000
     limits:              # ✗ Tab indentation
       "README.md": 8000

   # ✓ Use spaces
   default_limit: 4000
   limits:
     "README.md": 8000
   ```

**Validation**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('.mdtokenrc.yaml'))"
```

---

### Pattern Matching Not Working

**Problem**: File limit patterns don't match expected files.

**Debug Steps**:

1. **Test pattern matching**:
   ```python
   from mdtoken.config import Config

   config = Config.from_file()
   test_path = ".claude/commands/setup.md"

   limit = config.get_limit(test_path)
   print(f"{test_path} -> {limit} tokens")
   ```

2. **Pattern matching rules**:
   ```yaml
   limits:
     # Exact match (highest priority)
     ".claude/CLAUDE.md": 8000

     # Substring match
     "commands/": 2000        # Matches ".claude/commands/foo.md"

     # Glob pattern
     ".claude/**": 4000       # Matches any file under .claude/

     # Endswith pattern
     "README.md": 6000        # Matches any README.md
   ```

3. **Common issues**:
   ```yaml
   # ✗ Wrong - too specific
   limits:
     "/full/path/to/file.md": 8000    # Only matches absolute path

   # ✓ Correct - relative pattern
   limits:
     "file.md": 8000                  # Matches any file.md
     "docs/file.md": 8000             # Matches docs/file.md anywhere
   ```

---

## Pre-commit Hook Issues

### Hook Not Running

**Problem**: Pre-commit hook doesn't execute on commit.

**Diagnostic Steps**:

1. **Check if pre-commit is installed**:
   ```bash
   which pre-commit
   # If not found: pip install pre-commit
   ```

2. **Check if hooks are installed**:
   ```bash
   ls -la .git/hooks/pre-commit
   # Should exist and be executable
   ```

3. **Install hooks**:
   ```bash
   pre-commit install
   ```

4. **Test hook manually**:
   ```bash
   pre-commit run --all-files
   ```

5. **Check config file**:
   ```bash
   cat .pre-commit-config.yaml
   # Verify mdtoken hook is configured
   ```

---

### "Hook Failed" with No Output

**Problem**: Pre-commit fails but shows no error message.

**Solutions**:

1. **Run with verbose flag**:
   ```bash
   pre-commit run --verbose --all-files
   ```

2. **Run mdtoken directly**:
   ```bash
   # Test mdtoken command
   mdtoken check --verbose
   ```

3. **Check hook logs**:
   ```bash
   # Pre-commit stores logs
   cat ~/.cache/pre-commit/pre-commit.log
   ```

4. **Reinstall hook**:
   ```bash
   pre-commit uninstall
   pre-commit clean
   pre-commit install
   pre-commit run --all-files
   ```

---

### "mdtoken: command not found" in Hook

**Problem**: Pre-commit can't find mdtoken command.

**Cause**: Pre-commit uses its own virtual environment.

**Solutions**:

1. **Use repo local hook**:
   ```yaml
   repos:
     - repo: local
       hooks:
         - id: markdown-token-limit
           name: Check Markdown Token Limits
           entry: python -m mdtoken check
           language: system
           files: \.md$
   ```

2. **Specify Python environment**:
   ```yaml
   repos:
     - repo: https://github.com/stefanrmmr/mdtoken
       rev: v1.0.0
       hooks:
         - id: markdown-token-limit
           language: python
           additional_dependencies: ['mdtoken']
   ```

---

## Token Counting Issues

### "Tokens Don't Match My Expectations"

**Problem**: Token counts differ from manual calculations.

**Explanation**:

1. **Words ≠ Tokens**:
   ```python
   # Word count is not token count
   text = "Hello world!"
   words = len(text.split())  # 2 words
   tokens = counter.count_tokens(text)  # 3 tokens

   # Tokens can be subwords
   text = "tokenization"
   # May be split into: "token" + "ization" = 2 tokens
   ```

2. **Different encodings give different counts**:
   ```python
   from mdtoken.counter import TokenCounter

   # GPT-4 encoding
   counter_gpt4 = TokenCounter("cl100k_base")
   count1 = counter_gpt4.count_tokens("Hello world")  # 2 tokens

   # GPT-4o encoding
   counter_gpt4o = TokenCounter("o200k_base")
   count2 = counter_gpt4o.count_tokens("Hello world")  # May differ
   ```

3. **Approximate formula** (rough estimate):
   ```
   tokens ≈ words * 1.3
   tokens ≈ characters / 4
   ```

**Verification**:
```python
from mdtoken.counter import TokenCounter

counter = TokenCounter()
text = open("your-file.md").read()
tokens = counter.count_tokens(text)
print(f"Tokens: {tokens}")
```

---

### "UnicodeDecodeError" When Reading Files

**Problem**: mdtoken can't read file due to encoding issues.

**Error Message**:
```
OSError: Failed to read file 'file.md' with encoding 'utf-8'
```

**Solutions**:

1. **Check file encoding**:
   ```bash
   file -I your-file.md
   # Example output: text/plain; charset=utf-8
   ```

2. **Convert to UTF-8**:
   ```bash
   # Using iconv
   iconv -f ISO-8859-1 -t UTF-8 file.md > file-utf8.md

   # Using dos2unix for line endings
   dos2unix file.md
   ```

3. **Programmatic handling**:
   ```python
   from mdtoken.counter import TokenCounter

   counter = TokenCounter()

   # Try different encodings
   for encoding in ['utf-8', 'latin-1', 'cp1252']:
       try:
           tokens = counter.count_file_tokens(path, encoding=encoding)
           print(f"Success with {encoding}: {tokens} tokens")
           break
       except OSError:
           continue
   ```

---

## Performance Problems

### "mdtoken is slow on my repository"

**Problem**: Token checking takes too long.

**Expected Performance**:
- 5 files: < 500ms
- 10 files: < 1000ms
- 100 files: < 5000ms
- Per-file: ~0.3ms for 2000 tokens

**Optimization Steps**:

1. **Use exclusion patterns**:
   ```yaml
   exclude:
     - "node_modules/**"      # Often has many MD files
     - "vendor/**"
     - "**/archive/**"
     - "**/.cache/**"
   ```

2. **Check only changed files** (pre-commit does this automatically):
   ```bash
   # Manual workflow
   git diff --name-only | grep '.md$' | xargs mdtoken check
   ```

3. **Profile performance**:
   ```bash
   # Time the check
   time mdtoken check

   # Verbose output shows file count
   mdtoken check --verbose
   ```

4. **Check for large files**:
   ```bash
   # Find large markdown files
   find . -name "*.md" -size +1M
   ```

5. **Measure token counting speed**:
   ```python
   import time
   from mdtoken.counter import TokenCounter

   counter = TokenCounter()
   text = open("large-file.md").read()

   start = time.time()
   tokens = counter.count_tokens(text)
   elapsed = time.time() - start

   print(f"Counted {tokens:,} tokens in {elapsed*1000:.2f}ms")
   ```

**If Still Slow**:
- Check CPU usage during execution
- Verify SSD vs HDD performance
- Profile with `python -m cProfile -m mdtoken check`

---

## CI/CD Integration Issues

### GitHub Actions: "mdtoken: command not found"

**Problem**: CI can't find mdtoken after installation.

**Solution**:

```yaml
- name: Install mdtoken
  run: |
    python -m pip install --upgrade pip
    pip install mdtoken

- name: Check token limits
  run: python -m mdtoken check --verbose
```

**Alternative** (install from repo):
```yaml
- name: Install mdtoken
  run: pip install git+https://github.com/stefanrmmr/mdtoken.git@v1.0.0
```

---

### CI Fails But Local Passes

**Problem**: mdtoken passes locally but fails in CI.

**Common Causes**:

1. **Different configurations**:
   ```bash
   # Ensure .mdtokenrc.yaml is committed
   git add .mdtokenrc.yaml
   git commit -m "Add mdtoken config"
   git push
   ```

2. **Different files being checked**:
   ```bash
   # CI might have files not present locally
   # Pull latest changes
   git pull
   ```

3. **Different Python versions**:
   ```yaml
   # Pin Python version in CI
   - uses: actions/setup-python@v4
     with:
       python-version: '3.11'  # Match your local version
   ```

4. **Encoding differences** (Windows vs Linux):
   ```yaml
   # Normalize line endings
   - name: Normalize line endings
     run: |
       git config core.autocrlf false
       git rm --cached -r .
       git reset --hard
   ```

---

## Common Error Messages

### ConfigError: "default_limit must be a positive integer"

**Cause**: Invalid limit value in configuration.

**Fix**:
```yaml
# ✗ Wrong
default_limit: -1000
default_limit: "4000"   # String instead of number
default_limit: 0        # Zero not allowed

# ✓ Correct
default_limit: 4000
```

---

### "FileNotFoundError: File not found"

**Cause**: Specified file doesn't exist.

**Debug**:
```bash
# Check if file exists
ls -la README.md

# Check current directory
pwd

# Run from correct directory
cd /path/to/project
mdtoken check
```

---

### "Failed to load tiktoken encoding 'xyz'"

**Cause**: Invalid or unsupported encoding name.

**Valid Encodings**:
- `cl100k_base` (GPT-4, GPT-3.5-turbo)
- `o200k_base` (GPT-4o)
- `p50k_base` (Codex, text-davinci)
- `r50k_base` (GPT-3)

**Fix**:
```yaml
# Use valid encoding
encoding: "cl100k_base"

# Or use model name
model: "gpt-4"
```

---

### "Total tokens X exceeds total_limit Y"

**Cause**: Aggregate token count exceeds configured total limit.

**Solutions**:

1. **Increase total limit**:
   ```yaml
   total_limit: 100000  # Increase as needed
   ```

2. **Reduce individual file sizes**:
   - Split large files
   - Archive old content
   - Move to subdirectories with exclusions

3. **Remove total limit**:
   ```yaml
   total_limit: null  # Disable aggregate limit
   ```

4. **Check what's consuming tokens**:
   ```bash
   mdtoken check --verbose
   # Shows per-file token counts
   ```

---

## Getting Help

If you encounter issues not covered here:

1. **Check existing issues**: [GitHub Issues](https://github.com/stefanrmmr/mdtoken/issues)
2. **Run with verbose flag**: `mdtoken check --verbose`
3. **Check version**: `mdtoken --version`
4. **Verify configuration**: Validate `.mdtokenrc.yaml` syntax
5. **Test with minimal config**: Use default configuration first
6. **Enable debug logging**:
   ```bash
   DEBUG=true mdtoken check
   ```

### Creating a Bug Report

Include:
- mdtoken version (`mdtoken --version`)
- Python version (`python --version`)
- Operating system
- Configuration file (`.mdtokenrc.yaml`)
- Full error message with traceback
- Steps to reproduce

**Example**:
```markdown
## Bug Report

**mdtoken version**: 1.0.0
**Python version**: 3.11.5
**OS**: Ubuntu 22.04

**Config** (`.mdtokenrc.yaml`):
\```yaml
default_limit: 4000
model: "gpt-4"
\```

**Error**:
\```
ConfigError: Unknown model 'gpt-4'
\```

**Steps to reproduce**:
1. Create config with model: "gpt-4"
2. Run `mdtoken check`
3. Error occurs
```

---

## See Also

- [Examples](examples.md) - Usage examples
- [FAQ](faq.md) - Frequently asked questions
- [API Documentation](api.md) - Programmatic usage
- [README](../README.md) - Getting started guide
