from flask import Blueprint, jsonify, request
from app.services.talent import TalentService

talent_blueprint = Blueprint('talent', __name__)


@talent_blueprint.route('/talent', methods=['POST'])
def add_talent():
  talent_data = request.json
  new_talent = TalentService.create_talent(talent_data)
  return jsonify(new_talent.to_dict()), 201


@talent_blueprint.route('/talent/<talent>', methods=['GET'])
def get_talent(talent):
  talent_obj = TalentService.get_one_talent(talent)
  if talent_obj:
    return jsonify(talent_obj.to_dict())
  return jsonify({'error': 'Talent not found'}), 404


@talent_blueprint.route('/talent', methods=['GET'])
def get_talents():
  talents = TalentService.get_all_talents()
  if talents:
    return jsonify([talent.to_dict() for talent in talents])
  return jsonify({'error': 'Talents not found'}), 404
