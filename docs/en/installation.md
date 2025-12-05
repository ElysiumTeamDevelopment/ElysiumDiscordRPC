# ElysiumDiscordRPC Installation

Detailed guide for installing and configuring the Discord Rich Presence module for RenPy.

## 📋 Requirements

### System Requirements
- **RenPy:** 7.4+ (recommended 8.0+)
- **Python:** 3.9+ (built into RenPy 8.0+)
- **Discord:** Installed Discord client
- **Operating System:** Windows, macOS, Linux

### Discord Application Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Enter your game name
4. Copy the **Application ID** (needed for configuration)
5. (Optional) Upload images in "Rich Presence" → "Art Assets" section

## 📦 Installation Options

### Option 1: Core Package (minimal)

**For:** Developers with custom interface

**Files to copy:**
```
ElysiumDiscordRPC/
├── discord_rpc_config.rpy      # Configuration
├── discord_rpc.rpy             # Main module
├── discord_rpc_api.rpy         # API functions
└── python-packages/
    └── pypresence/             # Discord RPC library
```

### Option 2: Full Package (all features)

**For:** Users wanting a ready-made solution

**Files to copy:**
```
ElysiumDiscordRPC/
├── discord_rpc_config.rpy      # Configuration
├── discord_rpc.rpy             # Main module
├── discord_rpc_api.rpy         # API functions
├── discord_rpc_settings.rpy    # Built-in UI
├── discord_rpc_reliability.rpy # Additional reliability
└── python-packages/
    └── pypresence/             # Discord RPC library
```

## 🗂️ File Placement

### Recommended Placement

**In `game/` directory (standard):**
```
your_renpy_project/
├── game/
│   ├── discord_rpc_config.rpy
│   ├── discord_rpc.rpy
│   ├── discord_rpc_api.rpy
│   ├── discord_rpc_settings.rpy    # optional
│   ├── discord_rpc_reliability.rpy # optional
│   ├── python-packages/
│   │   └── pypresence/
│   ├── script.rpy                  # your files
│   ├── options.rpy
│   └── screens.rpy
├── README.md
└── project.json
```

### Alternative Placement Options

**In separate modules directory:**
```
your_renpy_project/
├── game/
│   ├── modules/
│   │   ├── discord_rpc/
│   │   │   ├── discord_rpc_config.rpy
│   │   │   ├── discord_rpc.rpy
│   │   │   └── discord_rpc_api.rpy
│   │   └── python-packages/
│   │       └── pypresence/
│   ├── script.rpy
│   └── options.rpy
```

**In project root (for large projects):**
```
your_renpy_project/
├── discord_rpc/
│   ├── discord_rpc_config.rpy
│   ├── discord_rpc.rpy
│   └── discord_rpc_api.rpy
├── game/
│   ├── python-packages/
│   │   └── pypresence/
│   ├── script.rpy
│   └── options.rpy
```

> **Important:** The `pypresence` library must be in `game/python-packages/` regardless of module placement.

## 🔧 Step-by-Step Installation

### Step 1: Download Module

**Via Git:**
```bash
git clone https://github.com/ElysiumDevelopment/ElysiumDiscordRPC.git
cd ElysiumDiscordRPC
```

**Via GitHub:**
1. Go to the releases page
2. Download `ElysiumDiscordRPC-core.zip` or `ElysiumDiscordRPC-full.zip`
3. Extract the archive

### Step 2: Copy Files

1. Copy the selected module files to your RenPy project
2. Ensure the directory structure matches your chosen option

### Step 3: Install pypresence

**Via uv (recommended):**
```bash
cd your_renpy_project
uv pip install pypresence --target game/python-packages
```

**Via pip:**
```bash
cd your_renpy_project
pip install pypresence --target game/python-packages
```

**Manual installation:**
1. Download pypresence from [PyPI](https://pypi.org/project/pypresence/)
2. Extract to `game/python-packages/pypresence/`

### Step 4: Basic Configuration

Edit `discord_rpc_config.rpy`:

```python
# REQUIRED: Your Discord Application ID
define discord_config.application_id = "123456789012345678"

# RECOMMENDED: Game name
define discord_config.game_name = "My Awesome Game"

# OPTIONAL: Main images
define discord_config.large_images = {
    "game_icon": "main_logo",           # Upload to Discord Developer Portal
    "gameplay": "gameplay_icon",
}
```

### Step 5: Verify Installation

1. Launch your RenPy project
2. Check console for errors
3. You should see: `✅ Discord RPC Configuration is valid`
4. Discord should display your game status

## 🔍 Verify Installation

### File Check
```python
# In RenPy console or in-game:
$ print("Discord RPC available:", 'discord_rpc' in globals())
$ print("Config valid:", hasattr(discord_config, 'application_id'))
$ print("API available:", 'discord_set_custom' in globals())
```

### Connection Check
```python
# In-game:
$ print("Status:", discord_rpc.get_status())
$ print("Connected:", discord_rpc.connected)
$ print("Enabled:", discord_rpc.enabled)
```

### Test Status Update
```python
# In-game:
$ discord_set_custom("Testing", "Installation check")
```

## ⚠️ Common Issues

### "pypresence not available"
**Solution:**
1. Ensure pypresence is installed in `game/python-packages/`
2. Check structure: `game/python-packages/pypresence/__init__.py` should exist
3. Reinstall pypresence

### "Discord RPC Configuration ERRORS"
**Solution:**
1. Check that `discord_config.application_id` is set
2. Ensure Application ID is correct (17-19 digits)
3. Check syntax in `discord_rpc_config.rpy`

### "Discord not found"
**Solution:**
1. Launch Discord client
2. Ensure you're logged into Discord
3. Check that Discord isn't blocked by antivirus

### Game won't start
**Solution:**
1. Check syntax of all .rpy files
2. Ensure all files are copied correctly
3. Check RenPy logs for errors

## 🎯 Next Steps

After successful installation:

1. **[Configure settings](configuration.md)** - detailed module configuration
2. **[Learn the API](api-reference.md)** - available functions
3. **[View examples](examples.md)** - ready-to-use code examples
4. **[UI integration](ui-integration.md)** - adding to game interface

## 📞 Support

If you encounter problems:
1. Check [Troubleshooting](troubleshooting.md)
2. Create an [Issue on GitHub](https://github.com/ElysiumDevelopment/ElysiumDiscordRPC/issues)
3. Include RenPy logs and problem description
