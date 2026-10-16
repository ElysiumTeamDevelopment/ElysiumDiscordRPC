# Discord RPC Reliability and Error Handling Module
# Provides error handling, user-friendly diagnostics, and backwards-compatible proxies

# IDE hints (not executed by Ren'Py)
from typing import Optional, Any, Dict

discord_rpc: Any = None
reliable_discord_rpc: Any = None
config: Any = None
DiscordRPCStatus: Any = None
get_discord_config: Any = None

"""renpy
init python:
"""

from typing import Optional, Any, Dict

class DiscordRPCErrorHandler:
    """Translates raw Discord IPC / socket exceptions into user-friendly messages."""

    @staticmethod
    def handle_connection_error(error: Any) -> str:
        """Handle connection-related errors."""
        error_str = str(error).lower()

        if "discord not found" in error_str or "no discord client" in error_str or "could not find discord" in error_str:
            return "Discord не запущен. Запустите Discord и попробуйте снова."
        elif "invalid client id" in error_str:
            return "Неверный Client ID. Проверьте настройки Discord RPC."
        elif "connection refused" in error_str or "connection reset" in error_str:
            return "Discord отклонил соединение. Проверьте настройки Discord."
        elif "timeout" in error_str:
            return "Таймаут подключения к Discord."
        else:
            return f"Ошибка подключения: {error}"

    @staticmethod
    def handle_update_error(error: Any) -> str:
        """Handle update-related errors."""
        error_str = str(error).lower()

        if "invalid payload" in error_str:
            return "Неверные данные для обновления статуса."
        elif "rate limit" in error_str:
            return "Слишком частые обновления. Троттлинг активен."
        elif "connection lost" in error_str or "pipe closed" in error_str:
            return "Соединение с Discord потеряно."
        else:
            return f"Ошибка обновления: {error}"


class DiscordRPCReliabilityManager:
    """
    Lightweight compatibility manager for Discord RPC reliability.
    Core socket resilience and coalesced queueing are handled directly by DiscordRPC worker.
    """

    def __init__(self, discord_rpc_instance: Any):
        self.discord_rpc = discord_rpc_instance
        self.monitoring: bool = False

    def start_monitoring(self) -> None:
        """Compatibility method for starting monitoring."""
        self.monitoring = True

    def stop_monitoring(self) -> None:
        """Compatibility method for stopping monitoring."""
        self.monitoring = False

    def queue_update(self, update_data: Dict[str, Any]) -> None:
        """Queue an update through the main RPC client."""
        if self.discord_rpc:
            self.discord_rpc.update_presence(force=False, **update_data)


class ReliableDiscordRPC:
    """Backwards-compatible wrapper adding error translation around DiscordRPC."""

    def __init__(self, discord_rpc_instance: Any):
        self.discord_rpc = discord_rpc_instance
        self.reliability_manager = DiscordRPCReliabilityManager(discord_rpc_instance)
        self.error_handler = DiscordRPCErrorHandler()

    def safe_update(self, **kwargs) -> bool:
        """Safely update Discord RPC presence with error handling."""
        if not self.discord_rpc or not self.discord_rpc.enabled:
            return False
        try:
            return self.discord_rpc.update_presence(force=False, **kwargs)
        except Exception as e:
            error_msg = self.error_handler.handle_update_error(e)
            print(f"Discord RPC safe update failed: {error_msg}")
            return False

    def safe_connect(self) -> bool:
        """Safely initiate connection with error handling."""
        if not self.discord_rpc:
            return False
        try:
            return self.discord_rpc.connect(sync_startup=False)
        except Exception as e:
            error_msg = self.error_handler.handle_connection_error(e)
            print(f"Discord RPC safe connect failed: {error_msg}")
            self.discord_rpc._set_status(DiscordRPCStatus.ERROR, error_msg)
            return False

    def cleanup(self) -> None:
        """Cleanup reliability wrapper."""
        self.reliability_manager.stop_monitoring()


reliable_discord_rpc = None

def init_reliable_discord_rpc():
    """Initialize reliable Discord RPC wrapper."""
    global reliable_discord_rpc
    try:
        if 'discord_rpc' in globals() and discord_rpc and not reliable_discord_rpc:
            reliable_discord_rpc = ReliableDiscordRPC(discord_rpc)
    except NameError:
        pass

init_reliable_discord_rpc()

"""renpy
init python:
"""

def discord_safe_update(**kwargs):
    """Safely update Discord RPC status."""
    if reliable_discord_rpc:
        return reliable_discord_rpc.safe_update(**kwargs)
    elif discord_rpc:
        return discord_rpc.update_presence(force=False, **kwargs)
    return False

def discord_safe_connect():
    """Safely connect to Discord RPC."""
    if reliable_discord_rpc:
        return reliable_discord_rpc.safe_connect()
    elif discord_rpc:
        return discord_rpc.connect(sync_startup=False)
    return False

def get_discord_error_info():
    """Get last Discord RPC error information."""
    if discord_rpc:
        return {
            'last_error': discord_rpc.last_error,
            'retry_count': discord_rpc.retry_count,
            'max_retries': discord_rpc.max_retries
        }
    return None

"""renpy
init python:
"""

def cleanup_reliable_discord_rpc():
    """Cleanup hook for reliability module."""
    if reliable_discord_rpc:
        reliable_discord_rpc.cleanup()

if hasattr(config, 'quit_callbacks') and config.quit_callbacks is not None:
    config.quit_callbacks.append(cleanup_reliable_discord_rpc)
