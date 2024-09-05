from flask import Blueprint, jsonify, request
from app.services.level import LevelService

levels_blueprint = Blueprint('levels', __name__)

@levels_blueprint.route('/levels', methods=['GET'])
def get_levels():
  levels = LevelService.get_all_levels()
  if levels:
    return jsonify([level.to_dict() for level in levels])
  return jsonify({'error': 'Levels not found'}), 404

@levels_blueprint.route('/levels', methods=['POST'])
def add_level():
  level_data = request.json
  new_level = LevelService.create_level(level_data)
  return jsonify(new_level.to_dict()), 201

@levels_blueprint.route('/levels/<level>', methods=['GET'])
def get_level_by_id(level):
  level_obj = LevelService.get_one_level(level)
  if level_obj:
    return jsonify(level_obj.to_dict())
  return jsonify({'error': 'Level not found'}), 404


@levels_blueprint.route('/levels/<level>/reward', methods=['POST'])
def add_reward(level):
  reward_data = request.json
  level = LevelService.add_reward(level, reward_data)
  if level:
    return jsonify(level.to_dict())
  return jsonify({'error': 'Level not found'}), 404

@levels_blueprint.route('/levels/<level>/reward', methods=['GET'])
def get_expected_reward(level):
  expected_reward = LevelService.get_expected_reward(level)
  if expected_reward:
    return jsonify(expected_reward)
  return jsonify({'error': 'Level not found'}), 404