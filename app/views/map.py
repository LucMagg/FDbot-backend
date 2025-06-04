from flask import Blueprint, jsonify, request, current_app
from app.services.map import MapService

map_blueprint = Blueprint('map', __name__)


@map_blueprint.route('/map', methods=['POST'])
def add_map():
  map_data = request.json
  new_map = MapService.create_map(map_data)
  return jsonify(new_map), 201


@map_blueprint.route('/map/<map>', methods=['GET'])
def get_map(map):
  map_obj = MapService.get_one_map(map)
  if map_obj:
    return jsonify(map_obj)
  return jsonify({'error': 'Map not found'}), 404


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


@map_blueprint.route('/map', methods=['PUT'])
def update_map():
  req = '/map PUT'
  current_app.logger.req(req)
  map_data = request.json
  update_map = MapService.update_map(map_data)
  if update_map:
    current_app.logger.req_ok(req)
    return jsonify(update_map), 200  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Map not found'}), 204