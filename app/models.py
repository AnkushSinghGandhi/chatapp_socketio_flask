from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class ChatRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=True)  # Group rooms have names
    type = db.Column(db.String(20), nullable=False)  # "private" or "group"
    description = db.Column(db.String(255), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    last_message_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user1_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user2_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    __table_args__ = (db.UniqueConstraint("user1_id", "user2_id", name="unique_private_room"),)

    messages = db.relationship("Message", backref="room", lazy=True)
    participants = db.relationship("RoomParticipant", backref="room", lazy=True)


class RoomParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("chat_room.id"), nullable=False)
    role = db.Column(db.String(20), default="member")  # "member", "admin"
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey("chat_room.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    rooms = db.relationship("RoomParticipant", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

