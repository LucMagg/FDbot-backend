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

@spire_blueprint.route('/spire/add_message_id', methods=['POST'])
def add_message_id():
  req = '/spire/add_message_id POST'
  current_app.logger.req(req)
  data = request.json
  if 'ranking_message_id' in data.keys():
    spire = SpireService.add_ranking_message_id_to_channel(data)
  elif 'climb_details_message_id' in data.keys():
    spire = SpireService.add_climb_details_message_id_to_channel(data)
  else:
    current_app.logger.req_404(req)
    return jsonify({'error': 'bad json (no ranking_message_id or climb_detail_message_id)'}), 404
  if spire:
    current_app.logger.req_ok(req)
    return jsonify(spire.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Spire not found'}), 404

@spire_blueprint.route('/spire/del_message_id', methods=['DELETE'])
def delete_message_id():
  req = '/spire/del_message_id DELETE'
  current_app.logger.req(req)
  data = request.json
  if 'ranking_message_id' in data.keys():
    spire = SpireService.delete_ranking_message_id_from_channel(data)
  elif 'climb_details_message_id' in data.keys():
    spire = SpireService.delete_climb_details_message_id_from_channel(data)
  else:
    current_app.logger.req_404(req)
    return jsonify({'error': 'bad json (no ranking_message_id or climb_detail_message_id)'}), 404
  if spire:
    current_app.logger.req_ok(req)
    return jsonify(spire.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Spire not found'}), 404

@spire_blueprint.route('/spire/add_climb_details', methods=['POST'])
def add_climb_details():
  req = '/spire/add_climb_details POST'
  current_app.logger.req(req)
  data = request.json
  date = data.get('date')
  climb_details = data.get('climb_details')
  spire = SpireService.add_climb_details(date, climb_details)
  if spire:
    current_app.logger.req_ok(req)
    return jsonify(spire.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Spire or climb not found'}), 404