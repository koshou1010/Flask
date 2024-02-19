from flask_socketio import SocketIO
from .error_handlers import handle_socketio_error


class WebSocket_Manager:
    """
    Manager for WebSocket.
    """
    WebSocketIO = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def setup(self, async_mode: str, cors_allowed_origins: list, ping_interval: int, ping_timeout: int):
        """
        Setup SocketIO with async mode, ping interval, ping timeout and cross domain config.
        """
        self.WebSocketIO = SocketIO(
            async_mode=async_mode,
            cors_allowed_origins=cors_allowed_origins,
            ping_interval=ping_interval,
            ping_timeout=ping_timeout
        )

        self.WebSocketIO.on_error = handle_socketio_error

    def set_event_handler(self, event: str, event_handler):
        """
        Set handlers for specific event.
        """
        self.WebSocketIO.on_event(event, event_handler)

    def emit(self, event: str, message: dict, namespace: str = None, room: str = None):
        """
        Push event message via namespace.
        """
        if namespace:
            self.WebSocketIO.emit(event, message, namespace=f'/{namespace}', room=room)
        else:
            self.WebSocketIO.emit(event, message)
