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


@spireData_blueprint.route('/spiredata/add', methods=['POST'])
def add_spireData():
  req = '/spiredata/add POST'
  current_app.logger.req(req)
  spire_data = request.json
  spire = SpireDataService.add_SpireData(spire_data)
  if spire:
    current_app.logger.req_ok(req)
    try:
      return jsonify(spire.to_dict())
    except:
      return jsonify(spire)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Problem while adding spire data'}), 404

@spireData_blueprint.route('/spiredata/extract', methods=['POST'])
def extract_spireData():
  req = '/spiredata/extract POST'
  current_app.logger.req(req)
  spire_data = request.json
  spire = SpireDataService.extract_SpireData(spire_data)
  if spire:
    current_app.logger.req_ok(req)
    try:
      return jsonify(spire.to_dict())
    except:
      return jsonify(spire)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Problem while extracting spire data'}), 404

@spireData_blueprint.route('/spiredata/guilds', methods=['GET'])
def get_guilds():
  req = '/spiredata/guilds GET'
  current_app.logger.req(req)
  guilds = SpireDataService.get_guilds()
  if guilds:
    current_app.logger.req_ok(req)
    return jsonify(guilds)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'No guilds found'}), 404