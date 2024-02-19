from .globals import websocket_manager


def initialize(app):
    """
    initialize with app config.
    Params:
        'WEBSOCKET_ASYNC_MODE': async mode.
        'WEBSOCKET_CORS_ALLOWED_ORIGINS': allowed cross domain origin.
        'WEBSOCKET_PING_INTERVAL': ping interval.
        'WEBSOCKET_PING_TIMEOUT': ping timeout.
    """
    async_mode = app.config['WEBSOCKET_ASYNC_MODE']
    cors_allowed_origins = app.config['WEBSOCKET_CORS_ALLOWED_ORIGINS']
    ping_interval = app.config['WEBSOCKET_PING_INTERVAL']
    ping_timeout = app.config['WEBSOCKET_PING_TIMEOUT']

    websocket_manager.setup(async_mode=async_mode, cors_allowed_origins=cors_allowed_origins,
                            ping_interval=ping_interval, ping_timeout=ping_timeout)
