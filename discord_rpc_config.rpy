# Discord RPC Configuration File
# All Discord RPC settings and constants in one place

# Initialize before other Discord RPC modules
init offset = -970

# =============================================================================
# REQUIRED SETTINGS - Must be configured for your game
# =============================================================================

# Discord Application ID (Client ID)
# Get this from https://discord.com/developers/applications
# Create a new application and copy the Application ID
define discord_config.application_id = "1234567890123456789"

# Game name displayed in Discord
# If not set, will use config.name from options.rpy
define discord_config.game_name = None

# =============================================================================
# DISCORD RICH PRESENCE ASSETS
# =============================================================================

# Large image assets (upload these to Discord Developer Portal)
define discord_config.large_images = {
    "game_icon": "main_icon",           # Main game icon
    "menu": "menu_background",          # Main menu background
    "gameplay": "gameplay_icon",        # In-game icon
    "chapter1": "chapter1_bg",          # Chapter 1 background
    "chapter2": "chapter2_bg",          # Chapter 2 background
    "ending": "ending_scene",           # Ending scene
}

# Small image assets
define discord_config.small_images = {
    "playing": "play_button",           # Playing indicator
    "paused": "pause_button",           # Paused indicator
    "menu": "menu_icon",                # Menu indicator
    "reading": "book_icon",             # Reading dialogue
    "choice": "choice_icon",            # Making choice
}

# =============================================================================
# DEFAULT PRESENCE STATES
# =============================================================================

# Main menu presence
define discord_config.main_menu_presence = {
    "state": "В главном меню",
    "details": None,  # Will use game_name
    "large_image": "game_icon",
    "large_text": None,  # Will use game_name
    "small_image": "menu",
    "small_text": "Главное меню"
}

# In-game default presence
define discord_config.gameplay_presence = {
    "state": "Играет",
    "details": None,  # Will use game_name
    "large_image": "gameplay",
    "large_text": None,  # Will use game_name
    "small_image": "playing",
    "small_text": "В игре"
}

# Paused presence
define discord_config.paused_presence = {
    "state": "На паузе",
    "details": None,  # Will use game_name
    "large_image": "gameplay",
    "large_text": None,  # Will use game_name
    "small_image": "paused",
    "small_text": "Пауза"
}

# Reading dialogue presence
define discord_config.dialogue_presence = {
    "state": "Читает диалог",
    "details": None,  # Will use game_name
    "large_image": "gameplay",
    "large_text": None,  # Will use game_name
    "small_image": "reading",
    "small_text": "Диалог"
}

# =============================================================================
# TECHNICAL SETTINGS
# =============================================================================

# Connection settings
define discord_config.connection = {
    "startup_sync_enabled": True,       # Enable sync connection on startup
    "startup_timeout": 5.0,             # Max seconds to wait for startup connection
    "max_retries": 3,                   # Max reconnection attempts
    "retry_delay": 5.0,                 # Seconds between retry attempts
    "connection_timeout": 30.0,         # Max seconds for connection attempt
    "update_timeout": 10.0,             # Max seconds for presence update
    "health_check_interval": 60.0,      # Seconds between health checks
}

# Queue settings
define discord_config.queue = {
    "max_pending_updates": 10,          # Max queued updates during connection
    "max_reliability_queue": 100,       # Max queued updates in reliability manager
}

# Logging settings
define discord_config.logging = {
    "log_connections": True,            # Log connection events
    "log_updates": True,                # Log presence updates
    "log_errors": True,                 # Log errors
    "log_status_changes": True,         # Log status changes
    "log_reliability": False,           # Log reliability events (verbose)
}

# =============================================================================
# AUTOMATIC TRACKING SETTINGS
# =============================================================================

# Label-based automatic tracking
define discord_config.auto_tracking = {
    "enabled": True,                    # Enable automatic tracking
    "track_labels": True,               # Track label changes
    "track_characters": True,           # Track character dialogue
    "track_menus": True,                # Track menu navigation
}

# Label patterns for automatic status updates
define discord_config.label_patterns = {
    "chapter_": "Глава {chapter}",      # chapter_1 -> "Глава 1"
    "scene_": "Сцена {scene}",          # scene_park -> "Сцена park"
    "menu_": "Меню {menu}",             # menu_settings -> "Меню settings"
    "ending_": "Концовка {ending}",     # ending_good -> "Концовка good"
}

# Character name mappings for better display
define discord_config.character_names = {
    "e": "Эйлин",                       # Character object 'e' -> "Эйлин"
    "narrator": "Рассказчик",           # narrator -> "Рассказчик"
    # Add your characters here:
    # "alice": "Алиса",
    # "bob": "Боб",
}

