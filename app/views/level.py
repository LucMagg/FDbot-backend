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

  level_data = request.json or {}
  current_app.logger.log_info('info', f'level_data : {level_data}')

  new_level = LevelService.add_level(level_data)
  current_app.logger.req_ok(req)
  return jsonify(new_level.to_dict()), 201


@levels_blueprint.route('/level', methods=['GET'])
def get_level():
  req = '/level GET'
  current_app.logger.req(req)
  payload = request.json or {}
  level_slug = payload.get('level')
  current_app.logger.log_info('info', f'level_slug : {level_slug}')

  if not level_slug:
    return jsonify({'error': 'level missing'}), 400

  level_obj = LevelService.get_one_level(level_slug)
  if level_obj:
    current_app.logger.req_ok(req)
    return jsonify(level_obj.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Level not found'}), 404


@levels_blueprint.route('/level/reward', methods=['POST'])
def add_reward():
  req = f'/level/reward POST'
  current_app.logger.req(req)

  payload  = request.json or {}
  level_slug = payload.get('level')
  current_app.logger.log_info('info', f'level_slug : {level_slug}')
  reward_data = payload.get('reward')
  current_app.logger.log_info('info', f'reward_data : {reward_data}')

  if not level_slug or not reward_data:
    return jsonify({'error': 'level or reward missing'}), 400

  level_obj = LevelService.add_reward(level_slug, reward_data)
  if level_obj:
    current_app.logger.req_ok(req)
    return jsonify(level_obj.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Level not found'}), 404


@levels_blueprint.route('/levels/gear', methods=['GET'])
def get_level_by_gear():
  req = '/levels/gear GET'
  current_app.logger.req(req)

  payload = request.json or {}
  item = payload.get('item')
  quality = payload.get('quality')
  lang = payload.get('lang', 'en')
  current_app.logger.log_info('info', f'item : {item}, quality: {quality}, lang: {lang}')

  if not item:
    return jsonify({'error': 'item missing'}), 400
  
  levels = LevelService.get_level_by_gear(item, quality, lang)
  if levels:
    current_app.logger.req_ok(req)
    return jsonify(levels)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Level or gear not found'}), 404