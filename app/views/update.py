from flask import Blueprint, jsonify, request, current_app
from app.services.update import UpdateService

update_blueprint = Blueprint('update', __name__)


@update_blueprint.route('/update', methods=['GET'])
def get_update():
  req = '/update GET'
  current_app.logger.req(req)

  update_type = request.args.get('type')
  current_app.logger.log_info('info', f'type : {type}')

  if update_type == 'all':
    update_type = None
  update_return = UpdateService.update(update_type)
  
  if update_return:
    current_app.logger.req_ok(req)
    return jsonify({'message': f"Update {update_type} OK"}), 200
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Type of update not found'}), 404