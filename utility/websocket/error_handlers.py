from flask import current_app
import traceback


def handle_socketio_error(e):
    """WebSocket Error Handler."""

    print("handle_socketio_error")
    print(traceback.format_exc())
    current_app.logger.info(traceback.format_exc())
    return current_app.jsonify.default_format(status_code=500, message=str(e)), 500
