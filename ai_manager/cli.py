"""
Command-line interface for AI Manager.
"""

import click
import json
from pathlib import Path
from .core import AIContextManager


@click.group()
@click.version_option(version="1.0.0")
def main():
    """AI Manager - Intelligent AI context management for any project."""
    pass


@main.command()
@click.argument("project_name")
@click.option("--type", "-t", default="general", help="Project type (general, web_application, data_engineering, desktop_application)")
@click.option("--path", "-p", type=click.Path(), help="Project path (default: current directory)")
def init(project_name: str, type: str, path: str):
    """Initialize AI context for a project."""
    project_path = Path(path) if path else Path.cwd()
    
    manager = AIContextManager(project_path)
    
    if manager.init(project_name, type):
        click.echo(f"AI context initialized for '{project_name}' ({type}) in {project_path}")
        click.echo(f"Context files created in: {manager.context_dir}")
    else:
        click.echo("Failed to initialize AI context.", err=True)
        raise click.Abort()


@main.command()
@click.option("--path", "-p", type=click.Path(), help="Project path (default: current directory)")
def status(path: str):
    """Show status of AI context system."""
    project_path = Path(path) if path else Path.cwd()
    
    manager = AIContextManager(project_path)
    status_info = manager.status()
    
    click.echo(f"AI Manager Status")
    click.echo(f"Project: {status_info['project_path']}")
    click.echo(f"Context directory: {'Exists' if status_info['context_dir_exists'] else 'Not found'}")
    click.echo(f"Configuration: {'Exists' if status_info['config_exists'] else 'Not found'}")
    
    if status_info['context_files']:
        click.echo(f"Context files ({len(status_info['context_files'])}):")
        for file_info in status_info['context_files']:
            click.echo(f"  - {file_info['name']} ({file_info['size']} bytes, modified: {file_info['modified']})")
    else:
        click.echo("No context files found.")


@main.command()
@click.option("--path", "-p", type=click.Path(), help="Project path (default: current directory)")
def maintain(path: str):
    """Maintain AI context system."""
    project_path = Path(path) if path else Path.cwd()
    
    manager = AIContextManager(project_path)
    
    if manager.maintain():
        click.echo("AI context maintenance completed successfully.")
    else:
        click.echo("AI context maintenance failed.", err=True)
        raise click.Abort()


@main.command()
@click.option("--path", "-p", type=click.Path(), help="Project path (default: current directory)")
def version(path: str):
    """Show version information."""
    project_path = Path(path) if path else Path.cwd()
    config_file = project_path / ".ai-context.yaml"
    
    if config_file.exists():
        try:
            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f)
            
            click.echo(f"AI Manager version: {config.get('version', 'unknown')}")
            click.echo(f"Project: {config.get('project_name', 'unknown')}")
            click.echo(f"Created: {config.get('created', 'unknown')}")
        except Exception as e:
            click.echo(f"Error reading configuration: {e}", err=True)
    else:
        click.echo("No AI context configuration found. Run 'ai-context init' first.")


if __name__ == "__main__":
    main()
