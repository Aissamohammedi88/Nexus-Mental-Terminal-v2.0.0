
---

## 📝 Fichier final `main.py`

```python
#!/usr/bin/env python3
"""
Point d'entrée Nexus Terminal Gateway v4.0
Usage: nexus-gateway start
"""

import click
import uvicorn
from src.config.settings import settings

@click.group()
def cli():
    """Nexus Terminal Gateway v4.0"""
    pass

@cli.command()
def start():
    """Lancer le gateway"""
    click.echo("🚀 Starting Nexus Terminal Gateway v4.0...")
    click.echo(f"📍 API: http://{settings.API_HOST}:{settings.API_PORT}")
    click.echo(f"🔒 Whitelist: {settings.ENABLE_COMMAND_WHITELIST}")
    click.echo(f"🛡️ Audit: {settings.LOG_ALL_COMMANDS}")
    
    uvicorn.run(
        "src.gateway.api_server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False,
        log_level="info"
    )

@cli.command()
def demo():
    """Mode démonstration"""
    from src.gateway.ssh_client import SSHClient, SSHConfig
    from src.gateway.command_validator import validator
    
    click.echo("=== Démo Nexus Terminal ===\n")
    
    commands = [
        "whoami",
        "ls -la /tmp",
        "df -h",
        "cat /etc/os-release",
    ]
    
    for cmd in commands:
        click.echo(f"$ {cmd}")
        result = validator.validate(cmd)
        click.echo(f"  ✓ Allowed: {result.allowed} | Risk: {result.risk_level.value}\n")

if __name__ == "__main__":
    cli()
