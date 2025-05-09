from flask import Blueprint, jsonify, request, current_app
from app.services.level import LevelService

levels_blueprint = Blueprint('levels', __name__)

@levels_blueprint.route('/levels', methods=['GET'])
def get_levels():
  req = '/levels GET'
  current_app.logger.req(req)

  levels = LevelService.get_all_levels()
  if levels:
    current_app.logger.req_ok(req)
    return jsonify([level.to_dict() for level in levels])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Levels not found'}), 404

@levels_blueprint.route('/levels', methods=['POST'])
def add_level():
  req = '/levels POST'
  current_app.logger.req(req)

  level_data = request.json
  current_app.logger.log_info('info', f'level_data : {level_data}')

  new_level = LevelService.add_level(level_data)
  current_app.logger.req_ok(req)
  return jsonify(new_level.to_dict()), 201


@levels_blueprint.route('/levels/<level>', methods=['GET'])
def get_level_by_name(level):
  req = '/levels GET'
  current_app.logger.req(req)
  current_app.logger.log_info('info', f'level : {level}')

  level_obj = LevelService.get_one_level(level)
  if level_obj:
    current_app.logger.req_ok(req)
    return jsonify(level_obj.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Level not found'}), 404

@levels_blueprint.route('/levels/<level>/reward', methods=['POST'])
def add_reward(level):
  req = f'/levels/{level}/reward POST'
  current_app.logger.req(req)

  reward_data = request.json
  current_app.logger.log_info('info', f'reward_data : {reward_data}')

  level = LevelService.add_reward(level, reward_data)
  if level:
    current_app.logger.req_ok(req)
    return jsonify(level.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Level not found'}), 404


@levels_blueprint.route('/levels/newrewards', methods=['GET'])
def set_new_rewards():
  req = '/levels/newrewards GET'
  current_app.logger.req(req)

  levels = LevelService.set_new_reward_types()
  if levels:
    current_app.logger.req_ok(req)
    return jsonify(levels)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Levels not found'}), 404

@levels_blueprint.route('/levels/gear', methods=['GET'])
def get_level_by_gear():
  req = '/levels/gear GET'
  current_app.logger.req(req)
  item = request.json.get('item', None)
  quality = request.json.get('quality', None)
  current_app.logger.log_info('info', f'item : {item}, quality: {quality}')
  levels = LevelService.get_level_by_gear(item, quality)
  if levels:
    current_app.logger.req_ok(req)
    return jsonify(levels)
  current_app.logger.req_404(req)
  return jsonify({'error': 'Level or gear not found'}), 404