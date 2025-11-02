# mdtoken Implementation Plan

**Project**: mdtoken - Markdown Token Limit Pre-commit Hook
**Version**: 1.0.0 (MVP)
**Created**: 2025-11-02
**Status**: Planning Complete, Ready for Implementation

---

## Executive Summary

**Objective**: Create a production-ready, open-source pre-commit hook that enforces token count limits on markdown files to prevent context window bloat in AI-assisted development workflows.

**Scope**: MVP (v1.0.0) includes core functionality with accurate token counting, flexible configuration, pre-commit integration, and PyPI distribution. Defers auto-fix, caching, and advanced features to v1.1+.

**Timeline**: ~52 hours total effort, 2-4 weeks calendar time (20-30 hrs/week pace)

**Success Criteria**:
- ✅ Accurate token counting using tiktoken (within 5-10% of Claude)
- ✅ < 1 second execution for typical projects (5-10 files)
- ✅ Comprehensive documentation and examples
- ✅ >80% test coverage with passing CI/CD
- ✅ Published to PyPI and usable via `pip install mdtoken`
- ✅ Works as pre-commit hook with clear error messages

---

## Project Overview

### Problem Statement

Markdown documentation files (CLAUDE.md, memory files, project docs) grow unbounded over time, consuming valuable AI context windows. Manual monitoring is tedious and error-prone, leading to degraded AI assistant performance.

### Solution

Automated token counting integrated into git workflow via pre-commit hooks, providing:
- **Early detection**: Catch bloat before commit
- **Clear feedback**: Actionable messages with suggestions
- **Flexible limits**: Per-file and total repository limits
- **Fast execution**: < 1 second for typical projects
- **Easy integration**: One-line addition to .pre-commit-config.yaml

### Target Users

- AI-assisted developers using Claude Code, Cursor, or similar tools
- Teams maintaining large documentation repositories
- Open-source projects with comprehensive markdown docs
- Anyone managing AI context window consumption

---

## Technical Architecture

### Technology Stack

**Core Dependencies**:
- **Python**: 3.8+ (broad compatibility)
- **tiktoken**: OpenAI's tokenizer library (cl100k_base encoding)
- **PyYAML**: Configuration file parsing
- **click**: CLI framework (simple, popular)

**Development Dependencies**:
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking

**Distribution**:
- **PyPI**: Public package index
- **pre-commit**: Hook framework integration

### System Components

```
mdtoken/
├── src/mdtoken/
│   ├── __init__.py              # Package initialization
│   ├── __version__.py           # Version string
│   ├── cli.py                   # Command-line interface
│   ├── counter.py               # Token counting engine (tiktoken)
│   ├── config.py                # Configuration loading (YAML)
│   ├── schema.py                # Config validation
│   ├── matcher.py               # File discovery and filtering
│   ├── enforcer.py              # Limit checking logic
│   └── reporter.py              # Violation reporting
├── tests/
│   ├── test_counter.py          # Token counting tests
│   ├── test_config.py           # Configuration tests
│   ├── test_matcher.py          # File matching tests
│   ├── test_enforcer.py         # Enforcement tests
│   ├── test_edge_cases.py       # Edge case handling
│   ├── test_performance.py      # Performance benchmarks
│   └── integration/
│       └── test_git_workflow.py # End-to-end tests
├── docs/
│   ├── api.md                   # API documentation
│   ├── examples.md              # Usage examples
│   ├── troubleshooting.md       # Common issues
│   └── faq.md                   # Frequently asked questions
├── pyproject.toml               # Package metadata
├── setup.py                     # Backward compatibility
├── .pre-commit-hooks.yaml       # Pre-commit hook definition
└── README.md                    # Primary documentation
```

### Data Flow

```
User runs 'git commit'
    ↓
Pre-commit framework invokes mdtoken
    ↓
1. Load configuration (.mdtokenrc.yaml)
2. Discover markdown files (glob patterns)
3. Filter files (exclude patterns)
4. Count tokens for each file (tiktoken)
5. Check against limits (per-file + total)
6. Report violations (if any)
    ↓
Exit code 0 (pass) or 1 (fail)
    ↓
Git commit succeeds or is blocked
```

### Configuration Schema

