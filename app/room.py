from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import ChatRoom, RoomParticipant, User, Message

room = Blueprint("room", __name__)

@room.route("/create", methods=["POST"])
@jwt_required()
def create_room():
    data = request.get_json()
    name = data.get("name")
    room_type = data.get("type", "group")

    if ChatRoom.query.filter_by(name=name).first():
        return jsonify({"message": "Room name already exists"}), 400

    new_room = ChatRoom(name=name, type=room_type)
    db.session.add(new_room)
    db.session.commit()

    return jsonify({"message": "Room created successfully", "room_id": new_room.id}), 201

@room.route("/my_rooms", methods=["GET"])
@jwt_required()
def my_rooms():
    user_id = get_jwt_identity()
    rooms = RoomParticipant.query.filter_by(user_id=user_id).all()

    room_list = [
        {"room_id": room.room_id, "room_name": room.room.name, "room_type": room.room.type}
        for room in rooms
    ]

    return jsonify({"rooms": room_list}), 200

@room.route("/join", methods=["POST"])
@jwt_required()
def join_room():
    data = request.get_json()
    room_id = data.get("room_id")
    user_id = get_jwt_identity()

    room = ChatRoom.query.get(room_id)
    if not room:
        return jsonify({"message": "Room not found"}), 404

    if RoomParticipant.query.filter_by(user_id=user_id, room_id=room_id).first():
        return jsonify({"message": "Already part of the room"}), 400

    role = "admin" if not room.participants else "member"

    participant = RoomParticipant(user_id=user_id, room_id=room_id, role=role)
    db.session.add(participant)
    db.session.commit()

    return jsonify({"message": "Joined room successfully"}), 200

@room.route("/leave", methods=["POST"])
@jwt_required()
def leave_room():
    data = request.get_json()
    room_id = data.get("room_id")
    user_id = get_jwt_identity()

    participant = RoomParticipant.query.filter_by(user_id=user_id, room_id=room_id).first()
    if not participant:
        return jsonify({"message": "You are not part of this room"}), 404

    db.session.delete(participant)
    db.session.commit()

    return jsonify({"message": "Left room successfully"}), 200

@room.route("/private", methods=["POST"])
@jwt_required()
def private_room():
    data = request.get_json()
    other_user_id = data.get("user_id")
    current_user_id = get_jwt_identity()

    if not User.query.get(other_user_id):
        return jsonify({"message": "User not found"}), 404

    private_room = ChatRoom.query.filter(
        ((ChatRoom.user1_id == current_user_id) & (ChatRoom.user2_id == other_user_id)) |
        ((ChatRoom.user1_id == other_user_id) & (ChatRoom.user2_id == current_user_id))
    ).first()

    if not private_room:
        private_room = ChatRoom(
            type="private",
            user1_id=current_user_id,
            user2_id=other_user_id
        )
        db.session.add(private_room)
        db.session.commit()

    return jsonify({"room_id": private_room.id, "type": "private"}), 200

@room.route("/role", methods=["PATCH"])
@jwt_required()
def update_role():
    data = request.get_json()
    room_id = data.get("room_id")
    user_id = data.get("user_id")
    new_role = data.get("role")
    current_user_id = get_jwt_identity()

    current_user = RoomParticipant.query.filter_by(user_id=current_user_id, room_id=room_id, role="admin").first()
    if not current_user:
        return jsonify({"message": "Only admins can update roles"}), 403

    participant = RoomParticipant.query.filter_by(user_id=user_id, room_id=room_id).first()
    if not participant:
        return jsonify({"message": "User not in this room"}), 404

    participant.role = new_role
    db.session.commit()

    return jsonify({"message": f"User role updated to {new_role}"}), 200

@room.route("/remove", methods=["DELETE"])
@jwt_required()
def remove_participant():
    data = request.get_json()
    room_id = data.get("room_id")
    user_id = data.get("user_id")
    current_user_id = get_jwt_identity()

    current_user = RoomParticipant.query.filter_by(user_id=current_user_id, room_id=room_id, role="admin").first()
    if not current_user:
        return jsonify({"message": "Only admins can remove participants"}), 403

    participant = RoomParticipant.query.filter_by(user_id=user_id, room_id=room_id).first()
    if not participant:
        return jsonify({"message": "User not in this room"}), 404

    db.session.delete(participant)
    db.session.commit()

    return jsonify({"message": "User removed from the room"}), 200

@room.route("/details/<int:room_id>", methods=["GET"])
@jwt_required()
def room_details(room_id):
    room = ChatRoom.query.get(room_id)
    if not room:
        return jsonify({"message": "Room not found"}), 404

    participants = RoomParticipant.query.filter_by(room_id=room_id).all()
    participant_list = [{"user_id": p.user_id, "role": p.role} for p in participants]

    return jsonify({
        "id": room.id,
        "name": room.name,
        "type": room.type,
        "description": room.description,
        "avatar_url": room.avatar_url,
        "last_message_at": room.last_message_at,
        "participants": participant_list
    }), 200