from flask import Blueprint, jsonify, request
from app.services.message import MessageService

message_blueprint = Blueprint('message', __name__)


@message_blueprint.route('/message', methods=['POST'])
def add_message():
  message_data = request.json
  new_message = MessageService.create_message(message_data)
  return jsonify(new_message), 201


@message_blueprint.route('/message/<message>', methods=['GET'])
def get_message(message):
  message_obj = MessageService.get_one_message(message)
  if message_obj:
    return jsonify(message_obj)
  return jsonify({'error': 'Message not found'}), 404


@message_blueprint.route('/message', methods=['GET'])
def get_messages():
  messages = MessageService.get_all_messages()
  if messages:
    return jsonify(messages)
  return jsonify({'error': 'Messages not found'}), 404


"""@message_blueprint.route('/message/<name>', methods=['GET'])
def get_message(name):
  message = Message.read_by_name(current_app.mongo_db, name)
  if message:
    return jsonify(message)
  return jsonify({"error": "Message not found"}), 404

@message_blueprint.route('/message', methods=['GET'])
def get_all_messages():
  messages = Message.read_all(current_app.mongo_db)
  return jsonify(messages)

@message_blueprint.route('/message', methods=['POST'])
def add_message():
  new_message = request.json
  result = Message.create(current_app.mongo_db, new_message)
  return jsonify({"message": "Message added successfully", "id": result}), 201

@message_blueprint.route('/message/<name>', methods=['PUT'])
def update_message(name):
  update_data = request.json
  result = Message.update(current_app.mongo_db, name, update_data)
  if result:
    return jsonify({"message": "Message updated successfully"})
  return jsonify({"error": "Message not found or no changes made"}), 404

@message_blueprint.route('/message/<name>', methods=['DELETE'])
def delete_message(name):
  result = Message.delete(current_app.mongo_db, name)
  if result:
    return jsonify({"message": "Message deleted successfully"})
  return jsonify({"error": "Message not found"}), 404"""