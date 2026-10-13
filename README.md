# Nexus-Mental-Terminal-v2.0.0
In-memory virtual terminal for AI agents. Simulates full Ubuntu: bash (100+ commands), Python REPL, apt, snap, flatpak, systemd, kernel PPAs. FHS filesystem, pipelines, redirections. Zero real system access. Safe sandbox for LLMs and testing.
# 🧠 Nexus Mental Terminal v2.0.0

> Terminal virtuel en mémoire pour agents IA — Ubuntu/Unix Edition

[![Version](https://img.shields.io/badge/version-2.0.0-purple)](https://github.com/Aissamohammedi88/nexus-mental-terminal)
[![License](https://img.shields.io/badge/license-NEXUS--OPEN--2.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Ubuntu](https://img.shields.io/badge/ubuntu-24.04-orange)](https://ubuntu.com/)

---

## Qu'est-ce que c'est ?

**Nexus Mental Terminal** est un terminal **100% virtuel** qui simule un environnement Ubuntu/Unix complet :

- 🐚 **Shell bash** avec 100+ commandes (ls, cd, cat, grep, find, sed, awk, ...)
- 🐍 **REPL Python** persistant
- 📦 **apt** — gestionnaire de paquets Ubuntu simulé
- 📸 **snap** — paquets snap
- 📦 **flatpak** — applications flatpak
- ⚙️ **systemd** — systemctl, journalctl, service
- 🧬 **PPAs Ubuntu** — noyaux, drivers, toolchains
- 📁 **Filesystem Hierarchy Standard** complet (/, /home, /etc, /usr, /var, /proc, /sys...)
- 🔧 **syscalls UNIX** — uname, getpid, getuid, getgid

**AUCUN accès au système réel.** Tout se passe en RAM.

---

## Pourquoi ?

Les agents IA (LLM) ont besoin d'un environnement pour :

1. **Tester des commandes** sans risque
2. **Simuler des installations** sans casser la machine
3. **Apprendre Unix/Linux** sans sudo
4. **Prototyper des workflows** Ubuntu
5. **Sandboxer des exécutions** de code

Nexus Mental Terminal fournit cette sandbox.

---

## Installation

```bash
git clone https://github.com/Aissamohammedi88/nexus-mental-terminal.git
cd nexus-mental-terminal
python3 -m nexus_mental
