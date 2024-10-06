from flask import Blueprint, jsonify, request, current_app
from app.services.rewardType import RewardTypeService

rewardType_blueprint = Blueprint('rewardtype', __name__)


@rewardType_blueprint.route('/rewardtype', methods=['POST'])
def add_rewardType():
  rewardType_data = request.json
  new_rewardType = RewardTypeService.create_reward_type(rewardType_data)
  return jsonify(new_rewardType.to_dict()), 201


@rewardType_blueprint.route('/rewardtype/<rewardtype>', methods=['GET'])
def get_rewardType(rewardtype):
  rewardType_obj = RewardTypeService.get_one_reward_type(rewardtype)
  if rewardType_obj:
    return jsonify(rewardType_obj.to_dict())
  return jsonify({'error': 'RewardType not found'}), 404


@rewardType_blueprint.route('/rewardtype', methods=['GET'])
def get_rewardTypes():
  req = '/rewardType GET'
  current_app.logger.req(req)
  rewardTypes = RewardTypeService.get_all_reward_types()
  if rewardTypes:
    current_app.logger.req_ok(req)
    return jsonify([rewardType.to_dict() for rewardType in rewardTypes])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'RewardTypes not found'}), 404