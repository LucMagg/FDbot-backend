from bson import ObjectId
from typing import Dict, Optional, List

from .reward import Reward, GoldReward, PotionsReward, GearReward, DustReward
from ..utils.strUtils import str_to_slug


class Level:
  def __init__(self, name: str, cost: int, rewards: List[Reward], _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.cost = cost
    self.rewards = rewards

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = str_to_slug(data.get('name')),
      cost= data.get('cost'),
      rewards = [Level.create_reward(reward_data) for reward_data in data.get('rewards', []) if
               isinstance(reward_data, dict)]
    )

  def to_dict(self) -> Dict:
    rewards = [reward.to_dict() for reward in self.rewards] if self.rewards else []
    rewards = sorted(rewards, key = lambda r: (-r.get('appearances'), -r.get('quantity')))
    level = {
      "name": self.name,
      "cost": self.cost,
      "rewards": rewards,
    }
    if self._id:
      level["_id"] = str(self._id)

    return level

  def create(self, db):
    existing = self.read_by_level(db, self.name)
    if existing:
      return existing
    result = db.levels.insert_one(self.to_dict())
    self._id = result.inserted_id
    return self

  def add_reward(self, db, reward_data: Dict):
    reward_data['appearances'] = 1
    new_reward = Level.create_reward(reward_data)
    existing_rewards = [existing_reward for existing_reward in self.rewards if existing_reward == new_reward]
    if len(existing_rewards) == 1:
      reward = existing_rewards[0]
      reward.appearances += 1
    elif len(existing_rewards) == 0:
      self.rewards.append(new_reward)
    else:
      return None
    db.levels.update_one({"_id": self._id}, {"$set": {'rewards': [reward.to_dict() for reward in self.rewards]}})
    return self

  def expected_reward(self):
    if len(self.rewards) == 0:
      return 0
    quantities = [reward.quantity for reward in self.rewards]
    return sum(quantities) / len(quantities)

  @staticmethod
  def read_by_name(db, level_name):
    data = db.levels.find_one({"name_slug": str_to_slug(level_name)})
    return Level.from_dict(data) if data else None

  @staticmethod
  def read_by_level(db, level_name):
    data = db.levels.find_one({"name": str_to_slug(level_name)})
    return Level.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    return [Level.from_dict(level) for level in db.levels.find()]

  @staticmethod
  def create_reward(reward_data):
    factories = {
      "gold": GoldReward,
      "potions": PotionsReward,
      "gear": GearReward,
      "dust": DustReward
    }
    return factories[reward_data['type']](reward_data)