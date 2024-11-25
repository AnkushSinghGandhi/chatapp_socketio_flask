from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from app import socketio, db
from app.models import Message

@socketio.on("connect")
def handle_connect():
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("join_room")
def handle_join_room(data):
    room_id = data.get("room_id")
    user_token = data.get("token")

    if not room_id or not user_token:
        emit("error", {"message": "Invalid data"})
        return

    try:
        user_identity = decode_token(user_token)["sub"]
        join_room(str(room_id))
        emit("joined_room", {"room_id": room_id, "user_id": user_identity}, room=str(room_id))
    except Exception as e:
        emit("error", {"message": str(e)})

@socketio.on("leave_room")
def handle_leave_room(data):
    room_id = data.get("room_id")
    user_token = data.get("token")

    if not room_id or not user_token:
        emit("error", {"message": "Invalid data"})
        return

    try:
        user_identity = decode_token(user_token)["sub"]
        leave_room(str(room_id))
        emit("left_room", {"room_id": room_id, "user_id": user_identity}, room=str(room_id))
    except Exception as e:
        emit("error", {"message": str(e)})

@socketio.on("send_message")
def handle_send_message(data):
    room_id = data.get("room_id")
    user_token = data.get("token")
    content = data.get("content")

    if not room_id or not user_token or not content:
        emit("error", {"message": "Invalid data"})
        return

    try:
        user_identity = decode_token(user_token)["sub"]
        new_message = Message(room_id=room_id, user_id=user_identity, content=content)
        db.session.add(new_message)
        db.session.commit()

        emit("new_message", {
            "room_id": room_id,
            "user_id": user_identity,
            "content": content,
            "timestamp": new_message.timestamp
        }, room=str(room_id))
    except Exception as e:
        emit("error", {"message": str(e)})
