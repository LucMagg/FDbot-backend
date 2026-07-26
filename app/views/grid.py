from flask import Blueprint, jsonify, current_app
from app.services.grid import GridService

grid_blueprint = Blueprint('grid', __name__)


@grid_blueprint.route('/grid', methods=['GET'])
def get_grids():
  req = '/grid GET'
  current_app.logger.req(req)

  grids = GridService.get_all_grids()
  if grids:
    current_app.logger.req_ok(req)
    return jsonify([grid.to_dict() for grid in grids])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Grids not found'}), 404