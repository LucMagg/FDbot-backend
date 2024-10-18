from bson import ObjectId
from typing import Dict, Optional, List, Union
from app.utils.strUtils import str_to_slug


class Choice:
  def __init__(self, name: str, grade: int, icon: Optional[str] = '', choices: Optional[Union[str, List['Choice']]] = None):
    self.name = name
    self.icon = icon
    self.choices = choices
    self.grade = grade

  @classmethod
  def from_dict(cls, data: Dict):
    if not data:
      return None
     
    choices_data = data.get('choices')
    choices = None
    if isinstance(choices_data, list):
      choices = [Choice.from_dict(choice) for choice in choices_data if isinstance(choice, dict)]
    elif isinstance(choices_data, str):
      choices = choices_data

    return cls(
      name = data.get('name'),
      icon = data.get('icon', ''),
      grade = data.get('grade'),
      choices = choices
    )

  def to_dict(self) -> Dict:
    to_return = {
      "name": self.name,
      "icon": self.icon,
      "grade": self.grade
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
        resolved_choices = [Choice.from_dict(choice) for choice in reward_choice.get('choices', [])]
        self.choices = resolved_choices
    elif isinstance(self.choices, list):
      resolved_choices = []
      for choice in self.choices:
        if isinstance(choice.choices, str):
          choice = choice.resolve_choices(db)
        resolved_choices.append(choice)
      self.choices = sorted(resolved_choices, key=lambda k: k.grade)
    return self


class RewardType:
  def __init__(self, name: str, name_slug: str, grade: int, has_quantity: bool, _id: Optional[str] = None, icon: Optional[str] = None, choices: List[Choice] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.name_slug = name_slug
    self.grade = grade
    self.icon = icon or ''
    self.has_quantity = has_quantity
    self.choices = choices or []

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name'),
      name_slug = data.get('name_slug') if data.get('name_slug') is not None else str_to_slug(data.get('name')),
      grade = data.get('grade'),
      icon = data.get('icon', ''),
      has_quantity = data.get('has_quantity'),
      choices = [Choice.from_dict(choice) for choice in data.get('choices', [])]
    )

  def to_dict(self) -> Dict:
    reward_type = {
      "name": self.name,
      "name_slug": self.name_slug,
      "grade": self.grade,
      "icon": self.icon,
      "has_quantity": self.has_quantity,
      "choices": [choice.to_dict() for choice in self.choices]
    }
    if self._id:
      reward_type["_id"] = str(self._id)
    return reward_type
  
  def resolve_choices(self, db):
    resolved_choices = []
    for choice in self.choices:
      resolved_choice = choice.resolve_choices(db)
      resolved_choices.append(resolved_choice)
    self.choices = resolved_choices
    return self

  def create(self, db):
    if not self._id:
      result = db.rewardTypes.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.rewardTypes.update_one({"_id": self._id}, {"$set": self.to_dict()})
    return self  

  @staticmethod
  def read_by_id(db, reward_type_id):
    data = db.rewardTypes.find_one({"_id": ObjectId(reward_type_id)})
    return RewardType.from_dict(data).resolve_choices(db) if data else None
  
  @staticmethod
  def read_by_name(db, reward_type_name):
    data = db.rewardTypes.find_one({"name": reward_type_name})
    return RewardType.from_dict(data).resolve_choices(db) if data else None

  @staticmethod
  def read_all(db):
    data = db.rewardTypes.find()
    return [RewardType.from_dict(reward_type).resolve_choices(db) for reward_type in data] if data else None
  
  @staticmethod
  def update_by_name(db, reward_type_name, update_data):
    result = db.rewardTypes.update_one({"name": reward_type_name}, {"$set": update_data})
    return result.modified_count if result.modified_count > 0 else None

  @staticmethod
  def update_by_id(db, reward_type_id, update_data):
    result = db.rewardTypes.update_one({"_id": ObjectId(reward_type_id)}, {"$set": update_data})
    return result.modified_count if result.modified_count > 0 else None

  @staticmethod
  def delete_by_name(db, reward_type_name):
    result = db.rewardTypes.delete_one({"name": reward_type_name})
    return result.deleted_count if result.deleted_count > 0 else None
  
  @staticmethod
  def delete_by_id(db, reward_type_id):
    result = db.rewardTypes.delete_one({"_id": ObjectId(reward_type_id)})
    return result.deleted_count if result.deleted_count > 0 else None