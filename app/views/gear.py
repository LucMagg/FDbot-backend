from flask import Blueprint, jsonify, request
from app.services.gear import GearService

gear_blueprint = Blueprint('gear', __name__)


@gear_blueprint.route('/gear', methods=['GET'])
def get_gear():
  type = request.args.get('type', None)
  position = request.args.get('position', None)

  if type:
    if ',' in type:
      type = type.split(',')
  if position:
    if ',' in position:
      position = position.split(',')

  print(type)
  print(position)

  gear_data = GearService.get_gear(type, position)
  if gear_data:
    return gear_data, 200
  return jsonify({'error': 'Gear not found'}), 404

@gear_blueprint.route('/gear/all', methods=['GET'])
def get_all_gear():
  gear_data = GearService.get_all_gear()

  if gear_data:
    return list(gear_data)[0]['gears'], 200
  return jsonify({'error': 'Gear not found'}), 404