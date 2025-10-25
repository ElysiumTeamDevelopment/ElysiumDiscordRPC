# Discord RPC Settings Screen for RenPy
# Provides user interface for Discord RPC configuration

# Default preferences
default persistent.discord_rpc_enabled = True
default persistent.discord_rpc_client_id = "1234567890123456789"
default persistent.discord_rpc_sync_startup = True

# Settings screen for Discord RPC
screen discord_rpc_settings():
    """Discord RPC settings screen"""
    
    modal True
    zorder 200
    
    style_prefix "confirm"
    
    add "#000000aa"
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 600
        ysize 400
        
        vbox:
            spacing 20
            xfill True
            
            label "Настройки Discord RPC" xalign 0.5
            
            hbox:
                spacing 10
                text "Discord RPC:"
                textbutton "Включен" action SetVariable("persistent.discord_rpc_enabled", True) selected persistent.discord_rpc_enabled
                textbutton "Отключен" action SetVariable("persistent.discord_rpc_enabled", False) selected not persistent.discord_rpc_enabled
            
            if persistent.discord_rpc_enabled:
                vbox:
                    spacing 10
                    
                    $ status_info = discord_rpc.get_status_info()
                    text "Статус подключения: {color=[status_info['color']]}[status_info['status']]{/color}"

                    if status_info['last_error']:
                        text "Последняя ошибка: [status_info['last_error']]" size 12
                    
                    hbox:
                        spacing 10
                        textbutton "Подключить" action Function(discord_rpc.enable) sensitive not discord_rpc.connected
                        textbutton "Отключить" action Function(discord_rpc.disable) sensitive discord_rpc.connected
                        textbutton "Переподключить" action Function(discord_rpc_reconnect)
                    
                    text "Client ID приложения Discord:"
                    input:
                        value VariableInputValue("persistent.discord_rpc_client_id")
                        length 20
                        allow "0123456789"
                        xsize 300
                    
                    text "Для получения Client ID создайте приложение на https://discord.com/developers/applications" size 14

                    null height 10

                    hbox:
                        spacing 10
                        text "Синхронизация при запуске:"
                        textbutton "Включена" action SetVariable("persistent.discord_rpc_sync_startup", True) selected persistent.discord_rpc_sync_startup
                        textbutton "Отключена" action SetVariable("persistent.discord_rpc_sync_startup", False) selected not persistent.discord_rpc_sync_startup

                    text "Включение замедляет запуск игры, но гарантирует подключение к Discord" size 12
            
            hbox:
                spacing 20
                xalign 0.5
                
                textbutton "Применить" action [
                    Function(apply_discord_rpc_settings),
                    Return()
                ]
                textbutton "Отмена" action Return()

# Functions for settings management
init python:
    def apply_discord_rpc_settings():
        """Apply Discord RPC settings"""
        # Update client ID if changed
        if discord_rpc.client_id != persistent.discord_rpc_client_id:
            discord_rpc.client_id = persistent.discord_rpc_client_id
            # Reconnect if currently connected
            if discord_rpc.connected:
                discord_rpc.disconnect()
                if persistent.discord_rpc_enabled:
                    discord_rpc.enable()

        # Update startup sync setting
        discord_rpc.startup_sync_enabled = persistent.discord_rpc_sync_startup

        # Enable/disable based on preference
        if persistent.discord_rpc_enabled and not discord_rpc.enabled:
            discord_rpc.enable()
        elif not persistent.discord_rpc_enabled and discord_rpc.enabled:
            discord_rpc.disable()
    
    def discord_rpc_reconnect():
        """Reconnect Discord RPC"""
        discord_rpc.disconnect()
        if persistent.discord_rpc_enabled:
            discord_rpc.enable()
    
    def get_discord_rpc_status_text():
        """Get formatted Discord RPC status text"""
        if not discord_rpc:
            return "Не инициализирован"
        return discord_rpc.get_status()

# Note: To add Discord RPC to your preferences screen, use:
# textbutton "Discord RPC" action ShowMenu("discord_rpc_settings")

# Quick toggle functions for use in game
init python:
    def toggle_discord_rpc():
        """Quick toggle Discord RPC on/off"""
        if persistent.discord_rpc_enabled:
            persistent.discord_rpc_enabled = False
            discord_rpc.disable()
            renpy.notify("Discord RPC отключен")
        else:
            persistent.discord_rpc_enabled = True
            discord_rpc.enable()
            renpy.notify("Discord RPC включен")
    
    def update_discord_rpc_game_state(state_text, details_text=None):
        """
        Quick function to update Discord RPC from game script
        
        Args:
            state_text (str): Current state text
            details_text (str): Optional details text
        """
        if discord_rpc.enabled and discord_rpc.connected:
            update_data = {
                'state': state_text,
                'details': details_text or (config.name or 'RenPy Game')
            }
            discord_rpc.update_presence(**update_data)

# Automatic status updates based on game events
# Note: Automatic label tracking is disabled by default to avoid conflicts
# To enable, uncomment the code below and test thoroughly with your game

# init python:
#     original_call_in_new_context = renpy.call_in_new_context
#     original_jump = renpy.jump
#     
#     def wrapped_call_in_new_context(label, *args, **kwargs):
#         """Wrapped call function to track label changes"""
#         result = original_call_in_new_context(label, *args, **kwargs)
#         
#         # Update Discord RPC with current label
#         if discord_rpc.enabled and discord_rpc.connected:
#             discord_rpc_on_label_start(label)
#             
#         return result
#     
#     def wrapped_jump(label, *args, **kwargs):
#         """Wrapped jump function to track label changes"""
#         # Update Discord RPC before jumping
#         if discord_rpc.enabled and discord_rpc.connected:
#             discord_rpc_on_label_start(label)
#             
#         return original_jump(label, *args, **kwargs)
#     
#     # Replace functions
#     renpy.call_in_new_context = wrapped_call_in_new_context
#     renpy.jump = wrapped_jump

# Screen action for opening Discord RPC settings
init python:
    class ShowDiscordRPCSettings(Action):
        """Action to show Discord RPC settings screen"""
        
        def __call__(self):
            renpy.call_screen("discord_rpc_settings")
        
        def get_selected(self):
            return False
