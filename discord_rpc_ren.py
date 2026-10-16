# Discord RPC Module for RenPy
# Provides Discord Rich Presence integration with flexible configuration

# IDE hints (not executed by Ren'Py)
from typing import Optional, Dict, Any, List, Callable
import asyncio
import threading
import time
from queue import Queue, Empty

# Ren'Py store hints
discord_rpc: Any = None
persistent: Any = None
config: Any = None
discord_config: Any = None
get_discord_config: Callable = None
get_presence_template: Callable = None
resolve_image_asset: Callable = None
init_reliable_discord_rpc: Callable = None
PYPRESENCE_AVAILABLE: bool = True

"""renpy
init -1 python:
"""

from typing import Optional, Dict, Any, List, Callable
import threading
import time
import asyncio
from queue import Queue, Empty

try:
    from pypresence import Presence
    PYPRESENCE_AVAILABLE = True
except ImportError:
    PYPRESENCE_AVAILABLE = False
    print("Warning: pypresence not available. Discord RPC will be disabled.")

# Discord RPC Constants
DISCORD_DEFAULT_CLIENT_ID = "1234567890123456789"
DISCORD_QUEUE_MAX_SIZE = 100
DISCORD_THREAD_JOIN_TIMEOUT = 2.0


class DiscordRPCStatus:
    """Enum-like class for Discord RPC connection status."""
    DISABLED = "Отключен"
    CONNECTING = "Подключение"
    CONNECTED = "Подключен"
    ERROR = "Ошибка"
    DISCONNECTED = "Не подключен"
    RECONNECTING = "Переподключение"
    TIMEOUT = "Таймаут"

    @staticmethod
    def get_color(status: str) -> str:
        """Get color hex code for status display."""
        colors = {
            DiscordRPCStatus.DISABLED: "#808080",
            DiscordRPCStatus.CONNECTING: "#ffaa00",
            DiscordRPCStatus.CONNECTED: "#00ff00",
            DiscordRPCStatus.ERROR: "#ff0000",
            DiscordRPCStatus.DISCONNECTED: "#a0a0a0",
            DiscordRPCStatus.RECONNECTING: "#ffaa00",
            DiscordRPCStatus.TIMEOUT: "#ff8800"
        }
        return colors.get(status, "#ffffff")


