from flask import Blueprint, jsonify, request, current_app
from app.services.replay import ReplayService

replays_blueprint = Blueprint('replays', __name__)

@replays_blueprint.route('/replays', methods=['GET'])
def get_events():
  req = '/replays GET'
  current_app.logger.req(req)

  event_names = ReplayService.get_all_event_names()

  if event_names:
    current_app.logger.req_ok(req)
    return jsonify(event_names)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Event replays not found'}), 404

@replays_blueprint.route('/replays', methods=['POST'])
def add_replay():
  req = '/replays POST'
  current_app.logger.req(req)

  replay_data = request.json
  current_app.logger.log_info('info', f'replay_data : {replay_data}')

  new_replay = ReplayService.add_replay(replay_data)
  current_app.logger.req_ok(req)
  return jsonify(new_replay.to_dict()), 201


@replays_blueprint.route('/replays/<event>', methods=['GET'])
def get_event_replays_by_level_name(event):
  level = request.args.get('level')
  req = '/levels GET'
  current_app.logger.req(req)
  current_app.logger.log_info('info', f'event: {event}, level: {event}')

  replays = ReplayService.get_replays_for_event_level(event, level)
  if replays:
    current_app.logger.req_ok(req)
    return jsonify(replays)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Level not found'}), 404
