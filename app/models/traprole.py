from bson import ObjectId
from typing import Dict, Optional


class TrapRole:
  def __init__(self, guild_id: int, role_id: str, _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.guild_id = guild_id
    self.role_id = role_id

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      guild_id = data.get('guild_id'),
      role_id = data.get('role_id'),
    )

  def to_dict(self, include_id: bool = True) -> Dict:
    traprole = {
      'guild_id': self.guild_id,
      'role_id': self.role_id,
    }
    if self._id and include_id:
      traprole['_id'] = str(self._id)
    return traprole

  def create(self, db):
    existing = db.traproles.find_one({'guild_id': self.guild_id})
    if existing:
      self._id = existing['_id']
      db.traproles.update_one({'_id': self._id}, {'$set': self.to_dict(include_id=False)})
    elif not self._id:
      result = db.traproles.insert_one(self.to_dict(include_id=False))
      self._id = result.inserted_id
    else:
      db.traproles.update_one({'_id': self._id}, {'$set': self.to_dict(include_id=False)})
    return self 

  @staticmethod
  def read_by_id(db, traprole_id):
    data = db.traproles.find_one({'_id': ObjectId(traprole_id)})
    return TrapRole.from_dict(data) if data else None
  
  @staticmethod
  def read_by_guild_id(db, traprole_guild_id):
    data = db.traproles.find_one({'guild_id': traprole_guild_id})
    return TrapRole.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.traproles.find()
    return [TrapRole.from_dict(traprole) for traprole in data] if data else None
  
  @staticmethod
  def update_by_guild_id(db, traprole_guild_id, update_data):
    update_dict = {k: v for k, v in update_data.items() if k != '_id'}
    result = db.traproles.update_one({'guild_id': traprole_guild_id}, {'$set': update_dict})
    return result.matched_count if result.matched_count > 0 else None

  @staticmethod
  def update_by_id(db, traprole_id, update_data):
    update_dict = {k: v for k, v in update_data.items() if k != '_id'}
    result = db.traproles.update_one({'_id': ObjectId(traprole_id)}, {'$set': update_dict})
    return result.matched_count if result.matched_count > 0 else None

  @staticmethod
  def delete_by_guild_id(db, traprole_guild_id):
    result = db.traproles.delete_one({'guild_id': traprole_guild_id})
    return result.deleted_count if result.deleted_count > 0 else None
  
  @staticmethod
  def delete_by_id(db, traprole_id):
    result = db.traproles.delete_one({'_id': ObjectId(traprole_id)})
    return result.deleted_count if result.deleted_count > 0 else None