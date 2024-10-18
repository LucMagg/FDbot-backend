from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.rewardType import RewardType


class RewardTypeService:

  @staticmethod
  def create_reward_type(reward_type_data):
    reward_type = RewardType.from_dict(reward_type_data)
    return reward_type.create(current_app.mongo_db)

  @staticmethod
  def get_one_reward_type(reward_type_name_or_id):
    try:
      reward_type_obj = RewardType.read_by_id(current_app.mongo_db, ObjectId(reward_type_name_or_id))
      return reward_type_obj if reward_type_obj else None
    except InvalidId:
      pass

    reward_type_obj = RewardType.read_by_name(current_app.mongo_db, reward_type_name_or_id)
    return reward_type_obj if reward_type_obj else None
  
  @staticmethod
  def get_all_reward_types():
    return RewardType.read_all(current_app.mongo_db)