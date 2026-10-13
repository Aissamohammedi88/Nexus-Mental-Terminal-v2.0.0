#!/usr/bin/env python3
"""
Nexus Mental Terminal CLI - Point d'entrée principal
"""

import click
import os
from pathlib import Path
from typing import Optional

from ..core.terminal import MentalTerminal
from ..utils.config import Config
from ..utils.logger import setup_logger


@click.group()
@click.version_option(version="3.0.0", prog_name="nexus-mental-terminal")
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Mode verbose détaillé"
)
@click.option(
    "--data-path", "-d",
    type=click.Path(),
    default=Path.home() / ".nexus_mental",
    help="Chemin de stockage des sessions"
)
@click.option(
    "--log-level", "-l",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO"
)
@click.pass_context
def cli(ctx, verbose: bool, data_path: Path, log_level: str):
    """
    🧠 Nexus Mental Terminal v3.0
    
    Terminal virtuel Ubuntu/Unix complet sans accès système réel.
    
    \b
    Exemples :
      nexus interactive          # Mode interactif
      nexus run 'apt list'       # Exécuter une commande
      nexus session --list       # Lister les sessions
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['data_path'] = Path(data_path)
    ctx.obj['log_level'] = log_level
    
    # Initialiser configuration
    Config.init(data_path, log_level)
    
    # Setup logger
    setup_logger(log_level, verbose)


@cli.command()
@click.pass_context
def interactive(ctx):
    """Mode terminal interactif"""
    from .interactive import run_interactive
    
    terminal = MentalTerminal(
        data_path=ctx.obj['data_path'],
        verbose=ctx.obj['verbose']
    )
    
    run_interactive(terminal)


@cli.command()
@click.argument('command', nargs=-1, required=True)
@click.option('--session', '-s', help="ID de session")
@click.pass_context
def run(ctx, command: tuple, session: Optional[str]):
    """Exécuter une commande"""
    terminal = MentalTerminal(
        data_path=ctx.obj['data_path'],
        verbose=ctx.obj['verbose']
    )
    
    if session:
        terminal.load_session(session)
    
    cmd_str = ' '.join(command)
    result = terminal.execute(cmd_str)
    
    print(result)
    
    if result.exit_code != 0:
        raise SystemExit(result.exit_code)


@cli.group()
def session():
    """Gérer les sessions"""
    pass


@session.command()
@click.pass_context
def list_sessions(ctx):
    """Lister toutes les sessions"""
    terminal = MentalTerminal(data_path=ctx.obj['data_path'])
    sessions = terminal.list_sessions()
    
    if not sessions:
        click.echo("Aucune session trouvée.")
        return
    
    click.echo(click.style(f"\nSessions ({len(sessions)}):\n", bold=True, fg='cyan'))
    
    for s in sessions:
        created = s.get('created', 'Unknown')[:16]
        commands = s.get('commands_count', 0)
        status = click.style("●", fg='green') if s.get('active') else "○"
        
        click.echo(f"{status} {s['id'][:8]:<10} {created:<17} {commands:>5} commandes")


@session.command()
@click.argument('session_id')
@click.pass_context
def load(ctx, session_id: str):
    """ Charger une session """
    terminal = MentalTerminal(data_path=ctx.obj['data_path'])
    success = terminal.load_session(session_id)
    
    if success:
        click.echo(click.style(f"✓ Session chargée: {session_id}", fg='green'))
    else:
        click.echo(click.style(f"✗ Session introuvable: {session_id}", fg='red'))


@session.command()
@click.argument('session_id')
@click.pass_context
def delete(ctx, session_id: str):
    """ Supprimer une session """
    if not click.confirm(f"Supprimer la session {session_id}?"):
        click.echo("Annulé.")
        return
    
    terminal = MentalTerminal(data_path=ctx.obj['data_path'])
    terminal.delete_session(session_id)
    click.echo(click.style(f"✓ Session supprimée: {session_id}", fg='green'))


@cli.command()
@click.pass_context
def stats(ctx):
    """ Afficher les statistiques """
    terminal = MentalTerminal(data_path=ctx.obj['data_path'])
    statistics = terminal.stats()
    
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    table = Table(title="📊 Nexus Mental Statistics", show_header=True, header_style="bold cyan")
    
    table.add_column("Metric", style="yellow")
    table.add_column("Value", justify="right")
    
    metrics = [
        ("Total Commands", f"{statistics['total_commands']:,}"),
        ("Successful", f"{statistics['successful']:,}"),
        ("Failed", f"{statistics['failed']:,}"),
        ("Success Rate", f"{statistics['success_rate']}%"),
        ("Active Sessions", f"{statistics['active_sessions']}"),
    ]
    
    for metric, value in metrics:
        table.add_row(metric, value)
    
    console.print(table)


@cli.command()
@click.pass_context
def demo(ctx):
    """ Mode démonstration rapide """
    from ..core.terminal import MentalTerminal
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    terminal = MentalTerminal(data_path=ctx.obj['data_path'])
    
    demo_commands = [
        "whoami",
        "ls -la",
        "apt list",
        "apt install nginx",
        "snap install firefox",
        "systemctl status docker",
        "PY: print('Hello from Nexus!')"
    ]
    
    panel = Panel(
        "[bold green]Running Demo[/bold green]",
        border_style="cyan"
    )
    console.print(panel)
    
    for cmd in demo_commands:
        console.print(f"\n[bold yellow]$ {cmd}[/bold yellow]")
        result = terminal.execute(cmd)
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[dim]{result.stderr}[/dim]")


@cli.command()
@click.pass_context
def reset(ctx):
    """ Réinitialiser toutes les données """
    if not click.confirm("⚠️  Cela supprimera TOUS les sessions et données. Continuer?"):
        click.echo("Annulé.")
        return
    
    terminal = MentalTerminal(data_path=ctx.obj['data_path'])
    terminal.reset_all()
    click.echo(click.style("✓ Données réinitialisées", fg='green'))


if __name__ == '__main__':
    cli(obj={})
