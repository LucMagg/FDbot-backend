from flask import Blueprint, jsonify, request
from app.services.level import LevelService

levels_blueprint = Blueprint('levels', __name__)

@levels_blueprint.route('/levels', methods=['POST'])
def add_level():
  level_data = request.json
  new_level = LevelService.create_level(level_data)
  return jsonify(new_level.to_dict()), 201

@levels_blueprint.route('/levels/<level>', methods=['GET'])
def get_level_by_id(level):
  level_obj = LevelService.get_one_level_by_id(level)
  if level_obj:
    return jsonify(level_obj.to_dict())
  return jsonify({'error': 'Level not found'}), 404

@levels_blueprint.route('/levels', methods=['GET'])
def get_level():
  level = request.args.get('level')
  floor = request.args.get('floor')
  number = request.args.get('number')
 
  if level is not None and floor is not None and number is not None:
    level_obj = LevelService.get_one_level(str(level), int(floor), int(number))
    if level_obj:
      return jsonify(level_obj.to_dict())
  else:
    levels = LevelService.get_all_levels()
    if levels:
      return jsonify([level.to_dict() for level in levels])
  if level_obj:
    return jsonify(level_obj.to_dict())
  return jsonify({'error': 'Level(s) not found'}), 404