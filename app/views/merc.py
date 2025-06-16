from flask import Blueprint, jsonify, request, current_app
from app.services.merc import MercService

merc_blueprint = Blueprint('merc', __name__)


@merc_blueprint.route('/merc', methods=['POST'])
def add_merc():
  req = '/merc POST'
  current_app.logger.req(req)
  merc_data = request.json
  new_merc = MercService.create_or_update_user(merc_data)
  if new_merc:
    current_app.logger.req_ok(req)
    return jsonify(new_merc.to_dict()), 201
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Error while creating/updating merc'}), 404


@merc_blueprint.route('/merc', methods=['GET'])
def get_mercs():
  merc_data = None
  if request.is_json and request.get_json(silent=True):
    merc_data = request.get_json()
  if merc_data:
    if 'user' in merc_data.keys():
      req = '/merc GET user mercs list'
      current_app.logger.req(req)
      result = MercService.get_user(merc_data.get('user'))
      if result:
        current_app.logger.req_ok(req)
        return jsonify(result.to_dict()), 200
      return jsonify({'error': 'Error user not found'}), 404
    elif 'merc' in merc_data.keys():
      req = '/merc GET users by merc'
      current_app.logger.req(req)
      result = MercService.get_users_by_merc(merc_data.get('merc'))
      if result:
        current_app.logger.req_ok(req)
        return jsonify(result), 200
      return jsonify({'error': 'Error merc not found'}), 404
  else:
    req = '/merc GET all merc users'
    current_app.logger.req(req)
    result = MercService.get_all_users()
    if result:
      current_app.logger.req_ok(req)
      return jsonify([r for r in result]), 200
    return jsonify({'error': 'Error no user found'}), 404
    
  current_app.logger.req_404(req)
  return jsonify({'error': 'Bad request'}), 400


@merc_blueprint.route('/mercs', methods=['GET'])
def get_all_mercs():
  req = '/mercs GET'
  current_app.logger.req(req)
  mercs = MercService.get_all_mercs()
  if mercs:
    current_app.logger.req_ok(req)
    return jsonify(mercs), 200
  return jsonify({'error': 'Error mercs not found'}), 404