from application import create_app
from swagger_ui import api_doc
from flask_cors import CORS
from utility.websocket.globals import websocket_manager
from dotenv import load_dotenv
import os
load_dotenv("./config/.env")


app = create_app(os.getenv('MODE'))
websocket_manager.WebSocketIO.init_app(app)
CORS(app)

api_doc(app, config_path='swagger_config.json',
        url_prefix='/api/doc', title='API doc')

if __name__ == '__main__':
#     app.run(host='0.0.0.0')
    websocket_manager.WebSocketIO.run(app, host='0.0.0.0', debug=True)

