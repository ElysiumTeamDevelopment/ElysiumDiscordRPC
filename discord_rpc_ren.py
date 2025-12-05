# Discord RPC Module for RenPy
# Provides Discord Rich Presence integration with flexible configuration

# IDE hints (not executed by Ren'Py)
from typing import Optional, Dict, Any, List, Callable
import threading
import time
from queue import Queue

# Ren'Py store hints
discord_rpc: Any = None
persistent: Any = None
config: Any = None
discord_config: Any = None
get_discord_config: Callable = None
get_presence_template: Callable = None
init_reliable_discord_rpc: Callable = None
PYPRESENCE_AVAILABLE: bool = True

"""renpy
init -1 python:
"""

import threading
import time
import traceback
from queue import Queue

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
DISCORD_MONITOR_INTERVAL = 5.0
DISCORD_RETRY_RESET_TIME = 300  # 5 minutes in seconds


class DiscordRPCStatus:
    """Enum-like class for Discord RPC connection status"""
    DISABLED = "Отключен"
    CONNECTING = "Подключение"
    CONNECTED = "Подключен"
    ERROR = "Ошибка"
    DISCONNECTED = "Отключен"
    RECONNECTING = "Переподключение"
    TIMEOUT = "Таймаут"

    @staticmethod
    def get_color(status):
        """Get color code for status display"""
        colors = {
            DiscordRPCStatus.DISABLED: "#808080",
            DiscordRPCStatus.CONNECTING: "#ffaa00",
            DiscordRPCStatus.CONNECTED: "#00ff00",
            DiscordRPCStatus.ERROR: "#ff0000",
            DiscordRPCStatus.DISCONNECTED: "#808080",
            DiscordRPCStatus.RECONNECTING: "#ffaa00",
            DiscordRPCStatus.TIMEOUT: "#ff8800"
        }
        return colors.get(status, "#ffffff")


