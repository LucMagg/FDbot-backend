from flask import Blueprint, jsonify, request, current_app
from app.services.spireData import SpireDataService

spireData_blueprint = Blueprint('spireData', __name__)


@spireData_blueprint.route('/spiredata/user', methods=['GET'])
def get_spire():
  req = '/spiredata/user GET'
  current_app.logger.req(req)
  data = request.json
  current_app.logger.log_info('info', f'username : {data.get('username')}')
  spires = SpireDataService.get_spireDatas_by_username(data.get('username'))
  if spires:
    current_app.logger.req_ok(req)
    return jsonify([spire.to_dict() for spire in spires])
  current_app.logger.req_404(req)
  return jsonify({'error': 'SpireData not found'}), 404

@spireData_blueprint.route('/spiredatas/best/<how_many>', methods=['GET'])
def get_best_spireDatas(how_many):
  req = '/spiredatas/best GET'
  current_app.logger.req(req)
  spires = SpireDataService.get_spireDatas_by_best_scores(int(how_many))
  if spires:
    current_app.logger.req_ok(req)
    return jsonify([spire.to_dict() for spire in spires])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'SpireDatas not found'}), 404


@spireData_blueprint.route('/spiredatas', methods=['GET'])
def get_all_spireDatas():
  req = '/spiredatas GET'
  current_app.logger.req(req)
  spires = SpireDataService.get_all_spireDatas()
  if spires:
    current_app.logger.req_ok(req)
    return jsonify([spire.to_dict() for spire in spires])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'SpireDatas not found'}), 404


@spireData_blueprint.route('/spiredata', methods=['POST'])
def add_spireData():
  req = '/spiredata POST'
  current_app.logger.req(req)
  spire_data = request.json
  print(spire_data)
  added_spire = SpireDataService.post_SpireData(spire_data)
  if added_spire:
    current_app.logger.req_ok(req)
    return jsonify(added_spire.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Problem while adding spiredata'}), 404