# Discord RPC API for RenPy Game Scripts
# Provides easy-to-use functions for updating Discord Rich Presence during gameplay

init python:
    class DiscordRPCAPI:
        """
        High-level API for Discord RPC integration in RenPy games
        Provides simple functions for common use cases
        """
        
        @staticmethod
        def set_main_menu():
            """Set Discord status to main menu"""
            if discord_rpc.enabled and discord_rpc.connected:
                presence = get_presence_template('main_menu_presence')
                if presence:
                    discord_rpc.update_presence(**presence)
        
        @staticmethod
        def set_in_game(chapter_name=None, character_name=None):
            """
            Set Discord status for in-game state
            
            Args:
                chapter_name (str): Current chapter/scene name
                character_name (str): Current character being talked to
            """
            if not (discord_rpc.enabled and discord_rpc.connected):
                return
                
            state_text = "Играет"
            details_text = config.name or 'RenPy Game'
            
            if chapter_name:
                state_text = f"Глава: {chapter_name}"
            
            if character_name:
                details_text = f"Разговор с {character_name}"
            
            discord_rpc.update_presence(
                state=state_text,
                details=details_text,
                large_image="game_icon",
                large_text=config.name or 'RenPy Game'
            )
        
        @staticmethod
        def set_reading_dialogue(character_name=None, scene_name=None):
            """
            Set Discord status for dialogue reading
            
            Args:
                character_name (str): Character currently speaking
                scene_name (str): Current scene name
            """
            if not (discord_rpc.enabled and discord_rpc.connected):
                return
                
            if character_name and scene_name:
                state_text = f"Сцена: {scene_name}"
                details_text = f"Диалог с {character_name}"
            elif character_name:
                state_text = "Читает диалог"
                details_text = f"Разговор с {character_name}"
            elif scene_name:
                state_text = f"Сцена: {scene_name}"
                details_text = "Читает диалог"
            else:
                state_text = "Читает диалог"
                details_text = config.name or 'RenPy Game'
            
            discord_rpc.update_presence(
                state=state_text,
                details=details_text,
                large_image="game_icon",
                large_text=config.name or 'RenPy Game'
            )
        
        @staticmethod
        def set_in_menu(menu_name="Меню"):
            """
            Set Discord status for menu navigation
            
            Args:
                menu_name (str): Name of the current menu
            """
            if discord_rpc.enabled and discord_rpc.connected:
                discord_rpc.update_presence(
                    state=f"В меню: {menu_name}",
                    details=config.name or 'RenPy Game',
                    large_image="game_icon",
                    large_text=config.name or 'RenPy Game'
                )
        
        @staticmethod
        def set_paused():
            """Set Discord status to paused"""
            if discord_rpc.enabled and discord_rpc.connected:
                presence = get_presence_template('paused_presence')
                if presence:
                    discord_rpc.update_presence(**presence)
        
        @staticmethod
        def set_loading():
            """Set Discord status to loading"""
            if discord_rpc.enabled and discord_rpc.connected:
                discord_rpc.update_presence(
                    state="Загрузка...",
                    details=config.name or 'RenPy Game',
                    large_image="game_icon",
                    large_text=config.name or 'RenPy Game'
                )
        
        @staticmethod
        def set_custom(state_text, details_text=None, **kwargs):
            """
            Set custom Discord status
            
            Args:
                state_text (str): Custom state text
                details_text (str): Custom details text
                **kwargs: Additional Discord RPC parameters
            """
            if not (discord_rpc.enabled and discord_rpc.connected):
                return
                
            update_data = {
                'state': state_text,
                'details': details_text or (config.name or 'RenPy Game'),
                'large_image': kwargs.get('large_image', 'game_icon'),
                'large_text': kwargs.get('large_text', config.name or 'RenPy Game')
            }
            
            # Add any additional parameters
            for key, value in kwargs.items():
                if key not in ['large_image', 'large_text']:
                    update_data[key] = value
            
            discord_rpc.update_presence(**update_data)
        
        @staticmethod
        def set_with_timestamp(state_text, details_text=None, start_time=None):
            """
            Set Discord status with timestamp
            
            Args:
                state_text (str): State text
                details_text (str): Details text
                start_time (int): Start timestamp (Unix time)
            """
            if not (discord_rpc.enabled and discord_rpc.connected):
                return
                
            import time
            
            discord_rpc.update_presence(
                state=state_text,
                details=details_text or (config.name or 'RenPy Game'),
                start=start_time or int(time.time()),
                large_image="game_icon",
                large_text=config.name or 'RenPy Game'
            )
        
        @staticmethod
        def clear():
            """Clear Discord Rich Presence"""
            if discord_rpc.enabled and discord_rpc.connected:
                discord_rpc.clear_presence()

    # Create global API instance
    drpc = DiscordRPCAPI()

