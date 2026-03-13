"""
CLI functionality.
"""
from typing import List, Optional
import click
from ..orchestrator import process_brief, run_analyse, run_veille as run_veille_core
from .utils import ensure_dir, setup_logging

@click.group()
def cli():
    """Bot CLI commands."""
    pass

@cli.command()
@click.argument('brief_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), help='Output directory')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')

def report(
    report_type: str,
    output_dir: Optional[str] = None,
    format: str = 'json',
    verbose: bool = False
):
    """Generate various reports."""
    if verbose:
        setup_logging('DEBUG')
    
    if output_dir:
        ensure_dir(output_dir)
    
    # TODO: Implement report generation
    click.echo(f"Generating {report_type} report in {format} format")
    if output_dir:
        click.echo(f"Output directory: {output_dir}")

if __name__ == '__main__':
    cli()

__all__ = [
    'cli',
    'brief',
    'analyse',
    'veille',
    'report'
]
