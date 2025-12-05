# Discord RPC Reliability and Error Handling Module
# Provides robust error handling, reconnection logic, and failure recovery

# IDE hints (not executed by Ren'Py)
from typing import Optional, Any, Dict
import threading
import time
from queue import Queue, Empty

discord_rpc: Any = None
reliable_discord_rpc: Any = None
config: Any = None
DiscordRPCStatus: Any = None
DISCORD_QUEUE_MAX_SIZE: int = 100
DISCORD_THREAD_JOIN_TIMEOUT: float = 2.0
DISCORD_MONITOR_INTERVAL: float = 5.0

"""renpy
init python:
"""

import threading
import time
from queue import Queue, Empty


class DiscordRPCReliabilityManager:
    """
    Manages reliability features for Discord RPC
    Handles reconnection, error recovery, and connection monitoring
    """
    
    def __init__(self, discord_rpc_instance):
        """
        Initialize reliability manager
        
        Args:
            discord_rpc_instance: The main DiscordRPC instance
        """
        self.discord_rpc = discord_rpc_instance
        self.monitor_thread = None
        self.monitoring = False
        self.update_queue = Queue(maxsize=DISCORD_QUEUE_MAX_SIZE)
        self.last_successful_update = None
        self.connection_timeout = 30.0
        self.update_timeout = 10.0
        self.health_check_interval = 60.0
        self.max_queue_size = DISCORD_QUEUE_MAX_SIZE
        self._lock = threading.RLock()
        self._shutdown_flag = False
        
    def start_monitoring(self):
        """Start connection monitoring"""
        with self._lock:
            if self.monitoring:
                return
                
            self.monitoring = True
            self._shutdown_flag = False
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop connection monitoring"""
        with self._lock:
            self.monitoring = False
            self._shutdown_flag = True
            thread = self.monitor_thread
            
        if thread and thread.is_alive():
            thread.join(timeout=DISCORD_THREAD_JOIN_TIMEOUT * 2.5)
            if thread.is_alive():
                print("Warning: Monitor thread did not terminate cleanly")
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while not self._shutdown_flag:
            with self._lock:
                should_monitor = self.monitoring
                
            if not should_monitor:
                break
                
            try:
                self._check_connection_health()
                self._process_update_queue()
                time.sleep(DISCORD_MONITOR_INTERVAL)
            except Exception as e:
                print(f"Discord RPC monitor error: {e}")
                time.sleep(DISCORD_MONITOR_INTERVAL * 2)  # Wait longer on error
                
    def _check_connection_health(self):
        """Check if connection is healthy"""
        if not self.discord_rpc.enabled:
            return
            
        current_time = time.time()
        
        # Check for connection timeout
        if (self.discord_rpc.connection_start_time and 
            current_time - self.discord_rpc.connection_start_time > self.connection_timeout and
            self.discord_rpc.status == DiscordRPCStatus.CONNECTING):
            
            print("Discord RPC connection timeout detected")
            self.discord_rpc._set_status(DiscordRPCStatus.TIMEOUT)
            self._attempt_recovery()
            
        # Check for stale updates
        if (self.last_successful_update and 
            current_time - self.last_successful_update > self.health_check_interval and
            self.discord_rpc.connected):
            
            # Send a health check update
            self._health_check_update()
            
    def _health_check_update(self):
        """Send a health check update to verify connection"""
        try:
            with self.discord_rpc._lock:
                rpc = self.discord_rpc.rpc
                is_connected = self.discord_rpc.connected
                last_update = self.discord_rpc.last_update.copy() if self.discord_rpc.last_update else None
            
            if rpc and is_connected:
                # Try a minimal update
                rpc.update(
                    state="Проверка соединения",
                    details=config.name or 'RenPy Game'
                )
                
                with self._lock:
                    self.last_successful_update = time.time()
                
                # Restore previous state if available
                if last_update:
                    def restore_state():
                        if not self._shutdown_flag:
                            self.discord_rpc._update_presence_internal(last_update)
                    threading.Timer(2.0, restore_state).start()
                    
        except Exception as e:
            print(f"Discord RPC health check failed: {e}")
            
            with self.discord_rpc._lock:
                self.discord_rpc.connected = False
                
            self.discord_rpc._set_status(DiscordRPCStatus.ERROR, e)
            self._attempt_recovery()

            
    def _process_update_queue(self):
        """Process queued updates"""
        while not self.update_queue.empty():
            try:
                update_data = self.update_queue.get_nowait()
                
                with self.discord_rpc._lock:
                    is_connected = self.discord_rpc.connected
                
                if is_connected:
                    success = self.discord_rpc._update_presence_internal(update_data)
                    if success:
                        with self._lock:
                            self.last_successful_update = time.time()
                else:
                    # Re-queue if not connected
                    if self.update_queue.qsize() < self.max_queue_size:
                        try:
                            self.update_queue.put_nowait(update_data)
                        except Exception:
                            pass  # Queue full, drop update
                    break
            except Empty:
                break
            except Exception as e:
                print(f"Error processing update queue: {e}")
                
    def queue_update(self, update_data):
        """Queue an update for reliable delivery"""
        try:
            self.update_queue.put_nowait(update_data.copy())
        except Exception as e:
            print(f"Discord RPC update queue full, dropping update: {e}")
            
    def _attempt_recovery(self):
        """Attempt to recover from connection issues"""
        with self.discord_rpc._lock:
            if not self.discord_rpc.enabled or self._shutdown_flag:
                return
                
        print("Attempting Discord RPC recovery...")
        
        # Reset connection state
        with self.discord_rpc._lock:
            self.discord_rpc.connected = False
        
        # Close existing connection
        if self.discord_rpc.rpc:
            try:
                self.discord_rpc.rpc.close()
            except Exception as e:
                print(f"Warning: Error closing RPC during recovery: {e}")
            finally:
                self.discord_rpc.rpc = None
            
        # Reset retry count if it's been a while
        current_time = time.time()
        with self.discord_rpc._lock:
            if (self.discord_rpc.connection_start_time and 
                current_time - self.discord_rpc.connection_start_time > 300):  # 5 minutes
                self.discord_rpc.retry_count = 0
            
            retry_count = self.discord_rpc.retry_count
            max_retries = self.discord_rpc.max_retries
            
        # Attempt reconnection
        if retry_count < max_retries and not self._shutdown_flag:
            def reconnect():
                if not self._shutdown_flag:
                    self.discord_rpc.connect()
            threading.Timer(self.discord_rpc.retry_delay, reconnect).start()
        else:
            print("Discord RPC max retries exceeded, giving up")
            self.discord_rpc._set_status(DiscordRPCStatus.ERROR)


class DiscordRPCErrorHandler:
    """Handles specific Discord RPC errors and provides appropriate responses"""
    
    @staticmethod
    def handle_connection_error(error):
        """Handle connection-related errors"""
        error_str = str(error).lower()
        
        if "discord not found" in error_str or "no discord client" in error_str:
            return "Discord не запущен. Запустите Discord и попробуйте снова."
        elif "invalid client id" in error_str:
            return "Неверный Client ID. Проверьте настройки Discord RPC."
        elif "connection refused" in error_str:
            return "Discord отклонил соединение. Проверьте настройки Discord."
        elif "timeout" in error_str:
            return "Таймаут подключения к Discord."
        else:
            return f"Ошибка подключения: {error}"
            
    @staticmethod
    def handle_update_error(error):
        """Handle update-related errors"""
        error_str = str(error).lower()
        
        if "invalid payload" in error_str:
            return "Неверные данные для обновления статуса."
        elif "rate limit" in error_str:
            return "Слишком частые обновления. Подождите немного."
        elif "connection lost" in error_str:
            return "Соединение с Discord потеряно."
        else:
            return f"Ошибка обновления: {error}"


class ReliableDiscordRPC:
    """Wrapper that adds reliability features to the main Discord RPC"""
    
    def __init__(self, discord_rpc_instance):
        self.discord_rpc = discord_rpc_instance
        self.reliability_manager = DiscordRPCReliabilityManager(discord_rpc_instance)
        self.error_handler = DiscordRPCErrorHandler()
        
        # Add status callback for monitoring
        self.discord_rpc.add_status_callback(self._on_status_change)
        
    def _on_status_change(self, old_status, new_status):
        """Handle status changes"""
        if new_status == DiscordRPCStatus.CONNECTED:
            self.reliability_manager.start_monitoring()
        elif new_status in [DiscordRPCStatus.DISABLED, DiscordRPCStatus.ERROR]:
            self.reliability_manager.stop_monitoring()
            
    def safe_update(self, **kwargs):
        """Safely update Discord RPC with error handling"""
        try:
            with self.discord_rpc._lock:
                is_enabled = self.discord_rpc.enabled
                is_connected = self.discord_rpc.connected
            
            if is_enabled and is_connected:
                return self.discord_rpc.update_presence(**kwargs)
            else:
                # Queue for later delivery
                self.reliability_manager.queue_update(kwargs)
                return True
        except Exception as e:
            error_msg = self.error_handler.handle_update_error(e)
            print(f"Discord RPC safe update failed: {error_msg}")
            return False
            
    def safe_connect(self):
        """Safely connect with enhanced error handling"""
        try:
            return self.discord_rpc.connect()
        except Exception as e:
            error_msg = self.error_handler.handle_connection_error(e)
            print(f"Discord RPC safe connect failed: {error_msg}")
            self.discord_rpc._set_status(DiscordRPCStatus.ERROR, error_msg)
            return False
            
    def cleanup(self):
        """Cleanup reliability features"""
        self.reliability_manager.stop_monitoring()


# Create reliable wrapper for global discord_rpc instance
reliable_discord_rpc = None


def init_reliable_discord_rpc():
    """Initialize reliable Discord RPC wrapper"""
    global reliable_discord_rpc
    try:
        if 'discord_rpc' in globals() and discord_rpc and not reliable_discord_rpc:
            reliable_discord_rpc = ReliableDiscordRPC(discord_rpc)
    except NameError:
        # discord_rpc not yet initialized, will be called later
        pass

# Initialize after discord_rpc is created
init_reliable_discord_rpc()


"""renpy
init python:
"""

# Enhanced API functions with reliability

def discord_safe_update(**kwargs):
    """Safely update Discord RPC status"""
    if reliable_discord_rpc:
        return reliable_discord_rpc.safe_update(**kwargs)
    return False
    
def discord_safe_connect():
    """Safely connect to Discord RPC"""
    if reliable_discord_rpc:
        return reliable_discord_rpc.safe_connect()
    return False
    
def get_discord_error_info():
    """Get last Discord RPC error information"""
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
    """Cleanup reliable Discord RPC on exit"""
    if reliable_discord_rpc:
        reliable_discord_rpc.cleanup()

config.quit_callbacks.append(cleanup_reliable_discord_rpc)