# Convenient wrapper functions for use in RenPy scripts
init python:
    def discord_set_main_menu():
        """
        Set Discord status to main menu
        
        Example:
            $ discord_set_main_menu()
        """
        drpc.set_main_menu()
    
    def discord_set_in_game(chapter=None, character=None):
        """
        Set Discord status for in-game state
        
        Args:
            chapter (str): Current chapter/scene name
            character (str): Current character being talked to
            
        Example:
            $ discord_set_in_game("Глава 1", "Эйлин")
        """
        drpc.set_in_game(chapter, character)
    
    def discord_set_dialogue(character=None, scene=None):
        """
        Set Discord status for dialogue reading
        
        Args:
            character (str): Character currently speaking
            scene (str): Current scene name
            
        Example:
            $ discord_set_dialogue("Эйлин", "Комната")
        """
        drpc.set_reading_dialogue(character, scene)
    
    def discord_set_menu(menu_name="Меню"):
        """
        Set Discord status for menu navigation
        
        Args:
            menu_name (str): Name of the current menu
            
        Example:
            $ discord_set_menu("Настройки")
        """
        drpc.set_in_menu(menu_name)
    
    def discord_set_paused():
        """
        Set Discord status to paused
        
        Example:
            $ discord_set_paused()
        """
        drpc.set_paused()
    
    def discord_set_loading():
        """
        Set Discord status to loading
        
        Example:
            $ discord_set_loading()
        """
        drpc.set_loading()
    
    def discord_set_custom(state, details=None, **kwargs):
        """
        Set custom Discord status
        
        Args:
            state (str): Custom state text
            details (str): Custom details text
            **kwargs: Additional Discord RPC parameters
            
        Example:
            $ discord_set_custom("Исследует мир", "Глава 2")
            $ discord_set_custom("В бою", large_image="battle_icon")
        """
        drpc.set_custom(state, details, **kwargs)
    
    def discord_clear():
        """
        Clear Discord Rich Presence
        
        Example:
            $ discord_clear()
        """
        drpc.clear()

# Automatic status tracking based on RenPy events
init python:
    class DiscordRPCAutoTracker:
        """Automatic Discord RPC status tracking"""
        
        def __init__(self):
            self.current_label = None
            self.current_character = None
            self.in_menu = False
            self.game_start_time = None
        
        def on_label_start(self, label_name):
            """Called when a new label starts"""
            self.current_label = label_name
            
            # Auto-update based on label name patterns
            if label_name.startswith("menu_"):
                drpc.set_in_menu(label_name.replace("menu_", "").replace("_", " ").title())
            elif label_name == "start":
                import time
                self.game_start_time = int(time.time())
                drpc.set_with_timestamp("Начало игры", start_time=self.game_start_time)
            elif label_name.startswith("chapter_"):
                chapter_name = label_name.replace("chapter_", "").replace("_", " ").title()
                drpc.set_in_game(chapter_name)
            else:
                drpc.set_in_game(label_name.replace("_", " ").title())
        
        def on_character_speak(self, character_name):
            """Called when a character speaks"""
            self.current_character = character_name
            drpc.set_reading_dialogue(character_name, self.current_label)
        
        def on_menu_enter(self):
            """Called when entering a menu"""
            self.in_menu = True
            drpc.set_in_menu()
        
        def on_menu_exit(self):
            """Called when exiting a menu"""
            self.in_menu = False
            if self.current_label:
                drpc.set_in_game(self.current_label.replace("_", " ").title())

    # Create global auto-tracker instance
    discord_auto_tracker = DiscordRPCAutoTracker()

# RenPy callback integration
# Note: Automatic character tracking is disabled by default to avoid conflicts
# To enable, uncomment the code below and test thoroughly with your game

# init python:
#     original_say = renpy.say
#
#     def wrapped_say(who, what, *args, **kwargs):
#         """Wrapped say function to track character dialogue"""
#         # Update Discord RPC if character is speaking
#         if who and hasattr(who, 'name'):
#             discord_auto_tracker.on_character_speak(who.name)
#         elif who:
#             discord_auto_tracker.on_character_speak(str(who))
#
#         return original_say(who, what, *args, **kwargs)
#
#     # Replace the say function
#     renpy.say = wrapped_say
