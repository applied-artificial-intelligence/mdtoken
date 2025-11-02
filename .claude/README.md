# Claude Code Configuration

This project is configured with Claude Code support for Python development.

## Enabled Plugins

- **system@local** - System utilities (audit, cleanup, setup, status)
- **workflow@local** - Task workflow (explore, plan, next, ship)
- **memory@local** - Memory management, knowledge persistence, handoff
- **development@local** - Development tools (analyze, review, test, fix, run, git operations)

## MCP Servers

- **serena** - Semantic code understanding (70-90% token reduction for code operations)
- **context7** - Up-to-date library documentation access

## Available Commands

Run `/help` to see all available commands from enabled plugins.

### Key Commands for Python Development

- `/test` - Run tests with pytest
- `/analyze` - Deep codebase analysis (uses Serena for semantic understanding)
- `/fix` - Debug errors and apply fixes
- `/review` - Code review and quality analysis
- `/git` - Unified git operations (commit, pr, issue)

### Workflow Commands

- `/explore` - Analyze requirements and create work breakdown
- `/plan` - Create implementation plan with dependencies
- `/next` - Execute next available task
- `/ship` - Deliver completed work

## Permissions

Standard Python development permissions are configured:
- ✅ pytest, ruff, mypy, black, git, make commands
- ✅ Read Python, markdown, TOML files
- ✅ Write/edit files in src/, tests/, docs/
- ❌ Dangerous commands (rm -rf, sudo) blocked
- ❌ Modifying pyproject.toml requires explicit confirmation

## Next Steps

1. Restart your Claude Code session to load the new configuration
2. Run `/system:status` to verify setup
3. Use `/test` to run the test suite
4. Use `/analyze` for deep code analysis with Serena
