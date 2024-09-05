from flask import current_app
from bson.objectid import ObjectId
from app.models.reward import Reward

class RewardService:

  @staticmethod
  def create_reward(reward_data):
    reward = Reward.from_dict(reward_data)
    return reward.create(current_app.mongo_db)

  @staticmethod
  def get_one_reward_by_id(reward_id):
    reward_obj = Reward.read_by_id(current_app.mongo_db, ObjectId(reward_id))
    return reward_obj if reward_obj else None

  @staticmethod
  def get_one_reward(reward_name, reward_floor, reward_number):
    reward_obj = Reward.read_by_reward(current_app.mongo_db, reward_name, reward_floor, reward_number)
    return reward_obj if reward_obj else None

  @staticmethod
  def get_all_rewards():
    return Reward.read_all(current_app.mongo_db)