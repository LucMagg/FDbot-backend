from flask import Blueprint, jsonify, request, current_app
from app.services.gear import GearService

gear_blueprint = Blueprint('gear', __name__)


@gear_blueprint.route('/gear', methods=['GET'])
def get_gear():
  req = '/gear GET'
  current_app.logger.req(req)

  type = request.args.get('type', None)
  position = request.args.get('position', None)

  if type:
    if ',' in type:
      type = type.split(',')
      type = [t.capitalize() for t in type]
      if 'Melee' in type:
        type.append('Melee/Ranged')
    if type == 'Melee':
      type = ['Melee', 'Melee/Ranged']
    current_app.logger.log_info('info', f'type(s) : {type}')
    
  if position:
    if ',' in position:
      splitted_positions = position.split(',')
      position = []
      for p in splitted_positions:
        if '-' in p:
          bug_fix = p.split('-')
          p = '-'.join([b.capitalize() for b in bug_fix])
        else:
          p = p.capitalize()
        position.append(p)

      current_app.logger.log_info('info', f'position(s) : {position}')

  gear_data = GearService.get_gear(type, position)
  
  if gear_data:
    current_app.logger.req_ok(req)
    return gear_data, 200
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Gear not found'}), 404

@gear_blueprint.route('/gear/all', methods=['GET'])
def get_all_gear():
  req = '/gear/all GET'
  current_app.logger.req(req)
  gear_data = GearService.get_all_gear()

  if gear_data:
    current_app.logger.req_ok(req)
    return list(gear_data)[0]['gears'], 200
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Gears not found'}), 404