# ElysiumDiscordRPC

**Advanced Discord Rich Presence module for Ren'Py games**

[![License](https://img.shields.io/badge/License-Custom-blue.svg)](#license)
[![RenPy](https://img.shields.io/badge/RenPy-8.1%2B-blue.svg)](https://www.renpy.org/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=flat&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

**English | [Русский](assets/README_ru.md)**

## 🚀 Features

- ✅ **Modular architecture** — use only what you need (3-6 files)
- ✅ **Rich API** — 15+ functions for any scenario
- ✅ **CDS syntax** — clean commands without Python
- ✅ **Centralized configuration** — all settings in one file
- ✅ **Built-in settings UI** — optional ready-made screen
- ✅ **Reliability system** — auto-reconnection and error handling
- ✅ **Detailed documentation** — complete Wiki with examples

## 📦 Quick Installation

### 1. Download
Download the [latest release](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/releases).

### 2. Copy files to your project
```
your_renpy_project/
└── game/
    ├── discord_rpc_ren.py          # Main module (required)
    ├── discord_rpc_api_ren.py      # API functions (required)
    ├── discord_rpc_config.rpy      # Configuration (required)
    ├── discord_rpc_settings.rpy    # Settings UI (optional)
    ├── discord_rpc_reliability_ren.py  # Reliability (optional)
    └── python-packages/
        └── pypresence/             # Discord RPC library
```

### 3. Install pypresence
```bash
pip install pypresence --target game/python-packages
```

### 4. Configure
Edit `discord_rpc_config.rpy`:
```python
define discord_config.application_id = "YOUR_DISCORD_APP_ID"
define discord_config.game_name = "Your Game Name"
```

## 🎮 Quick Start

```renpy
label start:
    # CDS syntax (clean)
    discord custom "Starting adventure" "Prologue"
    
    "Welcome to the game!"
    
    discord dialogue "Alice" "Park"
    alice "Hello! Nice to meet you!"
    
    discord in_game "Chapter 1" "Alice"
    
    menu:
        "What to do?"
        "Continue":
            discord custom "Continuing story" "Chapter 1"
            jump chapter1
```

Or use Python functions:
```python
$ discord_set_custom("Starting adventure", "Prologue")
$ discord_set_dialogue("Alice", "Park")
$ discord_set_in_game("Chapter 1", "Alice")
```

## 📁 Module Structure

| File | Purpose | Required |
|------|---------|----------|
| `discord_rpc_ren.py` | Main module | ✅ Yes |
| `discord_rpc_api_ren.py` | API functions | ✅ Yes |
| `discord_rpc_config.rpy` | Configuration | ✅ Yes |
| `discord_rpc_settings.rpy` | Settings UI | ❌ Optional |
| `discord_rpc_reliability_ren.py` | Reliability | ❌ Optional |
| `libs/01-discord-rpc_ren.py` | CDS commands | ❌ Optional |

## 📚 Documentation

**Full documentation available in the [Wiki](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki)**

- [Quick Start](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/Quick-Start)
- [Installation](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/Installation)
- [Basic Configuration](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/Basic-Configuration)
- [API Functions](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/API-Functions)
- [CDS Commands](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/CDS-Commands)
- [Common Errors](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/Common-Errors)
- [FAQ](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki/FAQ)

## ⚙️ Requirements

- **Ren'Py:** 8.1+
- **Python:** 3.9+
- **Discord:** Installed and running
- **OS:** Windows, macOS, Linux

## 📄 License

**Free to use, but credit is required.**

When using this module in your project, you must include the following attribution in your game's credits, README, or about section:

> **Uses Elysium Discord RPC by Elysium Development**

## 🆘 Support

- **Wiki:** [Documentation](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/wiki)
- **Issues:** [GitHub Issues](https://github.com/ElysiumTeamDevelopment/ElysiumDiscordRPC/issues)

## 🙏 Acknowledgments

- [pypresence](https://github.com/qwertyquerty/pypresence) — Discord RPC library
- [Lezalith](https://github.com/Lezalith/RenPy_Discord_Presence) — inspiration
- Ren'Py community for support and testing
