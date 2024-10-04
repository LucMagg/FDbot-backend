from bson import ObjectId
from typing import Dict, Optional, List, Union

from .reward import Reward, GoldReward, PotionsReward, GearReward, DustReward
from ..utils.strUtils import str_to_slug
  

class RewardChoice:
  def __init__(self, type: str, qualities: Optional[List[str]] = None, positions: Optional[List[str]] = None, item_types: Optional[List[str]] = None):
    self.type = type
    self.qualities = qualities or []
    self.positions = positions or []
    self.item_types = item_types or []

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      type = data.get('type'),
      qualities = [qualities_data.get('name') for qualities_data in data.get('qualities', []) if isinstance(qualities_data, dict)],
      positions = [positions_data.get('name') for positions_data in data.get('positions', []) if isinstance(positions_data, dict)],
      item_types = [item_types_data.get('name') for item_types_data in data.get('item_types', []) if isinstance(item_types_data, dict)]
    )

  def to_dict(self) -> Dict:
    return {
      "type": self.type,
      "qualities": [{'name': quality} for quality in self.qualities],
      "positions": [{'name': position} for position in self.positions],
      "item_types": [{'name': item_type} for item_type in self.item_types]
    }

class Level:
  def __init__(self, name: str, name_slug: str, standard_energy_cost: int, coop_energy_cost: int, rewards : List[Reward], _id: Optional[str] = None, reward_choices: Union[List[RewardChoice], List] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.name_slug = name_slug
    self.standard_energy_cost = standard_energy_cost
    self.coop_energy_cost = coop_energy_cost
    self.reward_choices = reward_choices or []
    self.rewards = rewards

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name'),
      name_slug = data.get('name_slug') if data.get('name_slug') is not None else str_to_slug(data.get('name')),
      standard_energy_cost = data.get('standard_energy_cost'),
      coop_energy_cost = data.get('coop_energy_cost'),
      reward_choices = [RewardChoice.from_dict(reward_choices_data) for reward_choices_data in data.get('reward_choices', []) if isinstance(reward_choices_data, dict)],
      rewards = [Level.create_reward(reward_data) for reward_data in data.get('rewards', []) if
               isinstance(reward_data, dict)]
    )

  def to_dict(self) -> Dict:
    rewards = [reward.to_dict() for reward in self.rewards] if self.rewards else []
    rewards = sorted(rewards, key = lambda r: (-r.get('appearances'), -r.get('quantity')))
    level = {
      "name": self.name,
      "name_slug": self.name_slug,
      "standard_energy_cost": self.standard_energy_cost,
      "coop_energy_cost": self.coop_energy_cost,
      "reward_choices": [possible_reward.to_dict() for possible_reward in self.reward_choices],
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