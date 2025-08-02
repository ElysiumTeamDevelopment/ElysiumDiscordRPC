# Discord RPC Module for RenPy
# Provides Discord Rich Presence integration with flexible configuration

init -1 python:
    import threading
    import time
    import traceback
    
    try:
        from pypresence import Presence
        PYPRESENCE_AVAILABLE = True
    except ImportError:
        PYPRESENCE_AVAILABLE = False
        print("Warning: pypresence not available. Discord RPC will be disabled.")

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
            # Try to get client ID from config, then persistent settings, then parameter
            try:
                if hasattr(persistent, 'discord_rpc_client_id') and persistent.discord_rpc_client_id:
                    self.client_id = persistent.discord_rpc_client_id
                elif hasattr(discord_config, 'application_id') and discord_config.application_id:
                    self.client_id = discord_config.application_id
                else:
                    self.client_id = client_id or "1234567890123456789"  # Default placeholder
            except:
                # Fallback if config/persistent not available yet
                self.client_id = client_id or "1234567890123456789"
            self.rpc = None
            self.status = DiscordRPCStatus.DISABLED
            self.enabled = False
            self.connected = False
            self.connection_thread = None
            self.last_update = {}
            self.retry_count = 0
            # Load settings from config
            self.max_retries = get_discord_config('connection.max_retries', 3)
            self.retry_delay = get_discord_config('connection.retry_delay', 5.0)
            self.startup_sync_enabled = get_discord_config('connection.startup_sync_enabled', True)
            self.startup_timeout = get_discord_config('connection.startup_timeout', 5.0)
            self.connection_timeout = get_discord_config('connection.connection_timeout', 30.0)
            self.max_pending_updates = get_discord_config('queue.max_pending_updates', 10)

            self.last_error = None
            self.connection_start_time = None
            self.status_callbacks = []
            self.pending_updates = []  # Queue updates during initial connection
            
        def is_enabled(self):
            """Check if Discord RPC is enabled in preferences"""
            return getattr(persistent, 'discord_rpc_enabled', True)
            
        def get_status(self):
            """Get current connection status"""
            return self.status

        def get_status_info(self):
            """Get detailed status information"""
            return {
                'status': self.status,
                'enabled': self.enabled,
                'connected': self.connected,
                'retry_count': self.retry_count,
                'last_error': self.last_error,
                'color': DiscordRPCStatus.get_color(self.status)
            }

        def add_status_callback(self, callback):
            """Add callback for status changes"""
            if callback not in self.status_callbacks:
                self.status_callbacks.append(callback)

        def remove_status_callback(self, callback):
            """Remove status callback"""
            if callback in self.status_callbacks:
                self.status_callbacks.remove(callback)

        def _notify_status_change(self, old_status, new_status):
            """Notify all callbacks about status change"""
            for callback in self.status_callbacks:
                try:
                    callback(old_status, new_status)
                except Exception as e:
                    print(f"Status callback error: {e}")

        def _set_status(self, new_status, error=None):
            """Internal method to set status and notify callbacks"""
            old_status = self.status
            self.status = new_status
            if error:
                self.last_error = str(error)
            self._notify_status_change(old_status, new_status)
            
        def enable(self):
            """Enable Discord RPC"""
            if not PYPRESENCE_AVAILABLE:
                self.status = DiscordRPCStatus.ERROR
                return False
                
            self.enabled = True
            persistent.discord_rpc_enabled = True
            return self.connect()
            
        def disable(self):
            """Disable Discord RPC"""
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

            if self.connected:
                return True

            if self.connection_thread and self.connection_thread.is_alive():
                return True

            import time
            self.connection_start_time = time.time()
            self._set_status(DiscordRPCStatus.CONNECTING)

            # Determine if we should sync during startup
            should_sync = sync_startup if sync_startup is not None else self.startup_sync_enabled

            if should_sync:
                # Try synchronous connection first (with timeout)
                return self._connect_sync_with_timeout()
            else:
                # Asynchronous connection
                self.connection_thread = threading.Thread(target=self._connect_thread, daemon=True)
                self.connection_thread.start()
                return True

        def _connect_sync_with_timeout(self):
            """
            Try synchronous connection with timeout for startup
            Falls back to async if timeout exceeded
            """
            import time
            import threading

            connection_result = {'success': False, 'error': None}

            def sync_connect():
                try:
                    if self.rpc:
                        try:
                            self.rpc.close()
                        except:
                            pass

                    self.rpc = Presence(self.client_id)
                    self.rpc.connect()
                    self.connected = True
                    self._set_status(DiscordRPCStatus.CONNECTED)
                    self.retry_count = 0
                    connection_result['success'] = True

                    # Set initial presence using config template
                    initial_presence = get_presence_template('main_menu_presence')
                    if initial_presence:
                        self._update_presence_internal(initial_presence)

                    # Process any pending updates
                    self._process_pending_updates()

                except Exception as e:
                    connection_result['error'] = e

            # Start sync connection in thread
            sync_thread = threading.Thread(target=sync_connect, daemon=True)
            sync_thread.start()

            # Wait with timeout
            sync_thread.join(timeout=self.startup_timeout)

            if sync_thread.is_alive():
                # Timeout exceeded, fall back to async
                print(f"Discord RPC startup sync timeout ({self.startup_timeout}s), falling back to async")
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
                self.connection_thread = threading.Thread(target=self._connect_thread, daemon=True)
                self.connection_thread.start()
                return True
            
        def _connect_thread(self):
            """Internal connection thread"""
            try:
                if self.rpc:
                    try:
                        self.rpc.close()
                    except:
                        pass
                        
                self.rpc = Presence(self.client_id)
                self.rpc.connect()
                self.connected = True
                self._set_status(DiscordRPCStatus.CONNECTED)
                self.retry_count = 0
                
                # Set initial presence
                self._update_presence_internal({
                    'state': 'В главном меню',
                    'details': config.name or 'RenPy Game',
                    'large_image': 'game_icon',
                    'large_text': config.name or 'RenPy Game'
                })
                
            except Exception as e:
                self.connected = False
                self._set_status(DiscordRPCStatus.ERROR, e)
                self.retry_count += 1

                if self.retry_count < self.max_retries:
                    # Schedule retry
                    self._set_status(DiscordRPCStatus.RECONNECTING)
                    threading.Timer(self.retry_delay, self._connect_thread).start()
                else:
                    print(f"Discord RPC connection failed after {self.max_retries} attempts: {e}")
                    
        def disconnect(self):
            """Disconnect from Discord RPC"""
            self.connected = False
            
            if self.rpc:
                try:
                    self.rpc.close()
                except:
                    pass
                self.rpc = None
                
            if self.connection_thread and self.connection_thread.is_alive():
                # Thread will exit naturally when it checks self.connected
                pass

            self._set_status(DiscordRPCStatus.DISCONNECTED)
            
        def _process_pending_updates(self):
            """Process any pending updates from startup"""
            while self.pending_updates:
                try:
                    update_data = self.pending_updates.pop(0)
                    self._update_presence_internal(update_data)
                except Exception as e:
                    print(f"Error processing pending update: {e}")

        def update_presence(self, **kwargs):
            """
            Update Discord Rich Presence

            Args:
                state (str): Current state text
                details (str): Details text
                large_image (str): Large image key
                large_text (str): Large image tooltip
                small_image (str): Small image key
                small_text (str): Small image tooltip
                start (int): Start timestamp
                end (int): End timestamp
                party_id (str): Party ID
                party_size (list): [current_size, max_size]
                join (str): Join secret
                spectate (str): Spectate secret
                match (str): Match secret
                buttons (list): List of button dicts with 'label' and 'url'
            """
            if not self.enabled:
                return False

            # Store the update for potential retry
            self.last_update = kwargs.copy()

            if not self.connected:
                # If not connected yet, queue the update
                if self.status == DiscordRPCStatus.CONNECTING and len(self.pending_updates) < self.max_pending_updates:
                    self.pending_updates.append(kwargs.copy())
                    return True
                return False

            return self._update_presence_internal(kwargs)
            
        def _update_presence_internal(self, kwargs):
            """Internal presence update method"""
            try:
                if self.rpc and self.connected:
                    self.rpc.update(**kwargs)
                    return True
            except Exception as e:
                print(f"Discord RPC update failed: {e}")
                self.connected = False
                self._set_status(DiscordRPCStatus.ERROR, e)

                # Try to reconnect
                if self.enabled:
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

# Initialize Discord RPC on game start
init python:
    def init_discord_rpc():
        """Initialize Discord RPC if enabled"""
        try:
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

# RenPy integration hooks
init python:
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

# Cleanup on quit
init python:
    def discord_rpc_cleanup():
        """Cleanup Discord RPC on game exit"""
        if discord_rpc:
            discord_rpc.disconnect()
    
    config.quit_callbacks.append(discord_rpc_cleanup)
