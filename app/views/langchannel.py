from flask import Blueprint, jsonify, request, current_app
from app.services.langchannel import LangChannelService

langchannel_blueprint = Blueprint('langchannel', __name__)


@langchannel_blueprint.route('/langchannel', methods=['POST'])
def add_langchannel():
  langchannel_data = request.json
  new_langchannel = LangChannelService.create_langchannel(langchannel_data)
  return jsonify(new_langchannel.to_dict()), 201


@langchannel_blueprint.route('/langchannel/<langchannel>', methods=['GET'])
def get_langchannel(langchannel):
  langchannel_obj = LangChannelService.get_one_langchannel(langchannel)
  if langchannel_obj:
    return jsonify(langchannel_obj.to_dict())
  return jsonify({'error': 'LangChannel not found'}), 404


@langchannel_blueprint.route('/langchannel', methods=['GET'])
def get_langchannels():
  req = '/langchannel GET'
  current_app.logger.req(req)
  langchannels = LangChannelService.get_all_langchannels()
  if langchannels:
    current_app.logger.req_ok(req)
    return jsonify([langchannel.to_dict() for langchannel in langchannels])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'LangChannels not found'}), 404

@langchannel_blueprint.route('/langchannel', methods=['PUT'])
def update_langchannel():
  req = '/langchannel PUT'
  current_app.logger.req(req)
  langchannel_data = request.json
  current_app.logger.log_info('info', langchannel_data)
  langchannel = LangChannelService.update_langchannel(langchannel_data)
  if langchannel:
    current_app.logger.req_ok(req)
    return jsonify({'message': f'LangChannel {langchannel_data.get('channel_id')} updated'}), 200
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'LangChannel not found'}), 404

@langchannel_blueprint.route('/langchannel', methods=['DELETE'])
def delete_langchannel():
  req = '/langchannel DELETE'
  current_app.logger.req(req)
  langchannel_data = request.json
  current_app.logger.log_info('info', langchannel_data)
  langchannel = LangChannelService.delete_langchannel(langchannel_data)
  if langchannel:
    current_app.logger.req_ok(req)
    return jsonify({'message': f'LangChannel {langchannel_data.get('channel_id')} deleted'}), 200
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'LangChannel not found'}), 404