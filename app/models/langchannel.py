from bson import ObjectId
from typing import Dict, Optional, Union, List
from ..utils.strUtils import str_to_slug


class LangChannel:
  def __init__(self, channel_id: int, code: str, _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.channel_id = channel_id
    self.code = code

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      channel_id = data.get('channel_id'),
      code = data.get('code'),
    )

  def to_dict(self, include_id: bool = True) -> Dict:
    langchannel = {
      'channel_id': self.channel_id,
      'code': self.code,
    }
    if self._id and include_id:
      langchannel['_id'] = str(self._id)
    return langchannel

  def create(self, db):
    existing = db.langchannels.find_one({'channel_id': self.channel_id})
    if existing:
      self._id = existing['_id']
      db.langchannels.update_one({'_id': self._id}, {'$set': self.to_dict(include_id=False)})
    elif not self._id:
      result = db.langchannels.insert_one(self.to_dict(include_id=False))
      self._id = result.inserted_id
    else:
      db.langchannels.update_one({'_id': self._id}, {'$set': self.to_dict(include_id=False)})
    return self 

  @staticmethod
  def read_by_id(db, langchannel_id):
    data = db.langchannels.find_one({'_id': ObjectId(langchannel_id)})
    return LangChannel.from_dict(data) if data else None
  
  @staticmethod
  def read_by_channel_id(db, langchannel_channel_id):
    data = db.langchannels.find_one({'channel_id': langchannel_channel_id})
    return LangChannel.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.langchannels.find()
    return [LangChannel.from_dict(langchannel) for langchannel in data] if data else None
  
  @staticmethod
  def update_by_channel_id(db, langchannel_channel_id, update_data):
    update_dict = {k: v for k, v in update_data.items() if k != '_id'}
    result = db.langchannels.update_one({'channel_id': langchannel_channel_id}, {'$set': update_dict})
    return result.matched_count if result.matched_count > 0 else None

  @staticmethod
  def update_by_id(db, langchannel_id, update_data):
    update_dict = {k: v for k, v in update_data.items() if k != '_id'}
    result = db.langchannels.update_one({'_id': ObjectId(langchannel_id)}, {'$set': update_dict})
    return result.matched_count if result.matched_count > 0 else None

  @staticmethod
  def delete_by_channel_id(db, langchannel_channel_id):
    result = db.langchannels.delete_one({'channel_id': langchannel_channel_id})
    return result.deleted_count if result.deleted_count > 0 else None
  
  @staticmethod
  def delete_by_id(db, langchannel_id):
    result = db.langchannels.delete_one({'_id': ObjectId(langchannel_id)})
    return result.deleted_count if result.deleted_count > 0 else None