```yaml
# .mdtokenrc.yaml
default_limit: 5000              # Default for files not explicitly listed

limits:                          # Per-file or per-pattern limits
  "CLAUDE.md": 8000
  "README.md": 3000
  ".claude/memory/*.md": 2000

exclude:                         # Files/patterns to ignore
  - "node_modules/**"
  - "**/archive/**"
  - "**/.git/**"

total_limit: 50000               # Optional: Total repo limit
fail_on_exceed: true             # Exit 1 on violations (default: true)
```

---

## Implementation Phases

### Phase 1: Project Foundation (3 tasks, ~6 hours)

**Goal**: Establish project structure, development environment, and basic CLI skeleton.

**Tasks**:
1. **TASK-001**: Setup Python package structure
   - Create pyproject.toml with metadata
   - Setup src/mdtoken/ package layout
   - Configure entry points for CLI
   - **AC**: Package installs with `pip install -e .`

2. **TASK-002**: Setup development environment
   - Create requirements.txt (core) and requirements-dev.txt
   - Configure linting (ruff), formatting (black), type checking (mypy)
   - Create Makefile with common commands
   - **AC**: All dev tools run without errors

3. **TASK-003**: Create basic CLI skeleton
   - Implement src/mdtoken/cli.py with click
   - Add --version, --help, check command (placeholder)
   - Configure entry point in pyproject.toml
   - **AC**: CLI invokable after installation

**Deliverables**:
- Working Python package structure
- Development tools configured
- Basic CLI that can be invoked

**Quality Gate**: Project builds, CLI runs, dev tools configured

---

### Phase 2: Core Implementation (4 tasks, ~14 hours)

**Goal**: Implement core token counting, configuration, file matching, and enforcement logic.

**Tasks**:
4. **TASK-004**: Implement token counting engine (3 hours)
   - Create TokenCounter class using tiktoken
   - Methods: count_tokens(text), count_file_tokens(path)
   - Handle UTF-8, performance optimization
   - **AC**: Counts 10K tokens in < 100ms

5. **TASK-005**: Implement configuration loader (4 hours)
   - Create Config class for YAML parsing
   - Schema validation with sensible defaults
   - Clear error messages for invalid configs
   - **AC**: Loads valid configs, rejects invalid with helpful errors

6. **TASK-006**: Implement file matching logic (3 hours)
   - Create FileMatcher class for glob patterns
   - Support exclude patterns, recursive traversal
   - Return (filepath, limit) tuples
   - **AC**: Correctly matches files per config

7. **TASK-007**: Implement limit enforcement and reporting (4 hours)
   - Create LimitEnforcer to check files against limits
   - Generate violation reports with suggestions
   - Handle total_limit checking
   - **AC**: Accurate violation detection and reporting

**Deliverables**:
- Functional token counting
- Config loading and validation
- File discovery and filtering
- Limit enforcement with clear output

**Quality Gate**: Token counting accurate, config works, violations detected correctly

---

### Phase 3: Pre-commit Integration (2 tasks, ~3 hours)

**Goal**: Integrate with pre-commit framework for git workflow automation.

**Tasks**:
8. **TASK-008**: Create pre-commit hook definition (1 hour)
   - Create .pre-commit-hooks.yaml
   - Define hook ID, entry point, file patterns
   - **AC**: Validates with `pre-commit validate-config`

9. **TASK-009**: Implement pre-commit hook script (2 hours)
   - Handle file arguments from pre-commit
   - Return appropriate exit codes (0/1)
   - Support --dry-run flag
   - **AC**: Works with `pre-commit try-repo`

**Deliverables**:
- Pre-commit hook definition
- Integration with pre-commit framework
- Correct exit code handling

**Quality Gate**: Pre-commit integration functional, blocks commits on violations

---

### Phase 4: Testing & Quality (5 tasks, ~12 hours)

**Goal**: Achieve >80% test coverage with comprehensive unit, integration, and performance tests.

**Tasks**:
10. **TASK-010**: Write comprehensive unit tests (4 hours)
    - Tests for counter, config, matcher, enforcer
    - Coverage >80% (pytest-cov)
    - **AC**: All tests pass, coverage target met

11. **TASK-011**: Write integration tests (3 hours)
    - End-to-end tests with temporary git repos
    - Simulate real commit workflows
    - **AC**: Integration tests pass consistently

12. **TASK-012**: Edge case and error handling tests (2 hours)
    - Empty files, invalid UTF-8, missing config
    - Graceful error handling
    - **AC**: All edge cases handled with clear errors

