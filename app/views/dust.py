from flask import Blueprint, jsonify, request, current_app
from app.services.dust import DustService

dust_blueprint = Blueprint('dust', __name__)


@dust_blueprint.route('/dust', methods=['POST'])
def add_dust():
  dust_data = request.json
  new_dust = DustService.create_dust(dust_data)
  return jsonify(new_dust.to_dict()), 201


@dust_blueprint.route('/dust/<dust>', methods=['GET'])
def get_dust(dust):
  dust_obj = DustService.get_one_dust(dust)
  if dust_obj:
    return jsonify(dust_obj.to_dict())
  return jsonify({'error': 'Dust not found'}), 404


@dust_blueprint.route('/dust', methods=['GET'])
def get_dusts():
  req = '/dust GET'
  current_app.logger.req(req)
  dusts = DustService.get_all_dusts()
  if dusts:
    current_app.logger.req_ok(req)
    return jsonify([dust.to_dict() for dust in dusts])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Dusts not found'}), 404