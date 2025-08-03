# ElysiumDiscordRPC

**Advanced Discord Rich Presence module for RenPy games**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![RenPy](https://img.shields.io/badge/RenPy-8.0%2B-blue.svg)](https://www.renpy.org/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![pypresence](https://img.shields.io/badge/using-pypresence-00bb88.svg?style=flat&logo=discord&logoWidth=20)](https://github.com/qwertyquerty/pypresence)

**English | [Русский](assets/README_ru.md)**

## 🚀 Features

- ✅ **Smart synchronization** - fast startup + reliable connection
- ✅ **Modular architecture** - use only needed components
- ✅ **Centralized configuration** - all settings in one file
- ✅ **Rich API** - 15+ functions for any scenarios
- ✅ **Automatic tracking** - labels, characters, menus
- ✅ **Reliability system** - reconnection and error handling
- ✅ **Flexible settings** - built-in UI or custom integration
- ✅ **Detailed documentation** - examples and guides

## 📦 Quick Installation

### 1. Download the module
```bash
git clone https://github.com/username/ElysiumDiscordRPC.git
```

### 2. Copy files to your RenPy project

**Minimal installation (Core):**
```
your_renpy_project/
├── game/
│   ├── discord_rpc_config.rpy      # Configuration
│   ├── discord_rpc.rpy             # Main module
│   ├── discord_rpc_api.rpy         # API functions
│   └── python-packages/
│       └── pypresence/             # Discord RPC library
```

**Full installation:**
```
your_renpy_project/
├── game/
│   ├── discord_rpc_config.rpy      # Configuration
│   ├── discord_rpc.rpy             # Main module
│   ├── discord_rpc_api.rpy         # API functions
│   ├── discord_rpc_settings.rpy    # Built-in UI (optional)
│   ├── discord_rpc_reliability.rpy # Additional reliability (optional)
│   └── python-packages/
│       └── pypresence/             # Discord RPC library
```

### 3. Install pypresence
```bash
# In your project directory
uv pip install pypresence --target game/python-packages
```

### 4. Configure settings

Edit `discord_rpc_config.rpy`:
```python
# Required: your Discord Application ID
define discord_config.application_id = "YOUR_DISCORD_APP_ID"

# Recommended: game name
define discord_config.game_name = "My Awesome Game"
```

**Get Application ID:**
1. Go to https://discord.com/developers/applications
2. Create a new application
3. Copy the Application ID

## 🎮 Quick Start

### Basic usage in RenPy scripts:

```python
label start:
    # Set game start status
    $ discord_set_custom("Adventure begins", "Prologue")

    "Welcome to the game!"

    # Character dialogue status
    $ discord_set_dialogue("Eileen", "Room")

    e "Hello! How are you?"

    # Gameplay status
    $ discord_set_in_game("Chapter 1", "Eileen")

    menu:
        "What to do?"

        "Continue":
            $ discord_set_custom("Continuing story", "Chapter 1")
            jump chapter1

        "Settings":
            $ discord_set_menu("Settings")
            jump settings
```

### Connection management:

```python
# Enable Discord RPC
$ discord_rpc.enable()

# Disable Discord RPC
$ discord_rpc.disable()

# Reconnect
$ discord_rpc.disconnect()
$ discord_rpc.connect()

# Check status
$ status = discord_rpc.get_status()
```

## 📁 Module Structure

| File | Purpose | Required |
|------|---------|----------|
| `discord_rpc_config.rpy` | Central configuration | ✅ **Required** |
| `discord_rpc.rpy` | Main module logic | ✅ **Required** |
| `discord_rpc_api.rpy` | API functions for developers | ✅ **Required** |
| `discord_rpc_settings.rpy` | Built-in settings UI | ⚪ Optional |
| `discord_rpc_reliability.rpy` | Additional reliability | ⚪ Optional |
| `discord_rpc_test.rpy` | Testing and debugging | ⚪ Development only |

## 🎯 Usage Options

### Core Package (minimal)
For developers with custom interface:
- `discord_rpc_config.rpy`
- `discord_rpc.rpy`
- `discord_rpc_api.rpy`

### Full Package (all features)
For ready-made "out of the box" solution:
- Core Package +
- `discord_rpc_settings.rpy` (ready UI)
- `discord_rpc_reliability.rpy` (enterprise-grade reliability)

## 📚 Documentation

- **[Installation](docs/en/installation.md)** - detailed installation guide
- **[Configuration](docs/en/configuration.md)** - configuring `discord_rpc_config.rpy`
- **[API Reference](docs/en/api-reference.md)** - reference for all functions
- **[UI Integration](docs/en/ui-integration.md)** - user interface integration
- **[Examples](docs/en/examples.md)** - ready-to-use code examples
- **[Troubleshooting](docs/en/troubleshooting.md)** - problem solving

## ⚙️ Requirements

- **RenPy:** 8.0+
- **Python:** 3.9+
- **Discord:** Installed Discord client
- **Internet:** For initial Discord App setup

## 🔧 Features

### Smart Synchronization
- **Default:** Startup connection with 5-second timeout
- **On issues:** Automatic switch to asynchronous mode
- **Configurable:** Can be disabled for instant startup

### Modular Architecture
- **Minimum:** 3 files for basic functionality
- **Maximum:** 6 files for all features
- **Flexibility:** Use only needed components

### Centralized Configuration
- **One file:** All settings in `discord_rpc_config.rpy`
- **Validation:** Automatic correctness checking
- **Templates:** Ready-made status templates

## 🤝 Comparison with Alternatives

| Feature | ElysiumDiscordRPC | Lezalith/RenPy-Discord-Presence |
|---------|-------------------|--------------------------------|
| **Code size** | Modular (3-6 files) | Monolithic (2 files) |
| **API functions** | 15+ functions | 4 functions |
| **Configuration** | Centralized | Built-in |
| **Settings UI** | Optional | None |
| **Reliability** | Advanced | Basic |
| **Rollback support** | Basic | Excellent |
| **Documentation** | Detailed | Good |

## 📄 License

MIT License - use freely in commercial and non-commercial projects.

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/username/ElysiumDiscordRPC/issues)
- **Documentation:** [docs/en/](docs/en/)
- **Examples:** [docs/en/examples.md](docs/en/examples.md)

## 🙏 Acknowledgments

- [pypresence](https://github.com/qwertyquerty/pypresence) - Discord RPC library
- [Lezalith](https://github.com/Lezalith/RenPy_Discord_Presence) - inspiration and reference
- RenPy community for support and testing
