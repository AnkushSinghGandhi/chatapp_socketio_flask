from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(async_mode="gevent")
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object("config.Config")

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)
    jwt.init_app(app)

    # Register blueprints (for routes)
    from app.auth import auth
    app.register_blueprint(auth, url_prefix="/auth")
    from app.room import room
    app.register_blueprint(room, url_prefix="/room")


    return app
