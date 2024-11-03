from flask import Blueprint, jsonify, request, current_app
from app.services.spire import SpireService

spire_blueprint = Blueprint('spire', __name__)


@spire_blueprint.route('/spire', methods=['GET'])
def get_spire():
  req = '/spire GET'
  current_app.logger.req(req)
  spire_date = request.json
  print(spire_date)
  spire_obj = SpireService.get_one_spire(spire_date)
  
  if spire_obj:
    current_app.logger.req_ok(req)
    return jsonify(spire_obj.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Spire not found'}), 404


@spire_blueprint.route('/spires', methods=['GET'])
def get_spires():
  req = '/spires GET'
  current_app.logger.req(req)
  spires = SpireService.get_all_spires()
  if spires:
    current_app.logger.req_ok(req)
    return jsonify([spire.to_dict() for spire in spires])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Spires not found'}), 404

@spire_blueprint.route('/spire/add_channel', methods=['POST'])
def add_channel():
  req = '/spire/add_channel POST'
  current_app.logger.req(req)
  data = request.json
  spire = SpireService.add_channel_to_spire(data)
  if spire:
    current_app.logger.req_ok(req)
    return jsonify(spire.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Spire not found'}), 404