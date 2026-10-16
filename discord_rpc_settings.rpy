# Discord RPC Settings Screen for RenPy
# Provides user interface for Discord RPC configuration

# Default preferences
default persistent.discord_rpc_enabled = True
default persistent.discord_rpc_client_id = "1234567890123456789"
default persistent.discord_rpc_sync_startup = False
default persistent.discord_rpc_show_advanced = False

# Settings screen for Discord RPC
screen discord_rpc_settings():
    """Discord RPC settings modal screen."""

    modal True
    zorder 200

    style_prefix "confirm"

    add "#000000aa"

    frame:
        xalign 0.5
        yalign 0.5
        xsize 680
        ymaximum 620

        vbox:
            spacing 12
            xfill True

            label _("Настройки Discord RPC") xalign 0.5

            viewport:
                scrollbars "vertical"
                mousewheel True
                ymaximum 480

                vbox:
                    spacing 16
                    xfill True
                    xsize 630

                    hbox:
                        spacing 15
                        text _("Discord RPC:") yalign 0.5
                        textbutton _("Включен") action SetVariable("persistent.discord_rpc_enabled", True) selected persistent.discord_rpc_enabled
                        textbutton _("Отключен") action SetVariable("persistent.discord_rpc_enabled", False) selected not persistent.discord_rpc_enabled

                    if persistent.discord_rpc_enabled:
                        vbox:
                            spacing 10

                            $ status_info = discord_rpc.get_status_info()
                            text _("Статус: {color=[status_info['color']]}[status_info['status']]{/color}")

                            if status_info['last_error']:
                                text _("Сообщение: [status_info['last_error']]") size 12 color "#ff8888"

                            hbox:
                                spacing 10
                                textbutton _("Подключить") action Function(set_discord_rpc_connected, True) sensitive (not discord_rpc.connected)
                                textbutton _("Отключить") action Function(set_discord_rpc_connected, False) sensitive discord_rpc.connected
                                textbutton _("Переподключить") action Function(discord_rpc_reconnect)

                            null height 8

                            textbutton _("Дополнительные параметры (Developer)"):
                                action ToggleVariable("persistent.discord_rpc_show_advanced")
                                text_size 14

                            if persistent.discord_rpc_show_advanced:
                                vbox:
                                    spacing 8
                                    xfill True

                                    text _("Client ID приложения Discord:") size 13
                                    input:
                                        value VariableInputValue("persistent.discord_rpc_client_id")
                                        length 20
                                        allow "0123456789"
                                        xsize 400

                                    text _("По умолчанию используется Application ID из discord_config.rpy.") size 11 color "#aaaaaa"

                                    null height 5

                                    text _("Синхронизация при запуске игры:") size 13
                                    hbox:
                                        spacing 10
                                        textbutton _("Включена") action SetVariable("persistent.discord_rpc_sync_startup", True) selected persistent.discord_rpc_sync_startup
                                        textbutton _("Отключена") action SetVariable("persistent.discord_rpc_sync_startup", False) selected not persistent.discord_rpc_sync_startup

            null height 5

            hbox:
                spacing 20
                xalign 0.5

                textbutton _("Применить") action [
                    Function(apply_discord_rpc_settings),
                    Hide("discord_rpc_settings")
                ] xsize 150
                textbutton _("Закрыть") action Hide("discord_rpc_settings") xsize 150

# Functions for settings management
init python:
    def get_effective_discord_client_id():
        """Return persistent override only when user entered a real ID."""
        persistent_id = getattr(persistent, 'discord_rpc_client_id', None)
        config_id = getattr(discord_config, 'application_id', None)

        if persistent_id and persistent_id != DISCORD_DEFAULT_CLIENT_ID:
            return persistent_id
        if config_id and config_id != DISCORD_DEFAULT_CLIENT_ID:
            return config_id
        return persistent_id or config_id or DISCORD_DEFAULT_CLIENT_ID

    def apply_discord_rpc_settings():
        """Apply Discord RPC settings."""
        effective_client_id = get_effective_discord_client_id()

        if discord_rpc.client_id != effective_client_id:
            discord_rpc.client_id = effective_client_id
            if discord_rpc.connected:
                discord_rpc.disconnect()
                if persistent.discord_rpc_enabled:
                    discord_rpc.enable()

        discord_rpc.startup_sync_enabled = persistent.discord_rpc_sync_startup

        if persistent.discord_rpc_enabled and not discord_rpc.enabled:
            discord_rpc.enable()
        elif not persistent.discord_rpc_enabled and discord_rpc.enabled:
            discord_rpc.disable()

    def discord_rpc_reconnect():
        """Reconnect Discord RPC."""
        discord_rpc.disconnect()
        if persistent.discord_rpc_enabled:
            discord_rpc.enable()

    def get_discord_rpc_status_text():
        """Get formatted Discord RPC status text."""
        if not discord_rpc:
            return "Не инициализирован"
        return discord_rpc.get_status()