# =============================================================================
# BUTTONS CONFIGURATION
# =============================================================================

# Discord Rich Presence buttons (max 2)
define discord_config.buttons = [
    {
        "label": "Играть в игру",
        "url": "https://example.com/play"
    },
    {
        "label": "Сайт разработчика", 
        "url": "https://example.com"
    }
]

# =============================================================================
# PARTY/MULTIPLAYER SETTINGS (for visual novels can be creative)
# =============================================================================

# Party settings (can represent progress, chapters, etc.)
define discord_config.party = {
    "enabled": False,                   # Enable party display
    "show_progress": False,             # Show progress as party (1/10 chapters)
    "party_id": None,                   # Custom party ID
}

# =============================================================================
# ADVANCED SETTINGS
# =============================================================================

# Timestamp settings
define discord_config.timestamps = {
    "show_start_time": True,            # Show time since game start
    "show_session_time": False,         # Show time since current session
    "show_chapter_time": False,         # Show time since chapter start
}

# Fallback settings
define discord_config.fallbacks = {
    "default_state": "Играет в игру",
    "default_details": "Visual Novel",
    "default_large_image": "game_icon",
    "default_small_image": "playing",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

init python:
    def get_discord_config(key, default=None):
        """
        Get Discord RPC configuration value
        
        Args:
            key (str): Configuration key (e.g., 'connection.startup_timeout')
            default: Default value if key not found
        """
        try:
            keys = key.split('.')
            value = discord_config
            
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                else:
                    return default
                    
            return value
        except:
            return default
    
    def get_game_name():
        """Get configured game name or fallback to config.name"""
        return discord_config.game_name or config.name or "RenPy Game"
    
    def get_presence_template(template_name):
        """
        Get presence template with game name filled in
        
        Args:
            template_name (str): Template name (e.g., 'main_menu_presence')
        """
        try:
            template = getattr(discord_config, template_name, {})
            result = template.copy()
            
            # Fill in game name where needed
            game_name = get_game_name()
            if result.get('details') is None:
                result['details'] = game_name
            if result.get('large_text') is None:
                result['large_text'] = game_name
                
            return result
        except:
            return {}
    
    def resolve_image_asset(image_key, image_type="large"):
        """
        Resolve image asset key to actual asset name
        
        Args:
            image_key (str): Image key from config
            image_type (str): 'large' or 'small'
        """
        try:
            if image_type == "large":
                return discord_config.large_images.get(image_key, image_key)
            else:
                return discord_config.small_images.get(image_key, image_key)
        except:
            return image_key
    
    def format_label_name(label_name):
        """
        Format label name using configured patterns
        
        Args:
            label_name (str): Raw label name
        """
        try:
            for pattern, format_str in discord_config.label_patterns.items():
                if label_name.startswith(pattern):
                    # Extract the part after pattern
                    suffix = label_name[len(pattern):]
                    # Format with proper capitalization
                    formatted_suffix = suffix.replace('_', ' ').title()
                    return format_str.format(**{pattern.rstrip('_'): formatted_suffix})
            
            # Default formatting
            return label_name.replace('_', ' ').title()
        except:
            return label_name
    
    def get_character_display_name(character_obj):
        """
        Get display name for character
        
        Args:
            character_obj: Character object or string
        """
        try:
            if hasattr(character_obj, 'name'):
                char_key = character_obj.name
            else:
                char_key = str(character_obj)
            
            return discord_config.character_names.get(char_key, char_key)
        except:
            return str(character_obj)

# =============================================================================
# VALIDATION
# =============================================================================

init python:
    def validate_discord_config():
        """Validate Discord RPC configuration"""
        errors = []
        warnings = []
        
        # Check required settings
        if not discord_config.application_id or discord_config.application_id == "1234567890123456789":
            errors.append("discord_config.application_id must be set to your Discord Application ID")
        
        # Check application ID format
        if not discord_config.application_id.isdigit() or len(discord_config.application_id) < 17:
            warnings.append("discord_config.application_id should be a 17-19 digit number")
        
        # Check image assets
        if not discord_config.large_images.get("game_icon"):
            warnings.append("discord_config.large_images['game_icon'] should be set")
        
        # Print results
        if errors:
            print("Discord RPC Configuration ERRORS:")
            for error in errors:
                print(f"  ❌ {error}")
        
        if warnings:
            print("Discord RPC Configuration WARNINGS:")
            for warning in warnings:
                print(f"  ⚠️ {warning}")
        
        if not errors and not warnings:
            print("✅ Discord RPC Configuration is valid")
        
        return len(errors) == 0
    
    # Auto-validate on startup
    validate_discord_config()
