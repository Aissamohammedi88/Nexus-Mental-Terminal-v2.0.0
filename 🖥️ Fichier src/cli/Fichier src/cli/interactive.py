#!/usr/bin/env python3
"""
Terminal interactif avec interface Rich
"""

import os
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.live import Live

from ..core.terminal import MentalTerminal


def run_interactive(terminal: MentalTerminal, theme: str = "monokai"):
    """
    Lancer le terminal interactif
    """
    console = Console()
    
    # En-tête
    title = Text()
    title.append("🧠 ", style="bold magenta")
    title.append("NEXUS MENTAL TERMINAL", style="bold cyan")
    title.append(" v3.0.0", style="dim")
    
    console.print(Panel(title, border_style="cyan", padding=(1, 2)))
    console.print(f"Session: [bold]{terminal.session_id[:8]}[/bold] | CWD: [yellow]{terminal.vfs.current_dir}[/yellow]")
    console.print("[dim]Tapez 'help' pour l'aide, 'exit' pour quitter\n[/dim]")
    
    while True:
        try:
            # Prompt stylisé
            cwd = terminal.vfs.current_dir
            prompt_text = f"user@nexus:[yellow]{cwd}[/yellow]$ "
            
            command = Prompt.ask(prompt_text, console=console)
            
            if not command or command.strip() == "":
                continue
            
            command = command.strip()
            
            if command.lower() in ("exit", "quit"):
                console.print("[green]👋 À bientôt![/green]")
                break
            
            if command.lower() == "clear":
                console.clear()
                continue
            
            # Gestion spéciale Python
            if command.startswith("PY:") or command.startswith("python ") or command.startswith("py "):
                if command.startswith("PY:"):
                    code = command[3:].strip()
                else:
                    code = command[6:].strip() if command.startswith("python ") else command[3:].strip()
                
                result = terminal.python(code)
            else:
                result = terminal.bash(command)
            
            # Affichage stylisé
            if result.stdout:
                console.print(Syntax(result.stdout.rstrip(), "bash", theme=theme, line_numbers=False))
            
            if result.stderr:
                console.print(f"[red]{result.stderr.rstrip()}[/red]")
            
            if result.duration_ms > 100:
                console.print(f"[dim]⏱ {result.duration_ms:.0f}ms[/dim]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]^C[/yellow]")
        except EOFError:
            console.print("[green]👋 À bientôt![/green]")
            break
    
    # Sauvegarder automatiquement
    terminal.save_session()
