#!/usr/bin/env python3
"""
Core Terminal Engine - Version optimisée avec persistance SQLite
"""

import json
import sqlite3
import time
import uuid
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field

from .filesystem import VirtualFileSystem
from .commands import MentalBash
from .python_engine import MentalPythonEngine
from .ubuntu.apt import MentalApt
from .ubuntu.snap import MentalSnap
from .ubuntu.flatpak import MentalFlatpak
from .ubuntu.systemd import MentalSystemd


@dataclass
class CommandResult:
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration_ms: float = 0.0
    command: str = ""
    
    def success(self) -> bool:
        return self.exit_code == 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def __str__(self) -> str:
        parts = []
        if self.stdout:
            parts.append(self.stdout.rstrip())
        if self.stderr:
            parts.append(f"[{self.stderr.rstrip()}]")
        if self.exit_code != 0:
            parts.append(f"(exit code: {self.exit_code})")
        return "\n".join(parts)


class MentalTerminal:
    def __init__(self, data_path: Path = None, verbose: bool = False):
        self.data_path = data_path or (Path.home() / ".nexus_mental")
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose
        
        self.vfs = VirtualFileSystem()
        self.bash = MentalBash(self.vfs)
        self.python_engine = MentalPythonEngine(self.vfs)
        
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = time.time()
        self.command_history: List[Dict[str, Any]] = []
        
        self.db_path = self.data_path / "sessions.db"
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created TEXT NOT NULL,
                updated TEXT NOT NULL,
                cwd TEXT NOT NULL,
                active INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                command TEXT NOT NULL,
                stdout TEXT,
                stderr TEXT,
                exit_code INTEGER,
                duration_ms REAL,
                timestamp TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_cmd_session ON commands(session_id);
            CREATE INDEX IF NOT EXISTS idx_cmd_ts ON commands(timestamp);
        """)
        conn.commit()
        
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn.execute(
            "INSERT OR IGNORE INTO sessions(id, created, updated, cwd, active) VALUES(?,?,?,?,1)",
            (self.session_id, now, now, self.vfs.current_dir)
        )
        conn.commit()
        conn.close()
    
    def execute(self, command: str) -> CommandResult:
        start = time.time()
        
        if command.strip().startswith(("python ", "py ", "PY:")):
            result = self.python(command)
        else:
            result = self.bash.execute(command)
        
        result.command = command
        result.duration_ms = round((time.time() - start) * 1000, 2)
        
        self._log_command(result)
        self._update_session()
        
        if self.verbose:
            print(f"[debug] {command} → {result.exit_code} ({result.duration_ms:.0f}ms)")
        
        return result
    
    def python(self, code: str) -> CommandResult:
        return self.python_engine.execute(code)
    
    def bash(self, command: str) -> CommandResult:
        return self.bash.execute(command)
    
    def _log_command(self, result: CommandResult):
        self.command_history.append({
            "command": result.command,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "duration_ms": result.duration_ms,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            INSERT INTO commands(session_id, command, stdout, stderr, exit_code, duration_ms, timestamp)
            VALUES(?,?,?,?,?,?,?)
        """, (
            self.session_id, result.command, result.stdout, 
            result.stderr, result.exit_code, result.duration_ms,
            datetime.datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
    
    def _update_session(self):
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "UPDATE sessions SET updated=?, cwd=? WHERE id=?",
            (now, self.vfs.current_dir, self.session_id)
        )
        conn.commit()
        conn.close()
    
    def save_session(self):
        pass  # Auto-save activé
    
    def load_session(self, session_id: str) -> bool:
        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute("SELECT id FROM sessions WHERE id=?", (session_id,)).fetchone()
        conn.close()
        
        if row:
            self.session_id = session_id
            return True
        return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute("""
            SELECT s.id, s.created, s.updated, s.active, COUNT(c.id) as cmds
            FROM sessions s LEFT JOIN commands c ON s.id = c.session_id
            GROUP BY s.id ORDER BY s.updated DESC
        """).fetchall()
        conn.close()
        
        return [{"id": r[0], "created": r[1], "updated": r[2], "active": bool(r[3]), "commands_count": r[4]} for r in rows]
    
    def delete_session(self, session_id: str):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("DELETE FROM commands WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
        conn.commit()
        conn.close()
    
    def stats(self) -> Dict[str, Any]:
        conn = sqlite3.connect(str(self.db_path))
        total = conn.execute("SELECT COUNT(*) FROM commands").fetchone()[0]
        successful = conn.execute("SELECT COUNT(*) FROM commands WHERE exit_code=0").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM sessions WHERE active=1").fetchone()[0]
        conn.close()
        
        return {
            "session_id": self.session_id,
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "total_commands": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": round(successful / total * 100, 1) if total else 0,
            "active_sessions": active
        }
    
    def reset_all(self):
        self.db_path.unlink(missing_ok=True)
        self._init_db()
