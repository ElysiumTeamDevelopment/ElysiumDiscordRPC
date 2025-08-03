# ElysiumDiscordRPC Configuration

Detailed guide for configuring the `discord_rpc_config.rpy` file - the central location for all module settings.

## 📋 Configuration Overview

The `discord_rpc_config.rpy` file contains all Discord RPC module settings, divided into logical sections:

- 🔧 **Required Settings** - Application ID and game name
- 🖼️ **Image Assets** - large and small images
- 📱 **Status Templates** - ready-made templates for different states
- ⚙️ **Technical Settings** - connection, queues, logging
- 🤖 **Automatic Tracking** - label patterns and characters

## 🔧 Required Settings

### Application ID
```python
define discord_config.application_id = "123456789012345678"
```

**How to get:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application or select existing one
3. Copy the **Application ID** from "General Information" section

**Important:** Without a correct Application ID, the module won't work!

### Game Name
```python
define discord_config.game_name = "My Awesome Game"
```

**Optional:** If not specified, `config.name` from `options.rpy` will be used.

## 🖼️ Image Assets

### Uploading Images to Discord

**Before configuring images:**
1. Go to Discord Developer Portal → your application
2. Open "Rich Presence" → "Art Assets" section
3. Upload images (recommended size: 512x512px)
4. Remember the **names** of uploaded images

### Large Images
```python
define discord_config.large_images = {
    "game_icon": "main_logo",           # Main game icon
    "menu": "menu_background",          # Main menu background
    "gameplay": "gameplay_scene",       # Gameplay
    "chapter1": "forest_background",    # Chapter 1 background
    "chapter2": "city_background",      # Chapter 2 background
    "ending": "ending_scene",           # Ending
}
```

### Small Images
```python
define discord_config.small_images = {
    "playing": "play_button",           # Playing indicator
    "paused": "pause_button",           # Pause indicator
    "menu": "menu_icon",                # Menu indicator
    "reading": "book_icon",             # Reading dialogue
    "choice": "question_mark",          # Choice selection
}
```

**How it works:**
- Key (e.g., `"game_icon"`) is used in code
- Value (e.g., `"main_logo"`) is the image name in Discord

## 📱 Status Templates

### Main Menu
```python
define discord_config.main_menu_presence = {
    "state": "In main menu",
    "details": None,                    # Automatically filled with game_name
    "large_image": "game_icon",
    "large_text": None,                 # Automatically filled with game_name
    "small_image": "menu",
    "small_text": "Main menu"
}
```

### Gameplay
```python
define discord_config.gameplay_presence = {
    "state": "Playing",
    "details": None,                    # Automatically filled with game_name
    "large_image": "gameplay",
    "large_text": None,
    "small_image": "playing",
    "small_text": "In game"
}
```

### Paused
```python
define discord_config.paused_presence = {
    "state": "Paused",
    "details": None,
    "large_image": "gameplay",
    "small_image": "paused",
    "small_text": "Paused"
}
```

### Reading Dialogue
```python
define discord_config.dialogue_presence = {
    "state": "Reading dialogue",
    "details": None,
    "large_image": "gameplay",
    "small_image": "reading",
    "small_text": "Dialogue"
}
```

**Automatic filling:**
- `None` in `details` and `large_text` is automatically replaced with `game_name`
- This allows easy game name changes in one place

## ⚙️ Technical Settings

### Connection
```python
define discord_config.connection = {
    "startup_sync_enabled": True,       # Synchronous connection at startup
    "startup_timeout": 5.0,             # Maximum seconds to wait at startup
    "max_retries": 3,                   # Maximum reconnection attempts
    "retry_delay": 5.0,                 # Seconds between attempts
    "connection_timeout": 30.0,         # Maximum seconds for connection
    "update_timeout": 10.0,             # Maximum seconds for update
    "health_check_interval": 60.0,      # Seconds between health checks
}
```

**Recommendations:**
- `startup_sync_enabled: True` - for stable connection
- `startup_sync_enabled: False` - for instant game startup

### Queues
```python
define discord_config.queue = {
    "max_pending_updates": 10,          # Maximum updates in queue during connection
    "max_reliability_queue": 100,       # Maximum in reliability module queue
}
```

### Logging
```python
define discord_config.logging = {
    "log_connections": True,            # Log connection events
    "log_updates": True,                # Log status updates
    "log_errors": True,                 # Log errors
    "log_status_changes": True,         # Log status changes
    "log_reliability": False,           # Log reliability events (verbose)
}
```

## 🤖 Automatic Tracking

### Basic Settings
```python
define discord_config.auto_tracking = {
    "enabled": True,                    # Enable auto-tracking
    "track_labels": True,               # Track label changes
    "track_characters": True,           # Track character dialogues
    "track_menus": True,                # Track menu navigation
}
```

### Label Patterns
```python
define discord_config.label_patterns = {
    "chapter_": "Chapter {chapter}",      # chapter_1 → "Chapter 1"
    "scene_": "Scene {scene}",          # scene_park → "Scene park"
    "menu_": "Menu {menu}",             # menu_settings → "Menu settings"
    "ending_": "Ending {ending}",     # ending_good → "Ending good"
    "route_": "Route {route}",           # route_alice → "Route alice"
}
```