class DiscordRPC:
    """
    Main Discord RPC class for RenPy integration
    Handles connection, status updates, and error management
    """
    
    def __init__(self, client_id=None):
        """
        Initialize Discord RPC client

        Args:
            client_id (str): Discord application client ID
        """
        # Initialize with default client_id, will be updated later
        self.client_id = client_id or DISCORD_DEFAULT_CLIENT_ID
        self.rpc = None
        self.status = DiscordRPCStatus.DISABLED
        self.enabled = False
        self.connected = False
        self.connection_thread = None
        self.last_update = {}
        self.retry_count = 0
        
        # Thread safety
        self._lock = threading.RLock()
        self._connection_lock = threading.Lock()
        
        # Load settings from config with safe defaults
        self.max_retries = 3
        self.retry_delay = 5.0
        self.startup_sync_enabled = True
        self.startup_timeout = 5.0
        self.connection_timeout = 30.0
        self.max_pending_updates = 10

        self.last_error = None
        self.connection_start_time = None
        self.status_callbacks = []  # List of callbacks (RenPy compatible)
        self.pending_updates = Queue(maxsize=DISCORD_QUEUE_MAX_SIZE)  # Thread-safe queue
        self._shutdown_flag = False
        
    def _load_config(self):
        """Load configuration after init phase"""
        try:
            # Try to get client ID from persistent, then config
            if hasattr(persistent, 'discord_rpc_client_id') and persistent.discord_rpc_client_id:
                self.client_id = persistent.discord_rpc_client_id
            elif hasattr(discord_config, 'application_id') and discord_config.application_id:
                self.client_id = discord_config.application_id
                
            # Load other settings
            self.max_retries = get_discord_config('connection.max_retries', 3)
            self.retry_delay = get_discord_config('connection.retry_delay', 5.0)
            self.startup_sync_enabled = get_discord_config('connection.startup_sync_enabled', True)
            self.startup_timeout = get_discord_config('connection.startup_timeout', 5.0)
            self.connection_timeout = get_discord_config('connection.connection_timeout', 30.0)
            self.max_pending_updates = get_discord_config('queue.max_pending_updates', 10)
        except Exception as e:
            print(f"Warning: Failed to load Discord RPC config: {e}")
        
    def is_enabled(self):
        """
        Check if Discord RPC is enabled in preferences
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return getattr(persistent, 'discord_rpc_enabled', True)
        
    def get_status(self):
        """
        Get current connection status
        
        Returns:
            str: Current status (DISABLED, CONNECTING, CONNECTED, ERROR, etc.)
        """
        return self.status

    def get_status_info(self):
        """
        Get detailed status information
        
        Returns:
            dict: Dictionary with keys:
                - status (str): Current status text
                - enabled (bool): Whether RPC is enabled
                - connected (bool): Whether connected to Discord
                - retry_count (int): Number of retry attempts
                - last_error (str): Last error message or None
                - color (str): Hex color code for status display
        """
        return {
            'status': self.status,
            'enabled': self.enabled,
            'connected': self.connected,
            'retry_count': self.retry_count,
            'last_error': self.last_error,
            'color': DiscordRPCStatus.get_color(self.status)
        }

    def add_status_callback(self, callback):
        """
        Add callback for status changes
        
        Args:
            callback (callable): Function to call on status change.
                Signature: callback(old_status, new_status)
        """
        if callback not in self.status_callbacks:
            self.status_callbacks.append(callback)

    def remove_status_callback(self, callback):
        """
        Remove status callback
        
        Args:
            callback (callable): Previously registered callback to remove
        """
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)

    def _notify_status_change(self, old_status, new_status):
        """Notify all callbacks about status change"""
        with self._lock:
            callbacks = list(self.status_callbacks)
        
        for callback in callbacks:
            try:
                callback(old_status, new_status)
            except Exception as e:
                print(f"Status callback error: {e}")

    def _set_status(self, new_status, error=None):
        """Internal method to set status and notify callbacks"""
        with self._lock:
            old_status = self.status
            self.status = new_status
            if error:
                self.last_error = str(error)
        self._notify_status_change(old_status, new_status)
        
    def enable(self):
        """
        Enable Discord RPC and attempt connection
        
        Returns:
            bool: True if connection started, False if pypresence unavailable
        """
        if not PYPRESENCE_AVAILABLE:
            self.status = DiscordRPCStatus.ERROR
            return False
            
        self.enabled = True
        persistent.discord_rpc_enabled = True
        return self.connect()
        
    def disable(self):
        """
        Disable Discord RPC and disconnect
        
        This will close the connection and prevent automatic reconnection.
        """
        self.enabled = False
        persistent.discord_rpc_enabled = False
        self.disconnect()
        self._set_status(DiscordRPCStatus.DISABLED)

        
    def connect(self, sync_startup=None):
        """
        Connect to Discord RPC

        Args:
            sync_startup (bool): If True, wait for connection during startup
        Returns True if connection successful or in progress
        """
        if not self.enabled or not PYPRESENCE_AVAILABLE:
            return False

        with self._lock:
            if self.connected:
                return True

        # Use connection lock to prevent multiple simultaneous connection attempts
        if not self._connection_lock.acquire(blocking=False):
            # Another connection attempt is in progress
            return True

        try:
            with self._lock:
                if self.connection_thread and self.connection_thread.is_alive():
                    return True

            self.connection_start_time = time.time()
            self._set_status(DiscordRPCStatus.CONNECTING)

            # Determine if we should sync during startup
            should_sync = sync_startup if sync_startup is not None else self.startup_sync_enabled

            if should_sync:
                # Try synchronous connection first (with timeout)
                return self._connect_sync_with_timeout()
            else:
                # Asynchronous connection
                with self._lock:
                    self.connection_thread = threading.Thread(target=self._connect_thread, daemon=True)
                    self.connection_thread.start()
                return True
        finally:
            self._connection_lock.release()

    def _connect_sync_with_timeout(self):
        """
        Try synchronous connection with timeout for startup
        Falls back to async if timeout exceeded
        """
        connection_result = {'success': False, 'error': None}

        def sync_connect():
            if self._shutdown_flag:
                return
                
            try:
                # Close existing connection safely
                if self.rpc:
                    try:
                        self.rpc.close()
                    except Exception as e:
                        print(f"Warning: Error closing old RPC connection: {e}")
                    finally:
                        self.rpc = None

                self.rpc = Presence(self.client_id)
                self.rpc.connect()
                
                with self._lock:
                    self.connected = True
                    self.retry_count = 0
                
                self._set_status(DiscordRPCStatus.CONNECTED)
                connection_result['success'] = True

                # Set initial presence using config template
                initial_presence = get_presence_template('main_menu_presence')
                if initial_presence:
                    self._update_presence_internal(initial_presence)

                # Process any pending updates
                self._process_pending_updates()

            except Exception as e:
                connection_result['error'] = e
                print(f"Discord RPC sync connection error: {e}")

        # Start sync connection in thread
        sync_thread = threading.Thread(target=sync_connect, daemon=True)
        sync_thread.start()

        # Wait with timeout
        sync_thread.join(timeout=self.startup_timeout)

        if sync_thread.is_alive():
            # Timeout exceeded, fall back to async
            print(f"Discord RPC startup sync timeout ({self.startup_timeout}s), falling back to async")
            with self._lock:
                self.connection_thread = threading.Thread(target=self._connect_thread, daemon=True)
                self.connection_thread.start()
            return True
        elif connection_result['success']:
            # Successful sync connection
            return True
        else:
            # Failed sync connection, try async
            if connection_result['error']:
                print(f"Discord RPC sync connection failed: {connection_result['error']}")
            with self._lock:
                self.connection_thread = threading.Thread(target=self._connect_thread, daemon=True)
                self.connection_thread.start()
            return True
        
    def _connect_thread(self):
        """Internal connection thread"""
        if self._shutdown_flag:
            return
            
        try:
            # Close existing connection safely
            if self.rpc:
                try:
                    self.rpc.close()
                except Exception as e:
                    print(f"Warning: Error closing old RPC connection: {e}")
                finally:
                    self.rpc = None
                    
            self.rpc = Presence(self.client_id)
            self.rpc.connect()
            
            with self._lock:
                self.connected = True
                self.retry_count = 0
            
            self._set_status(DiscordRPCStatus.CONNECTED)
            
            # Set initial presence
            self._update_presence_internal({
                'state': 'В главном меню',
                'details': config.name or 'RenPy Game',
                'large_image': 'game_icon',
                'large_text': config.name or 'RenPy Game'
            })
            
            # Process pending updates
            self._process_pending_updates()
            
        except Exception as e:
            with self._lock:
                self.connected = False
                self.retry_count += 1
                current_retry = self.retry_count
            
            self._set_status(DiscordRPCStatus.ERROR, e)
            print(f"Discord RPC connection error (attempt {current_retry}): {e}")

            if current_retry < self.max_retries and not self._shutdown_flag:
                # Schedule retry
                self._set_status(DiscordRPCStatus.RECONNECTING)
                threading.Timer(self.retry_delay, self._connect_thread).start()
            else:
                print(f"Discord RPC connection failed after {self.max_retries} attempts")
                
    def disconnect(self):
        """Disconnect from Discord RPC"""
        self._shutdown_flag = True
        
        with self._lock:
            self.connected = False
        
        if self.rpc:
            try:
                self.rpc.close()
            except Exception as e:
                print(f"Warning: Error closing RPC connection: {e}")
            finally:
                self.rpc = None
            
        # Wait for connection thread to finish (with timeout)
        with self._lock:
            thread = self.connection_thread
            
        if thread and thread.is_alive():
            thread.join(timeout=DISCORD_THREAD_JOIN_TIMEOUT)
            if thread.is_alive():
                print("Warning: Connection thread did not terminate cleanly")

        self._set_status(DiscordRPCStatus.DISCONNECTED)
        self._shutdown_flag = False
        
    def _process_pending_updates(self):
        """Process any pending updates from startup"""
        if self.pending_updates is None or self.rpc is None:
            return
            
        while not self.pending_updates.empty():
            try:
                update_data = self.pending_updates.get_nowait()
                self._update_presence_internal(update_data)
            except Exception as e:
                print(f"Error processing pending update: {e}")
                break


    def update_presence(self, **kwargs):
        """
        Update Discord Rich Presence
        
        Args:
            state (str): Current state text (max 128 chars recommended)
            details (str): Details text (max 128 chars recommended)
            large_image (str): Large image key from Discord assets
            large_text (str): Large image hover text
            small_image (str): Small image key from Discord assets
            small_text (str): Small image hover text
            start (int): Unix timestamp for elapsed time display
            end (int): Unix timestamp for remaining time display
            party_id (str): Unique party identifier
            party_size (list): [current_size, max_size] for party display
            buttons (list): Max 2 buttons with 'label' and 'url' keys
            
        Returns:
            bool: True if update successful or queued, False otherwise
            
        Example:
            discord_rpc.update_presence(
                state="В главном меню",
                details="Моя игра",
                large_image="game_icon",
                large_text="Название игры"
            )
        """
        if not self.enabled:
            return False

        # Store the update for potential retry
        with self._lock:
            self.last_update = kwargs.copy()
            is_connected = self.connected
            current_status = self.status

        if not is_connected:
            # If not connected yet, queue the update
            if current_status == DiscordRPCStatus.CONNECTING:
                try:
                    self.pending_updates.put_nowait(kwargs.copy())
                    return True
                except Exception as e:
                    print(f"Warning: Failed to queue update: {e}")
            return False

        return self._update_presence_internal(kwargs)
        
    def _update_presence_internal(self, kwargs):
        """
        Internal presence update method
        
        Args:
            kwargs (dict): Presence data to send to Discord
            
        Returns:
            bool: True if update successful, False otherwise
        """
        if kwargs is None:
            return False
            
        try:
            with self._lock:
                rpc = self.rpc
                is_connected = self.connected
                
            if rpc and is_connected:
                rpc.update(**kwargs)
                return True
            return False
        except Exception as e:
            print(f"Discord RPC update failed: {e}")
            print(f"  Status: {self.status}, Connected: {self.connected}")
            
            with self._lock:
                self.connected = False
                
            self._set_status(DiscordRPCStatus.ERROR, e)

            # Try to reconnect
            if self.enabled and not self._shutdown_flag:
                self.connect()
                
        return False
        
    def clear_presence(self):
        """Clear Discord Rich Presence"""
        try:
            if self.rpc and self.connected:
                self.rpc.clear()
                return True
        except Exception as e:
            print(f"Discord RPC clear failed: {e}")
            
        return False


# Global Discord RPC instance
discord_rpc = DiscordRPC()

"""renpy
init python:
"""

def init_discord_rpc():
    """Initialize Discord RPC if enabled"""
    try:
        # Load configuration after init phase
        discord_rpc._load_config()
        
        if discord_rpc.is_enabled():
            # Use sync startup for better user experience
            discord_rpc.enabled = True
            discord_rpc.connect(sync_startup=True)

        # Initialize reliable wrapper if available
        if 'init_reliable_discord_rpc' in globals():
            init_reliable_discord_rpc()
    except Exception as e:
        print(f"Discord RPC initialization error: {e}")

# Auto-initialize
init_discord_rpc()

"""renpy
init python:
"""

def discord_rpc_on_label_start(label_name):
    """Called when a label starts"""
    if discord_rpc.enabled and discord_rpc.connected:
        discord_rpc.update_presence(
            state=f"В сцене: {label_name}",
            details=config.name or 'RenPy Game'
        )

def discord_rpc_on_menu():
    """Called when entering menu"""
    if discord_rpc.enabled and discord_rpc.connected:
        discord_rpc.update_presence(
            state="В меню",
            details=config.name or 'RenPy Game'
        )

"""renpy
init python:
"""

def discord_rpc_cleanup():
    """Cleanup Discord RPC on game exit"""
    if discord_rpc:
        discord_rpc.disconnect()

config.quit_callbacks.append(discord_rpc_cleanup)
