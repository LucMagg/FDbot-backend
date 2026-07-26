from flask import Blueprint, jsonify, current_app
from app.services.map import MapService

map_blueprint = Blueprint('map', __name__)


@map_blueprint.route('/map', methods=['GET'])
def get_maps():
  req = '/map GET'
  current_app.logger.req(req)

  maps = MapService.get_all_maps()
  if maps:
    current_app.logger.req_ok(req)
    return jsonify([map.to_dict() for map in maps])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Maps not found'}), 404