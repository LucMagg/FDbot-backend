from bson import ObjectId
from typing import Dict, Optional
from pymongo import UpdateOne
from app.utils.strUtils import str_to_slug
from app.utils.types import *


class Talent:
  def __init__(self, name: Optional[str], image_url: str|None, description: Optional[str], position: TalentPositionType, name_slug: Optional[str], _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.name_slug = name_slug
    self.image_url = image_url
    self.description = description
    self.position = position
    

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name'),
      name_slug = str_to_slug(data.get('name')) if data.get('name') else None,
      image_url = data.get('image_url', None),
      description = data.get('description', None),
      position = data.get('position', '')
    )

  def to_dict(self) -> Dict:
    return {
      '_id': str(self._id) if self._id else None,
      'name': self.name,
      'name_slug': self.name_slug,
      'image_url': self.image_url,
      'description': self.description,
      'position': self.position
    }
  
  def create(self, db):
    if not self._id:
      result = db.talents.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.talents.update_one({'_id': self._id}, {'$set': self.to_dict()})
    return self

  @staticmethod
  def read_by_id(db, talent_id):
    data = db.talents.find_one({'_id': ObjectId(talent_id)})
    return Talent.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, talent_name):
    data = db.talents.find_one({'name_slug': str_to_slug(talent_name)})
    return Talent.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    return [Talent.from_dict(talent) for talent in db.talents.find()]
  
  def update_talents(db, new_talents):
    existing_talents = list(db.talents.find())
    operations = []

    for new_talent in new_talents:
      talent_to_update = next((h for h in existing_talents if h['name'] == new_talent['name']), None)
      if talent_to_update:
        talent_to_return = {}
        for key, value in new_talent.items():
          if value is not None:
            talent_to_return[key] = value
      else:
        talent_to_return = new_talent

      talent_to_return['name_slug'] = str_to_slug(talent_to_return['name'])

      operations.append(
        UpdateOne(
          {'name': talent_to_return['name']},
          {'$set': talent_to_return},
          upsert = True
        )
      )
    if len(operations) > 0:
      db.talents.bulk_write(operations)

    return True
  
  @staticmethod
  def update_by_name(db, talent_name, update_data):
    result = db.talents.update_one({'name_slug': str_to_slug(talent_name)}, {'$set': update_data})
    return result.modified_count > 0

  @staticmethod
  def update_by_id(db, talent_id, update_data):
    result = db.talents.update_one({'_id': ObjectId(talent_id)}, {'$set': update_data})
    return result.modified_count > 0

  @staticmethod
  def delete_by_name(db, talent_name):
    result = db.talents.delete_one({'name_slug': str_to_slug(talent_name)})
    return result.deleted_count > 0
  
  @staticmethod
  def delete_by_id(db, talent_id):
    result = db.talents.delete_one({'_id': ObjectId(talent_id)})
    return result.deleted_count > 0