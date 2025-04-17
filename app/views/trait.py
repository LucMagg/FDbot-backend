from flask import Blueprint, jsonify, request, current_app
from app.services.trait import TraitService

trait_blueprint = Blueprint('trait', __name__)


@trait_blueprint.route('/trait', methods=['GET'])
def get_traits():
  req = '/trait GET'
  current_app.logger.req(req)

  traits = TraitService.get_all_traits()
  if traits:
    current_app.logger.req_ok(req)
    return jsonify([trait.to_dict() for trait in traits])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Talents not found'}), 404