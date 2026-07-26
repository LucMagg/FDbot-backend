from flask import Blueprint, jsonify, request, current_app
from app.services.traprole import TrapRoleService

traprole_blueprint = Blueprint('traprole', __name__)


@traprole_blueprint.route('/traprole', methods=['POST'])
def add_traprole():
  req = '/traprole POST'
  current_app.logger.req(req)
  traprole_data = request.json
  new_traprole = TrapRoleService.create_traprole(traprole_data)
  if new_traprole:
    current_app.logger.req_ok(req)
    return jsonify(new_traprole.to_dict()), 201
  current_app.logger.req_404(req)
  return jsonify({'error': 'TrapRole not added'}), 404


@traprole_blueprint.route('/traprole/<traprole>', methods=['GET'])
def get_traprole(traprole):
  traprole_obj = TrapRoleService.get_one_traprole(traprole)
  if traprole_obj:
    return jsonify(traprole_obj.to_dict())
  return jsonify({'error': 'TrapRole not found'}), 404


@traprole_blueprint.route('/traprole', methods=['GET'])
def get_traproles():
  req = '/traprole GET'
  current_app.logger.req(req)
  traproles = TrapRoleService.get_all_traproles()
  if traproles:
    current_app.logger.req_ok(req)
    return jsonify([traprole.to_dict() for traprole in traproles])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'TrapRoles not found'}), 404

@traprole_blueprint.route('/traprole', methods=['PUT'])
def update_traprole():
  req = '/traprole PUT'
  current_app.logger.req(req)
  traprole_data = request.json
  current_app.logger.log_info('info', traprole_data)
  traprole = TrapRoleService.update_traprole(traprole_data)
  if traprole:
    current_app.logger.req_ok(req)
    return jsonify({'message': f'TrapRole of guild {traprole_data.get('guild_id')} updated'}), 200
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'TrapRole not found'}), 404

@traprole_blueprint.route('/traprole', methods=['DELETE'])
def delete_traprole():
  req = '/traprole DELETE'
  current_app.logger.req(req)
  traprole_data = request.json
  current_app.logger.log_info('info', traprole_data)
  traprole = TrapRoleService.delete_traprole(traprole_data)
  if traprole:
    current_app.logger.req_ok(req)
    return jsonify({'message': f'TrapRole of guild {traprole_data.get('guild_id')} deleted'}), 200
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'TrapRole not found'}), 404