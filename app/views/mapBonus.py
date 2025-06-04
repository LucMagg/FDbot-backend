from flask import Blueprint, jsonify, current_app
from app.services.spireConfig import SpireConfigService

map_bonus_blueprint = Blueprint('map_bonus', __name__)

@map_bonus_blueprint.route('/map_bonus', methods=['GET'])
def get_map_bonuses():
  req = '/map_bonus GET'
  current_app.logger.req(req)
  map_bonuses = SpireConfigService.get_all_map_bonuses()
  if map_bonuses:
    current_app.logger.req_ok(req)
    return jsonify(map_bonuses), 200
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Map bonuses not found'}), 404