#!/usr/bin/env python3
"""
Configuration centrale - SÉCURITÉ MAXIMALE
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Configuration du Gateway - Charger depuis .env"""
    
    # === SÉCURITÉ AUTHENTIFICATION ===
    SECRET_KEY: str = Field(default=os.urandom(32).hex(), description="Clé secrète JWT")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    API_RATE_LIMIT_PER_MINUTE: int = 100
    
    # === PORTS ===
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 9080
    WEBSOCKET_PORT: int = 9081
    
    # === SSH ===
    SSH_TIMEOUT_SECONDS: int = 30
    SSH_MAX_CONNECTIONS: int = 10
    SSH_KEEPALIVE_INTERVAL: int = 30
    
    # === SÉCURITÉ COMMANDES ===
    ENABLE_COMMAND_WHITELIST: bool = True
    ENABLE_COMMAND_BLACKLIST: bool = True
    ALLOW_SUDO: bool = False  # DÉSACTIVER EN PRODUCTION
    MAX_COMMAND_LENGTH: int = 4096
    MAX_OUTPUT_SIZE_KB: int = 1024
    
    # === AUDIT ===
    LOG_ALL_COMMANDS: bool = True
    LOG_SENSITIVE_DATA: bool = False  # Ne jamais logger de secrets
    AUDIT_LOG_PATH: Path = Path("/var/log/nexus-terminal/audit.log")
    RETENTION_DAYS: int = 90
    
    # === ISOLATION ===
    USE_DOCKER_ISOLATION: bool = True
    CONTAINER_MEMORY_LIMIT_MB: int = 512
    CONTAINER_CPU_LIMIT: float = 1.0
    
    # === BACKUP ===
    BACKUP_ENABLED: bool = true
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Tous les jours à 2h
    BACKUP_RETENTION_DAYS: int = 30
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