class DiscordRPC:
    """
    Main Discord RPC client for RenPy integration.
    Uses an asynchronous worker thread (Actor model) to contain all socket I/O
    and asyncio event loop operations, preventing main thread stutters and concurrency bugs.
    """

    def __init__(self, client_id: Optional[str] = None):
        self.client_id: str = client_id or DISCORD_DEFAULT_CLIENT_ID
        self.rpc: Optional[Any] = None
        self.status: str = DiscordRPCStatus.DISABLED
        self.enabled: bool = False
        self.connected: bool = False
        self.last_update: Dict[str, Any] = {}
        self.retry_count: int = 0
        self.last_error: Optional[str] = None

        self._lock = threading.RLock()
        self._cmd_queue: Queue = Queue(maxsize=DISCORD_QUEUE_MAX_SIZE)
        self._worker_thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._connection_event = threading.Event()
        self._shutdown_flag: bool = False

        self.max_retries: int = 3
        self.retry_delay: float = 5.0
        self.startup_sync_enabled: bool = False
        self.startup_timeout: float = 5.0
        self.connection_timeout: float = 30.0
        self.rate_limit_enabled: bool = True
        self.rate_limit_interval: float = 4.0

        self.status_callbacks: List[Callable[[str, str], None]] = []

    def _is_placeholder_client_id(self, client_id: Optional[str]) -> bool:
        """Return True for empty or placeholder client IDs."""
        return not client_id or str(client_id).strip() == DISCORD_DEFAULT_CLIENT_ID

    def _is_valid_client_id(self, client_id: Optional[str]) -> bool:
        """Validate Discord application ID format."""
        if self._is_placeholder_client_id(client_id):
            return False
        cid = str(client_id).strip()
        return cid.isdigit() and 17 <= len(cid) <= 19

    def _load_config(self) -> None:
        """Load configuration from discord_config and persistent state."""
        try:
            persistent_client_id = getattr(persistent, 'discord_rpc_client_id', None)
            config_client_id = getattr(discord_config, 'application_id', None)

            if not self._is_placeholder_client_id(persistent_client_id):
                self.client_id = str(persistent_client_id).strip()
            elif not self._is_placeholder_client_id(config_client_id):
                self.client_id = str(config_client_id).strip()
            else:
                self.client_id = DISCORD_DEFAULT_CLIENT_ID

            if get_discord_config:
                self.max_retries = get_discord_config('connection.max_retries', 3)
                self.retry_delay = get_discord_config('connection.retry_delay', 5.0)
                self.startup_sync_enabled = get_discord_config('connection.startup_sync_enabled', False)
                if hasattr(persistent, 'discord_rpc_sync_startup'):
                    self.startup_sync_enabled = persistent.discord_rpc_sync_startup
                self.startup_timeout = get_discord_config('connection.startup_timeout', 5.0)
                self.connection_timeout = get_discord_config('connection.connection_timeout', 30.0)
                self.rate_limit_enabled = get_discord_config('rate_limiting.enabled', True)
                self.rate_limit_interval = get_discord_config('rate_limiting.min_interval', 4.0)
        except Exception as e:
            print(f"Warning: Failed to load Discord RPC config: {e}")

    def is_enabled(self) -> bool:
        """Check if Discord RPC is enabled in persistent preferences."""
        return getattr(persistent, 'discord_rpc_enabled', True)

    def get_status(self) -> str:
        """Get current connection status."""
        with self._lock:
            return self.status

    def get_status_info(self) -> Dict[str, Any]:
        """Get detailed status dictionary for UI rendering."""
        with self._lock:
            return {
                'status': self.status,
                'enabled': self.enabled,
                'connected': self.connected,
                'retry_count': self.retry_count,
                'last_error': self.last_error,
                'color': DiscordRPCStatus.get_color(self.status)
            }

    def add_status_callback(self, callback: Callable[[str, str], None]) -> None:
        """Add callback for status transitions."""
        with self._lock:
            if callback not in self.status_callbacks:
                self.status_callbacks.append(callback)

    def remove_status_callback(self, callback: Callable[[str, str], None]) -> None:
        """Remove previously registered status callback."""
        with self._lock:
            if callback in self.status_callbacks:
                self.status_callbacks.remove(callback)

    def _notify_status_change(self, old_status: str, new_status: str) -> None:
        """Notify registered status listeners."""
        with self._lock:
            callbacks = list(self.status_callbacks)

        for callback in callbacks:
            try:
                callback(old_status, new_status)
            except Exception as e:
                print(f"Status callback error: {e}")

    def _set_status(self, new_status: str, error: Optional[Any] = None) -> None:
        """Update internal status and fire change callbacks."""
        with self._lock:
            old_status = self.status
            self.status = new_status
            if error is not None:
                self.last_error = str(error)
            elif new_status == DiscordRPCStatus.CONNECTED:
                self.last_error = None

        if old_status != new_status:
            self._notify_status_change(old_status, new_status)

    def _prepare_presence_payload(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve asset keys and sanitize payload boundaries."""
        payload = kwargs.copy()

        try:
            if payload.get('large_image') and resolve_image_asset:
                payload['large_image'] = resolve_image_asset(payload['large_image'], "large")
            if payload.get('small_image') and resolve_image_asset:
                payload['small_image'] = resolve_image_asset(payload['small_image'], "small")
        except Exception as e:
            print(f"Warning: Failed to resolve Discord RPC assets: {e}")

        for text_key in ['state', 'details', 'large_text', 'small_text']:
            if text_key in payload and payload[text_key] is not None:
                payload[text_key] = str(payload[text_key])[:128]

        if 'buttons' in payload and payload['buttons']:
            payload['buttons'] = payload['buttons'][:2]

        return payload

    def _ensure_worker_running(self) -> None:
        """Ensure background worker thread is active."""
        with self._lock:
            if self._worker_thread is None or not self._worker_thread.is_alive():
                self._shutdown_flag = False
                self._worker_thread = threading.Thread(
                    target=self._worker_loop,
                    daemon=True,
                    name="DiscordRPCWorker"
                )
                self._worker_thread.start()

    def _safe_close_rpc(self) -> None:
        """Close live RPC connection safely within worker thread."""
        if self.rpc:
            try:
                self.rpc.close()
            except Exception:
                pass
            self.rpc = None

    def _worker_loop(self) -> None:
        """
        Actor loop running strictly in its own thread with a private asyncio loop.
        Handles connection management, queued commands, and coalesced rate-limiting.
        """
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        last_presence_send_time = 0.0
        pending_throttled_payload: Optional[Dict[str, Any]] = None
        next_retry_time = 0.0

        while not self._shutdown_flag:
            now = time.time()

            # Flush queued throttled presence when rate limit interval has passed
            if pending_throttled_payload is not None and self.connected and self.rpc:
                time_until_send = (last_presence_send_time + self.rate_limit_interval) - now
                if time_until_send <= 0:
                    try:
                        self.rpc.update(**pending_throttled_payload)
                        last_presence_send_time = time.time()
                        pending_throttled_payload = None
                    except Exception as e:
                        self._handle_rpc_error(e)
                        next_retry_time = time.time() + self.retry_delay

            # Handle automatic reconnection if disconnected unexpectedly
            with self._lock:
                should_auto_reconnect = (
                    self.enabled and
                    not self.connected and
                    self.retry_count < self.max_retries and
                    self._is_valid_client_id(self.client_id) and
                    next_retry_time > 0 and
                    now >= next_retry_time
                )

            if should_auto_reconnect:
                self._do_connect()
                if not self.connected:
                    with self._lock:
                        self.retry_count += 1
                        current_retry = self.retry_count

                    if current_retry < self.max_retries:
                        next_retry_time = time.time() + self.retry_delay
                        self._set_status(DiscordRPCStatus.RECONNECTING)
                    else:
                        next_retry_time = 0.0
                        self._set_status(DiscordRPCStatus.ERROR, f"Max retries ({self.max_retries}) exceeded")

            # Determine dynamic poll timeout for responsive command handling
            poll_timeout = 0.25
            if pending_throttled_payload is not None and self.connected:
                time_until_send = (last_presence_send_time + self.rate_limit_interval) - time.time()
                poll_timeout = max(0.02, min(time_until_send, 0.25))

            try:
                cmd, args = self._cmd_queue.get(timeout=poll_timeout)
            except Empty:
                continue

            if cmd == 'STOP':
                self._do_disconnect()
                break
            elif cmd == 'CONNECT':
                next_retry_time = 0.0
                with self._lock:
                    self.retry_count = 0
                self._do_connect()
                if not self.connected:
                    with self._lock:
                        self.retry_count += 1
                        current_retry = self.retry_count
                    if current_retry < self.max_retries:
                        next_retry_time = time.time() + self.retry_delay
                        self._set_status(DiscordRPCStatus.RECONNECTING)
                    else:
                        self._set_status(DiscordRPCStatus.ERROR, f"Connection failed after {self.max_retries} attempts")
                else:
                    # Apply initial or latest requested presence upon connection
                    with self._lock:
                        payload_to_send = self.last_update.copy() if self.last_update else None

                    if not payload_to_send and get_presence_template:
                        payload_to_send = get_presence_template('main_menu_presence')

                    if payload_to_send:
                        prepared = self._prepare_presence_payload(payload_to_send)
                        try:
                            self.rpc.update(**prepared)
                            last_presence_send_time = time.time()
                        except Exception as e:
                            self._handle_rpc_error(e)
            elif cmd == 'DISCONNECT':
                next_retry_time = 0.0
                pending_throttled_payload = None
                self._do_disconnect()
                self._set_status(DiscordRPCStatus.DISCONNECTED)
            elif cmd == 'CLEAR':
                pending_throttled_payload = None
                if self.connected and self.rpc:
                    try:
                        self.rpc.clear()
                    except Exception as e:
                        self._handle_rpc_error(e)
            elif cmd == 'UPDATE':
                payload, force = args
                if not self.connected:
                    with self._lock:
                        self.last_update = payload
                    continue

                prepared = self._prepare_presence_payload(payload)
                elapsed = time.time() - last_presence_send_time

                if force or not self.rate_limit_enabled or elapsed >= self.rate_limit_interval:
                    try:
                        self.rpc.update(**prepared)
                        last_presence_send_time = time.time()
                        pending_throttled_payload = None
                    except Exception as e:
                        self._handle_rpc_error(e)
                        next_retry_time = time.time() + self.retry_delay
                else:
                    # Coalesce into pending throttled payload
                    pending_throttled_payload = prepared

        self._safe_close_rpc()
        if self._loop and not self._loop.is_closed():
            try:
                self._loop.close()
            except Exception:
                pass

    def _do_connect(self) -> None:
        """Internal connect logic executing on worker thread."""
        if not PYPRESENCE_AVAILABLE or not self._is_valid_client_id(self.client_id):
            self._connection_event.set()
            return

        self._set_status(DiscordRPCStatus.CONNECTING)
        self._safe_close_rpc()

        try:
            self.rpc = Presence(self.client_id, loop=self._loop)
            self.rpc.connect()
            with self._lock:
                self.connected = True
                self.retry_count = 0
            self._set_status(DiscordRPCStatus.CONNECTED)
        except Exception as e:
            with self._lock:
                self.connected = False
            self._safe_close_rpc()
            self._set_status(DiscordRPCStatus.ERROR, e)
        finally:
            self._connection_event.set()

    def _do_disconnect(self) -> None:
        """Internal disconnect logic executing on worker thread."""
        with self._lock:
            self.connected = False
        self._safe_close_rpc()

    def _handle_rpc_error(self, error: Exception) -> None:
        """Handle runtime RPC communication failure."""
        with self._lock:
            self.connected = False
        self._safe_close_rpc()
        self._set_status(DiscordRPCStatus.ERROR, error)

    def enable(self, sync_startup: Optional[bool] = None) -> bool:
        """
        Enable Discord RPC and initiate connection.
        Returns True if connection request dispatched successfully.
        """
        if not PYPRESENCE_AVAILABLE:
            self.status = DiscordRPCStatus.ERROR
            return False

        if not self._is_valid_client_id(self.client_id):
            self._set_status(
                DiscordRPCStatus.ERROR,
                "Discord RPC Client ID is not configured. Set discord_config.application_id or persistent.discord_rpc_client_id."
            )
            return False

        self.enabled = True
        persistent.discord_rpc_enabled = True
        return self.connect(sync_startup=sync_startup)

    def disable(self) -> None:
        """Disable Discord RPC and disconnect."""
        self.enabled = False
        persistent.discord_rpc_enabled = False
        self.disconnect()
        self._set_status(DiscordRPCStatus.DISABLED)

    def connect(self, sync_startup: Optional[bool] = None) -> bool:
        """
        Connect to Discord RPC asynchronously or with startup timeout.
        """
        if not self.enabled or not PYPRESENCE_AVAILABLE:
            return False

        if not self._is_valid_client_id(self.client_id):
            self._set_status(
                DiscordRPCStatus.ERROR,
                "Discord RPC Client ID is not configured. Set discord_config.application_id or persistent.discord_rpc_client_id."
            )
            return False

        with self._lock:
            if self.connected:
                return True

        self._ensure_worker_running()
        self._connection_event.clear()
        self._cmd_queue.put(('CONNECT', None))

        should_sync = sync_startup if sync_startup is not None else self.startup_sync_enabled
        if should_sync:
            self._connection_event.wait(timeout=self.startup_timeout)

        return True

    def disconnect(self) -> None:
        """Disconnect from Discord RPC without disabling persistent preference."""
        self._ensure_worker_running()
        self._cmd_queue.put(('DISCONNECT', None))

    def update_presence(self, force: bool = False, **kwargs) -> bool:
        """
        Queue a Discord Rich Presence update without blocking main thread.
        """
        if not self.enabled:
            return False

        with self._lock:
            self.last_update = kwargs.copy()

        self._ensure_worker_running()
        self._cmd_queue.put(('UPDATE', (kwargs.copy(), force)))
        return True

    def clear_presence(self) -> bool:
        """Clear active presence in Discord."""
        if not self.enabled:
            return False

        self._ensure_worker_running()
        self._cmd_queue.put(('CLEAR', None))
        return True

    def stop(self) -> None:
        """Terminate background worker thread on game exit."""
        self._shutdown_flag = True
        if self._worker_thread and self._worker_thread.is_alive():
            self._cmd_queue.put(('STOP', None))
            self._worker_thread.join(timeout=DISCORD_THREAD_JOIN_TIMEOUT)


# Global Discord RPC instance
discord_rpc = DiscordRPC()

"""renpy
init python:
"""

def init_discord_rpc():
    """Initialize Discord RPC during RenPy startup."""
    try:
        discord_rpc._load_config()
        if discord_rpc.is_enabled():
            discord_rpc.enable(sync_startup=False)

        if callable(globals().get('init_reliable_discord_rpc')):
            init_reliable_discord_rpc()
    except Exception as e:
        print(f"Discord RPC initialization error: {e}")

init_discord_rpc()

"""renpy
init python:
"""

def discord_rpc_on_label_start(label_name):
    """Called when a label starts."""
    if discord_rpc.enabled:
        discord_rpc.update_presence(
            state=f"В сцене: {label_name}",
            details=getattr(config, 'name', None) or 'RenPy Game'
        )

def discord_rpc_on_menu():
    """Called when entering a menu."""
    if discord_rpc.enabled:
        discord_rpc.update_presence(
            state="В меню",
            details=getattr(config, 'name', None) or 'RenPy Game'
        )

"""renpy
init python:
"""

def discord_rpc_cleanup():
    """Clean up Discord RPC on game exit."""
    if discord_rpc:
        discord_rpc.disconnect()
        discord_rpc.stop()

if hasattr(config, 'quit_callbacks') and config.quit_callbacks is not None:
    config.quit_callbacks.append(discord_rpc_cleanup)