13. **TASK-013**: Performance benchmarks (2 hours)
    - Benchmark 5, 10, 100 files
    - Performance targets: < 1s for typical projects
    - **AC**: Meets performance requirements

14. **TASK-014**: Setup CI/CD with GitHub Actions (1 hour)
    - Test workflow for Python 3.8-3.12
    - Linting, type checking, coverage
    - **AC**: CI green, badges added to README

**Deliverables**:
- >80% test coverage
- Passing CI/CD pipeline
- Performance benchmarks met
- Comprehensive test suite

**Quality Gate**: Tests passing, coverage >80%, CI green, performance targets met

---

### Phase 5: Documentation (3 tasks, ~6 hours)

**Goal**: Create comprehensive user and developer documentation.

**Tasks**:
15. **TASK-015**: Write comprehensive README (3 hours)
    - Installation, usage, configuration
    - Examples, troubleshooting
    - Badges, contributing reference
    - **AC**: README covers all user needs

16. **TASK-016**: Write API documentation (2 hours)
    - Document public API (TokenCounter, Config)
    - Docstrings for all public methods
    - Usage examples for programmatic use
    - **AC**: API fully documented

17. **TASK-017**: Create usage examples and troubleshooting guide (1 hour)
    - Practical examples (5+)
    - Common configurations
    - FAQ, error messages, solutions
    - **AC**: Users can self-serve common issues

**Deliverables**:
- Comprehensive README
- API documentation
- Examples and troubleshooting guides

**Quality Gate**: Documentation complete, users can get started without support

---

### Phase 6: Release Preparation (6 tasks, ~11 hours)

**Goal**: Prepare for public open-source release on GitHub and PyPI.

**Tasks**:
18. **TASK-018**: Prepare PyPI packaging (2 hours)
    - Complete pyproject.toml metadata
    - Build with `python -m build`
    - Test upload to TestPyPI
    - **AC**: Package builds and installs from TestPyPI

19. **TASK-019**: Setup GitHub repository (1 hour)
    - Create repository, set description and topics
    - Issue templates, PR template
    - Code of conduct
    - **AC**: Repository configured professionally

20. **TASK-020**: Write contributing guidelines (2 hours)
    - Development setup instructions
    - Testing, code style, PR guidelines
    - **AC**: Contributors have clear guidance

21. **TASK-021**: Create CHANGELOG and version tagging (1 hour)
    - Initialize CHANGELOG.md (Keep a Changelog format)
    - Document v1.0.0 features
    - Create git tag v1.0.0
    - **AC**: Version consistent across all files

22. **TASK-022**: Publish to PyPI (2 hours)
    - Upload to PyPI
    - Verify installation from public index
    - **AC**: `pip install mdtoken` works

23. **TASK-023**: Create GitHub release and announcement (2 hours)
    - GitHub release v1.0.0 with assets
    - Announcement draft
    - Add to pre-commit.com registry (if applicable)
    - **AC**: Release published, announcement ready

**Deliverables**:
- Published PyPI package
- GitHub repository configured
- Release v1.0.0 announced

**Quality Gate**: Package on PyPI, GitHub release published, ready for users

---

## Task Dependencies and Critical Path

### Critical Path (32 hours)
Tasks that must be completed sequentially for project delivery:

```
TASK-001 (Foundation)
  → TASK-003 (CLI Skeleton)
  → TASK-004 (Token Counter)
  → TASK-005 (Config Loader)
  → TASK-007 (Enforcement)
  → TASK-008 (Pre-commit Definition)
  → TASK-009 (Pre-commit Integration)
  → TASK-010 (Unit Tests)
  → TASK-015 (README)
  → TASK-018 (PyPI Packaging)
  → TASK-021 (Versioning)
  → TASK-022 (PyPI Publish)
```

### Parallel Opportunities

**After TASK-003** (CLI ready):
- TASK-004 (Counter) and TASK-005 (Config) can be developed in parallel

**After TASK-007** (Core complete):
- TASK-016 (API docs) can be written while TASK-010 (tests) are being developed

**After TASK-010** (Tests written):
- TASK-012 (Edge cases), TASK-013 (Performance), TASK-014 (CI) can run in parallel

**After TASK-015** (README complete):
- TASK-017 (Examples) and TASK-019 (GitHub setup) can proceed in parallel

