from flask import Blueprint, jsonify, request
from app.services.update import UpdateService

update_blueprint = Blueprint('update', __name__)


@update_blueprint.route('/update', methods=['GET'])
def get_update():
  update_type = request.args.get('type')

  match update_type:
    case 'hero'|'pet'|'talent':
      update_return = UpdateService.update_one(update_type)
    case _:
      update_type = 'all'
      update_return = UpdateService.update_all()
  
  if update_return:
    return jsonify({'message': f"Update {update_type} OK"}), 200
  return jsonify({'error': 'Type of update not found'}), 404