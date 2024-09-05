from flask import Blueprint, jsonify, request
from app.services.command import CommandService

command_blueprint = Blueprint('command', __name__)


@command_blueprint.route('/command', methods=['POST'])
def add_command():
  command_data = request.json
  new_command = CommandService.create_command(command_data)
  return jsonify(new_command.to_dict()), 201


@command_blueprint.route('/command/<command>', methods=['GET'])
def get_command(command):
  command_obj = CommandService.get_one_command(command)
  if command_obj:
    return jsonify(command_obj.to_dict())
  return jsonify({'error': 'Command not found'}), 404


@command_blueprint.route('/command', methods=['GET'])
def get_commands():
  commands = CommandService.get_all_commands()
  if commands:
    return jsonify([command.to_dict() for command in commands])
  return jsonify({'error': 'Commands not found'}), 404