**How it works:**
1. When jumping to label `chapter_1`, status automatically becomes "Chapter 1"
2. Part after `_` is formatted (underscores replaced with spaces, first letter capitalized)

### Character Names
```python
define discord_config.character_names = {
    "e": "Eileen",                       # Character object 'e' → "Eileen"
    "narrator": "Narrator",           # narrator → "Narrator"
    "alice": "Alice",
    "bob": "Bob",
    "villain": "Antagonist",
}
```

**Usage:**
```python
# In script.rpy:
define alice = Character("Alice")

# In discord_rpc_config.rpy:
define discord_config.character_names = {
    "alice": "Alice"
}

# Result: during alice dialogue automatically shows "Talking to Alice"
```

## 🔘 Discord Buttons

```python
define discord_config.buttons = [
    {
        "label": "Play Game",
        "url": "https://example.com/play"
    },
    {
        "label": "Developer Site",
        "url": "https://example.com"
    }
]
```

**Limitations:**
- Maximum 2 buttons
- Buttons don't work in your own profile (test with other accounts)

## 🎯 Configuration Examples

### Minimal Configuration
```python
# Only the essentials
define discord_config.application_id = "123456789012345678"
define discord_config.game_name = "My VN"
```

### Basic Configuration
```python
define discord_config.application_id = "123456789012345678"
define discord_config.game_name = "Epic Story"

define discord_config.large_images = {
    "game_icon": "main_logo"
}

define discord_config.character_names = {
    "protagonist": "Main Character",
    "love_interest": "Love Interest"
}
```

### Advanced Configuration
```python
define discord_config.application_id = "123456789012345678"
define discord_config.game_name = "Epic Story: Hero's Path"

# Full image set
define discord_config.large_images = {
    "game_icon": "logo_512",
    "chapter1": "forest_bg",
    "chapter2": "city_bg",
    "chapter3": "castle_bg",
    "ending_good": "sunset_bg",
    "ending_bad": "storm_bg"
}

define discord_config.small_images = {
    "playing": "sword_icon",
    "paused": "pause_icon",
    "choice": "crossroads_icon",
    "reading": "scroll_icon"
}

# Detailed patterns
define discord_config.label_patterns = {
    "ch": "Chapter {ch}",
    "scene": "{scene}",
    "route": "Route {route}",
    "battle": "Battle: {battle}",
    "ending": "Ending: {ending}"
}

# All characters
define discord_config.character_names = {
    "hero": "Main Hero",
    "princess": "Princess Elara",
    "wizard": "Wise Gandalf",
    "villain": "Dark Lord",
    "narrator": "Narrator"
}

# Custom buttons
define discord_config.buttons = [
    {
        "label": "Download Game",
        "url": "https://mygame.com/download"
    },
    {
        "label": "Our Discord",
        "url": "https://discord.gg/mygame"
    }
]

# Fine-tuned connection settings
define discord_config.connection = {
    "startup_sync_enabled": True,
    "startup_timeout": 3.0,             # Faster for SSD
    "max_retries": 5,                   # More attempts
    "retry_delay": 3.0,                 # Faster reconnection
}
```

## ✅ Configuration Validation

The module automatically validates configuration at startup:

### Successful Validation
```
✅ Discord RPC Configuration is valid
```

### Configuration Errors
```
Discord RPC Configuration ERRORS:
  ❌ discord_config.application_id must be set to your Discord Application ID

Discord RPC Configuration WARNINGS:
  ⚠️ discord_config.application_id should be a 17-19 digit number
  ⚠️ discord_config.large_images['game_icon'] should be set
```

## 🛠️ Helper Functions

### Getting Settings
```python
# Get config value with fallback
timeout = get_discord_config('connection.startup_timeout', 5.0)
max_retries = get_discord_config('connection.max_retries', 3)
```

### Working with Templates
```python
# Get ready status template
presence = get_presence_template('main_menu_presence')
discord_rpc.update_presence(**presence)
```

### Working with Assets
```python
# Get image asset name
large_img = resolve_image_asset('game_icon', 'large')    # → "main_logo"
small_img = resolve_image_asset('playing', 'small')     # → "sword_icon"
```

### Formatting
```python
# Automatic name formatting
formatted = format_label_name('chapter_1')              # → "Chapter 1"
char_name = get_character_display_name(hero)            # → "Main Hero"
```

## 🔄 Updating Configuration

After changing configuration:

1. **Save file** `discord_rpc_config.rpy`
2. **Restart game** (Shift+R in RenPy)
3. **Check logs** for validation errors
4. **Test** Discord RPC in game

## 💡 Configuration Tips

1. **Start minimal** - only `application_id` and `game_name`
2. **Gradually add** images and features
3. **Test each change** before adding the next
4. **Use meaningful names** for image keys
5. **Document changes** with comments in config
6. **Create backup** of working configuration

## 🔗 Related Sections

- **[API Reference](api-reference.md)** - using settings in code
- **[Examples](examples.md)** - examples with various configurations
- **[Troubleshooting](troubleshooting.md)** - solving configuration problems
