from flask import Blueprint, jsonify, current_app
from app.services.heroXp import HeroXpService

heroXp_blueprint = Blueprint('heroXp', __name__)

@heroXp_blueprint.route('/heroXp', methods=['GET'])
def get_heroXp():
  req = '/heroXp GET'
  current_app.logger.req(req)
  heroXp = HeroXpService.get_heroXp()
  if heroXp:
    current_app.logger.req_ok(req)
    return jsonify([xp.to_dict() for xp in heroXp])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'heroXp not found'}), 404