"""Command-line interface for mdtoken."""
import sys
import click
from mdtoken.__version__ import __version__


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def main(ctx, version):
    """
    mdtoken - Markdown Token Limit Pre-commit Hook

    Enforce token count limits on markdown files to prevent AI context window bloat.

    Use 'mdtoken check' to validate markdown files against configured token limits.
    """
    if version:
        click.echo(f"mdtoken version {__version__}")
        ctx.exit(0)

    # If no command provided and not --version, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


@main.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('--config', default='.mdtokenrc.yaml', help='Path to configuration file')
@click.option('--dry-run', is_flag=True, help='Check files without failing on violations')
def check(files, config, dry_run):
    """
    Check markdown files against token count limits.

    FILES: Markdown files to check. If none provided, uses glob patterns from config.
    """
    click.echo(f"mdtoken check (placeholder implementation)")
    click.echo(f"Config: {config}")
    click.echo(f"Dry run: {dry_run}")

    if files:
        click.echo(f"Files to check: {len(files)}")
        for file in files:
            click.echo(f"  - {file}")
    else:
        click.echo("No files provided - would use config glob patterns")

    click.echo("\nThis is a placeholder. Full implementation coming soon.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