---

## Risk Assessment and Mitigation

### High-Priority Risks

**Risk 1: tiktoken accuracy vs Claude tokenizer**
- **Impact**: Token counts might not match Claude's actual usage
- **Probability**: Medium (known 5-10% variance)
- **Mitigation**:
  - Document expected variance in README
  - Suggest conservative limits (e.g., 90% of desired)
  - Consider supporting multiple tokenizers in v1.1+

**Risk 2: Performance on large repositories**
- **Impact**: Slow execution could frustrate users
- **Probability**: Low (tiktoken is fast)
- **Mitigation**:
  - Implement early performance tests (TASK-013)
  - Profile and optimize if needed
  - Defer caching to v1.1 if performance acceptable

**Risk 3: Complex glob pattern edge cases**
- **Impact**: Files incorrectly matched or excluded
- **Probability**: Medium (glob patterns can be tricky)
- **Mitigation**:
  - Comprehensive tests with various patterns (TASK-006)
  - Clear documentation with examples
  - Leverage Python's pathlib for robust matching

### Medium-Priority Risks

**Risk 4: PyPI publishing complications**
- **Impact**: Delayed release
- **Probability**: Low (well-documented process)
- **Mitigation**:
  - Test with TestPyPI first (TASK-018)
  - Follow official PyPI packaging guide
  - Have backup plan for manual upload

**Risk 5: Pre-commit framework compatibility issues**
- **Impact**: Hook doesn't work in some environments
- **Probability**: Low (pre-commit is mature)
- **Mitigation**:
  - Test with `pre-commit try-repo` (TASK-009)
  - CI tests with pre-commit integration
  - Clear troubleshooting docs

---

## Quality Standards

### Code Quality
- **Coverage**: >80% test coverage (enforced by CI)
- **Linting**: Ruff with default rules, no warnings
- **Formatting**: Black with default settings
- **Type Hints**: mypy strict mode on public API
- **Docstrings**: All public functions and classes

### Testing Standards
- **Unit Tests**: Every module has corresponding test file
- **Integration Tests**: End-to-end git workflow scenarios
- **Edge Cases**: Empty files, invalid configs, encoding issues
- **Performance**: Benchmarks for 5, 10, 100 file scenarios

### Documentation Standards
- **README**: Installation, usage, config, examples, troubleshooting
- **API Docs**: All public API documented with examples
- **Code Comments**: Complex logic explained inline
- **Changelog**: All user-facing changes documented

### Release Standards
- **Version**: Semantic versioning (v1.0.0 for MVP)
- **Changelog**: Keep a Changelog format
- **Git Tags**: Annotated tags for releases
- **GitHub Release**: Assets (wheel, sdist) attached

---

## Success Metrics

### Functional Metrics
- ✅ Token counting accuracy: Within 5-10% of Claude tokenizer
- ✅ Execution speed: < 1 second for 5-10 files, < 5 seconds for 100 files
- ✅ Test coverage: >80% across all modules
- ✅ CI/CD: All tests passing on Python 3.8-3.12

### Quality Metrics
- ✅ Zero linting errors (ruff)
- ✅ Zero type errors (mypy)
- ✅ All acceptance criteria met for each task
- ✅ All quality gates passed

### User Experience Metrics
- ✅ Clear error messages with actionable suggestions
- ✅ Installation works with single `pip install mdtoken`
- ✅ Configuration file is intuitive (YAML)
- ✅ Documentation answers common questions (FAQ)

### Release Metrics
- ✅ Published to PyPI successfully
- ✅ GitHub repository public and configured
- ✅ v1.0.0 release created
- ✅ Ready for community contributions

---

## Timeline and Effort Estimates

### By Phase

| Phase | Tasks | Hours | Calendar Time |
|-------|-------|-------|---------------|
| Phase 1: Foundation | 3 | 6 | 1-2 days |
| Phase 2: Core | 4 | 14 | 3-5 days |
| Phase 3: Pre-commit | 2 | 3 | 1 day |
| Phase 4: Testing | 5 | 12 | 2-3 days |
| Phase 5: Documentation | 3 | 6 | 1-2 days |
| Phase 6: Release | 6 | 11 | 2-3 days |
| **Total** | **23** | **52** | **2-4 weeks** |

