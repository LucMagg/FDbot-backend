from flask import Blueprint, jsonify, request, current_app
from app.services.spireConfig import SpireConfigService

channel_blueprint = Blueprint('channel', __name__)


@channel_blueprint.route('/channel', methods=['POST'])
def add_channel():
  req = '/channel POST'
  current_app.logger.req(req)
  channel_data = request.json
  new_channel_id = channel_data.get('channel_id')
  type = channel_data.get('type')
  if not new_channel_id or not type:
    return jsonify({'error': 'No channel_id or type in request'}), 400
  current_app.logger.log_info('info', f'channel_id: {new_channel_id} / type: {type}')
  channels = SpireConfigService.add_channel(new_channel_id, type)
  if not channels:
    current_app.logger.req_404(req)
    return jsonify({'error': 'Channels not found'}), 404
  current_app.logger.req_ok(req)
  return jsonify(channels), 201

@channel_blueprint.route('/channel', methods=['GET'])
def get_channels():
  req = '/channel GET'
  current_app.logger.req(req)
  channels = SpireConfigService.get_all_channels()
  if channels:
    current_app.logger.req_ok(req)
    return jsonify(channels), 200
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Channels not found'}), 404