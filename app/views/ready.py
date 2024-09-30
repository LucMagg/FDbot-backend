from flask import Blueprint, jsonify

ready_blueprint = Blueprint('ready', __name__)


@ready_blueprint.route('/', methods=['GET'])
def app_is_ready():
  return jsonify({'message': 'I\'m ready :)'}), 200