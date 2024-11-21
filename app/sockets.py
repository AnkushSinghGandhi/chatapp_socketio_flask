from flask_socketio import emit, join_room, leave_room
from app import socketio

@socketio.on("connect")
def handle_connect():
    emit("message", {"message": "User connected!"})

@socketio.on("send_message")
def handle_send_message(data):
    room = data.get("room")
    message = data.get("message")
    emit("receive_message", {"message": message}, room=room)

@socketio.on("join_room")
def handle_join_room(data):
    room = data.get("room")
    join_room(room)
    emit("message", {"message": f"Joined room {room}"}, room=room)

@socketio.on("leave_room")
def handle_leave_room(data):
    room = data.get("room")
    leave_room(room)
    emit("message", {"message": f"Left room {room}"}, room=room)
