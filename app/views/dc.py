from flask import Blueprint, jsonify, request, current_app
from app.services.dc import DcService

dc_blueprint = Blueprint('dc', __name__)

@dc_blueprint.route('/dcs', methods=['GET'])
def get_dcs():
  req = '/dcs GET'
  current_app.logger.req(req)

  levels = DcService.get_all_levels()
  if levels:
    current_app.logger.req_ok(req)
    return jsonify([level.to_dict() for level in levels])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Dc levels not found'}), 404


@dc_blueprint.route('/dc', methods=['POST'])
def add_dc():
  req = '/dc POST'
  current_app.logger.req(req)

  dc_data = request.json or {}
  current_app.logger.log_info('info', f'dc_data : {dc_data}')

  dc = DcService.post_dc(dc_data)
  if dc:
    current_app.logger.req_ok(req)
    return jsonify(dc.to_dict()), 201
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Dc level not found'}), 404


@dc_blueprint.route('/dc', methods=['GET'])
def get_dc():
  req = '/dc GET'
  current_app.logger.req(req)
  payload = request.json or {}
  name = payload.get('name')
  current_app.logger.log_info('info', f'dc : {name}')

  if not name:
    return jsonify({'error': 'Dc name missing'}), 400

  level_obj = DcService.get_one_level(name)
  if level_obj:
    current_app.logger.req_ok(req)
    return jsonify(level_obj.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Dc level not found'}), 404


@dc_blueprint.route('/dc', methods=['DELETE'])
def clear_dc():
  req = '/dc DELETE'
  current_app.logger.req(req)
  dc = DcService.clear_dc()
  match dc.get('status'):
    case 200|404:
      current_app.logger.req_ok(req)
      return jsonify({'message': dc.get('message')}), dc.get('status')
    case _:
      current_app.logger.req_404(req)
      return jsonify({'error': dc.get('message')}), dc.get('status')