### Critical Path vs Parallel Work
- **Critical Path**: 32 hours (61% of total)
- **Parallel Opportunities**: 20 hours (39% of total)
- **Minimum Calendar Time**: 2 weeks at 30 hrs/week
- **Comfortable Pace**: 3-4 weeks at 20 hrs/week

---

## Deferred to v1.1+

The following features were explicitly deferred from v1.0.0 MVP to keep scope manageable:

### Auto-fix / File Splitting
- Automatically split files that exceed limits
- Suggest specific content to move to archive
- Complexity: High, requires content analysis

### Token Count Caching
- Cache token counts for unchanged files
- Reduces repeat execution time
- Complexity: Medium, adds state management

### Parallel Processing
- Process multiple files concurrently
- Useful for very large repositories (100+ files)
- Complexity: Low, but adds dependencies

### GitHub Action
- Run checks in CI without pre-commit
- Useful for enforcing on remote
- Complexity: Low, separate workflow file

### IDE Integrations
- VS Code extension for real-time token counts
- Complexity: High, different technology stack

### Multiple Tokenizer Support
- Support Claude, LLaMA, other tokenizers
- Allow user to choose encoding
- Complexity: Medium, API surface expansion

---

## Execution Strategy

### Using Factory Workflow

1. **Task Execution**: Use `/next` command to execute tasks sequentially
2. **State Tracking**: `state.json` maintains current status and dependencies
3. **Quality Gates**: Verify criteria before proceeding to next phase
4. **Flexibility**: Adjust task order if blockers arise

### Recommended Pace

**Week 1**: Phases 1-2 (Foundation + Core)
- Days 1-2: Setup and foundation
- Days 3-5: Core implementation

**Week 2**: Phases 3-4 (Integration + Testing)
- Days 1-2: Pre-commit integration
- Days 3-5: Comprehensive testing

**Week 3**: Phases 5-6 (Documentation + Release)
- Days 1-2: Documentation
- Days 3-5: Release preparation

**Week 4**: Buffer and polish
- Address any gaps
- Final testing
- Publication

---

## Conversion to GitHub Issues (Before Public Release)

Before making the repository public, convert tasks to GitHub issues:

1. **Create Issues**: One issue per task, using labels from state.json
2. **Create Milestones**: One milestone per phase
3. **Archive .claude/**: Move to `.claude-dev-archive/` (optional)
4. **Update README**: Remove Factory workflow references

**Rationale**: Public repository should use standard GitHub project management for external contributors.

---

## Getting Started

### Next Steps

1. **Review this plan**: Ensure all requirements are covered
2. **Execute TASK-001**: Begin with foundation setup
3. **Use `/next` workflow**: Let Factory guide task execution
4. **Track progress**: Monitor via state.json
5. **Pass quality gates**: Verify each phase completion

### How to Execute

```bash
# In Claude Code session
cd ~/projects/mdtoken

# Review plan
cat .claude/implementation-plan.md

# Start first task
/next

# After completing a task
/next  # Automatically picks next available task

# Check status
/status
```

---

## Appendix: Requirements Traceability

All requirements from `docs/requirements.md` are mapped to implementation tasks:

| Requirement | Tasks | Status |
|-------------|-------|--------|
| FR-1: Token counting | TASK-004 | Pending |
| FR-2: Config loading | TASK-005 | Pending |
| FR-3: File discovery | TASK-006 | Pending |
| FR-4: Limit enforcement | TASK-007 | Pending |
| FR-5: Error reporting | TASK-007 | Pending |
| FR-6: Pre-commit integration | TASK-008, TASK-009 | Pending |
| FR-7: CLI interface | TASK-003 | Pending |
| NFR-1: Performance < 1s | TASK-013 | Pending |
| NFR-2: Python 3.8+ | TASK-001, TASK-014 | Pending |
| NFR-3: Test coverage >80% | TASK-010, TASK-011, TASK-012 | Pending |
| NFR-4: Documentation | TASK-015, TASK-016, TASK-017 | Pending |
| NFR-5: PyPI distribution | TASK-018, TASK-022 | Pending |
| NFR-6: MIT license | TASK-001 (LICENSE exists) | Complete |
| NFR-7: Error handling | TASK-012 | Pending |

---

**Plan Status**: ✅ Complete and Ready for Execution
**Next Action**: Review plan, then execute TASK-001
**Questions**: Review with team if needed, otherwise proceed with `/next`
