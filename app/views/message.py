from flask import Blueprint, jsonify, request, current_app
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
  req = '/message GET'
  current_app.logger.req(req)

  messages = MessageService.get_all_messages()
  if messages:
    current_app.logger.req_ok(req)
    return jsonify(messages)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Messages not found'}), 404