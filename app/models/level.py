from bson import ObjectId
from typing import Dict, Optional, List, Union

from app.utils.strUtils import str_to_slug
from app.models.rewardType import RewardType


from app.models.reward import Reward, GoldReward, PotionsReward, GearReward, DustReward
from collections import defaultdict
  


class Detail:
  def __init__(self, quantity: Optional[int] = None, appearances: Optional[int] = None, item: Optional[str] = None):
    self.quantity = quantity if quantity else None
    self.appearances = appearances if appearances else None
    self.item = item if item else None

  @classmethod
  def from_dict(cls, data: Dict):
    if not data:
      return None

    return cls(
      quantity = data.get('quantity', None),
      appearances = data.get('appearances', None),
      item = data.get('item', None)
    )
  
  def to_dict(self) -> Dict:
    return {
      "quantity": self.quantity,
      "appearances": self.appearances,
      "item": self.item
    }


class Reward:
  def __init__(self, type: str, details: List['Detail'], total_appearances: Optional[int] = 1, quality: Optional[str] = None):
    self.total_appearances = total_appearances or 1
    self.type = type
    self.quality = quality or None
    self.details = details

  @classmethod
  def from_dict(cls, data: Dict):
    if not data:
      return None

    return cls(
      total_appearances = data.get('total_appearances'),
      type = data.get('type'),
      quality = data.get('quality', None),
      details = [Detail.from_dict(detail_data) for detail_data in data.get('details', []) if isinstance(detail_data, dict)]
    )
  
  def to_dict(self) -> Dict:
    details = [detail.to_dict() for detail in self.details]

    details = sorted(details, key = lambda x: (-x.get('appearances')))

    return {
      "total_appearances": self.total_appearances,
      "type": self.type,
      "quality": self.quality,
      "details": details
    }

class RewardChoice:
  def __init__(self, name: str, grade: int, icon: Optional[str] = '', has_quantity: Optional[bool] = None, choices: Optional[Union[List['RewardChoice'], 'RewardChoice']] = []):
    self.name = name
    self.icon = icon
    self.has_quantity = has_quantity
    self.choices = choices
    self.grade = grade

  @classmethod
  def from_dict(cls, data: Dict):
    if not data:
      return None
     
    choices_data = data.get('choices')
    if choices_data is not None:
      choices = [RewardChoice.from_dict(choice) for choice in choices_data if isinstance(choice, dict)]
    else:
      choices = None

    return cls(
      name = data.get('name'),
      icon = data.get('icon', ''),
      grade = data.get('grade'),
      has_quantity = data.get('has_quantity'),
      choices = choices
    )

  def to_dict(self) -> Dict:
    to_return = {
      "name": self.name,
      "icon": self.icon,
      "grade": self.grade,
      "has_quantity": self.has_quantity
    }
    if self.choices is not None:
      if isinstance(self.choices, list):
        to_return["choices"] = [choice.to_dict() for choice in self.choices]
      else:
        to_return["choices"] = self.choices
    return to_return
    
  def resolve_choices(self, db):
    if isinstance(self.choices, str):
      reward_choice = db.rewardChoices.find_one({"name": self.choices})
      if reward_choice:
        resolved_choices = [RewardChoice.from_dict(choice) for choice in reward_choice.get('choices', [])]
        self.choices = resolved_choices
    elif isinstance(self.choices, list):
      resolved_choices = []
      for choice in self.choices:
        if isinstance(choice.choices, str):
          choice = choice.resolve_choices(db)
        resolved_choices.append(choice)
      self.choices = sorted(resolved_choices, key=lambda k: k.grade)
    return self

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
      rewards = [Reward.from_dict(reward_data) for reward_data in data.get('rewards', []) if isinstance(reward_data, dict)]
    )

  def to_dict(self) -> Dict:
    rewards = [reward.to_dict() for reward in self.rewards] if self.rewards else []
    rewards = sorted(rewards, key = lambda r: -r.get('total_appearances'))
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
    existing = self.read_by_name(db, self.name)
    if existing:
      return existing
    result = db.levels.insert_one(self.to_dict())
    self._id = result.inserted_id
    return self

  @staticmethod
  def add_reward(db, level, reward_data: Dict):

    found_reward = next((r for r in level.get('rewards') if r.get('type') == reward_data.get('type') and r.get('quality') == reward_data.get('quality')), None)
    done = False
    if found_reward:
      for detail in found_reward.get('details'):
        if detail.get('quantity') == reward_data.get('quantity') and detail.get('item') == reward_data.get('item'):
          detail['appearances'] += 1
          done = True
      if not done:
        found_reward['details'].append({'appearances': 1, 'item': reward_data.get('item'), 'quantity': reward_data.get('quantity')})
      found_reward['total_appearances'] += 1

    else:
      level.get('rewards').append({
        'type': reward_data.get('type'),
        'quality': reward_data.get('quality'),
        'details': [
          {
            'quantity': reward_data.get('quantity'),
            'item': reward_data.get('item'),
            'appearances': 1
          }
        ],
        'total_appearances': 1
      })

    del level['_id']

    db.levels.update_one({"name": level.get('name')}, {"$set": level})
    return Level.from_dict(level)


  @staticmethod
  def read_by_name(db, level_name):
    data = db.levels.find_one({"name_slug": str_to_slug(level_name)})
    return Level.from_dict(data) if data else None

  @staticmethod
  def read_by_id(db, level_id):
    data = db.levels.find_one({"_id": ObjectId(level_id)})
    return Level.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.levels.find()
    return [Level.from_dict(level) for level in data] if data else None
  
  @staticmethod
  def build_new_levels(db):
    levels = [] #insérer la collection exportée en json pour extraire les levels
    reward_types = [RewardType.to_dict(reward) for reward in RewardType.read_all(db)]

    for level in levels:
      level['reward_choices'] = []
      for reward in level.get('rewards'):
        if reward.get('type') != 'gear' and reward.get('type') != 'dust':
          if not any(reward.get('type') == r.get('name') for r in level['reward_choices']):
            rw = next((rw for rw in reward_types if rw.get('name') == reward.get('type')), None)
            if 'id' in rw.keys():
              del rw['_id']
            level['reward_choices'].append(rw)
    
    for level in levels:
      rewards = level.get('rewards')

      count = []
      for r in rewards:
        if r.get('type') not in count:
          count.append(r.get('type'))
      
      if len(count) == 1:

        result = []
        for r in rewards:
          if not any(rt for rt in result if r.get('type') == rt.get('type')):
            result.append({
              'type': r.get('type'),
              'quality': r.get('quality', None),
              'details': [{'quantity': r.get('quantity'), 'appearances': r.get('appearances')}],
              'total_appearances': r.get('appearances')
            })
          else:
            rt = next((rt for rt in result if r.get('type') == rt.get('type')), None)
            rt.get('details').append({'quantity': r.get('quantity'), 'appearances': r.get('appearances')})
            rt['total_appearances'] += r.get('appearances')
        
      result.sort(key=lambda x: -x['total_appearances'])
      level['rewards'] = result

    to_return = []
    for level in levels:
      if len(level['reward_choices']) > 0:
        if '_id' in level['reward_choices'][0].keys():
          del level['reward_choices'][0]['_id']
        if 'name_slug' in level['reward_choices'][0].keys():
          del level['reward_choices'][0]['name_slug']
        if 'choices' in level['reward_choices'][0].keys():
          del level['reward_choices'][0]['choices']
        to_return.append(level)
    
    return to_return


