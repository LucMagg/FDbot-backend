from flask import Blueprint, jsonify, request, current_app
from app.services.talent import TalentService

talent_blueprint = Blueprint('talent', __name__)


@talent_blueprint.route('/talent', methods=['POST'])
def add_talent():
  talent_data = request.json
  new_talent = TalentService.create_talent(talent_data)
  return jsonify(new_talent.to_dict()), 201


@talent_blueprint.route('/talent/<talent>', methods=['GET'])
def get_talent(talent):
  req = '/talent GET'
  current_app.logger.req(req)

  talent_obj = TalentService.get_one_talent(talent)
  current_app.logger.log_info('info', f'talent : {talent}')

  if talent_obj:
    current_app.logger.req_ok(req)
    return jsonify(talent_obj.to_dict())
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Talent not found'}), 404


@talent_blueprint.route('/talent', methods=['GET'])
def get_talents():
  req = '/talent GET'
  current_app.logger.req(req)

  talents = TalentService.get_all_talents()
  if talents:
    current_app.logger.req_ok(req)
    return jsonify([talent.to_dict() for talent in talents])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Talents not found'}), 404
