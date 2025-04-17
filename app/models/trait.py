from bson import ObjectId
from typing import Dict, Optional
from pymongo import UpdateOne
from app.utils.strUtils import str_to_slug
from app.utils.types import *


class Trait:
  def __init__(self, name: Optional[str], image_url: str|None, type: str, sub_type: str, description: Optional[str], name_slug: Optional[str], _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.name_slug = name_slug
    self.image_url = image_url
    self.type = type
    self.sub_type = sub_type
    self.description = description
    

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name'),
      name_slug = str_to_slug(data.get('name')) if data.get('name') else None,
      image_url = data.get('image_url', None),
      type = data.get('type', None),
      sub_type = data.get('sub_type', None),
      description = data.get('description', None)
    )

  def to_dict(self) -> Dict:
    return {
      '_id': str(self._id) if self._id else None,
      'name': self.name,
      'name_slug': self.name_slug,
      'image_url': self.image_url,
      'type': self.type,
      'sub_type': self.sub_type,
      'description': self.description
    }
  
  def create(self, db):
    if not self._id:
      result = db.traits.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.traits.update_one({'_id': self._id}, {'$set': self.to_dict()})
    return self

  @staticmethod
  def read_by_id(db, trait_id):
    data = db.traits.find_one({'_id': ObjectId(trait_id)})
    return Trait.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, trait_name):
    data = db.traits.find_one({'name_slug': str_to_slug(trait_name)})
    return Trait.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    return [Trait.from_dict(trait) for trait in db.traits.find()]
  
  def update_traits(db, new_traits):
    existing_traits = list(db.traits.find())
    operations = []

    for new_trait in new_traits:
      trait_to_update = next((h for h in existing_traits if h['name'] == new_trait['name']), None)
      if trait_to_update:
        trait_to_return = {}
        for key, value in new_trait.items():
          if value is not None:
            trait_to_return[key] = value
      else:
        trait_to_return = new_trait

      trait_to_return['name_slug'] = str_to_slug(trait_to_return['name'])

      operations.append(
        UpdateOne(
          {'name': trait_to_return['name']},
          {'$set': trait_to_return},
          upsert = True
        )
      )
    if len(operations) > 0:
      db.traits.bulk_write(operations)

    return True
  
  @staticmethod
  def update_by_name(db, trait_name, update_data):
    result = db.traits.update_one({'name_slug': str_to_slug(trait_name)}, {'$set': update_data})
    return result.modified_count > 0

  @staticmethod
  def update_by_id(db, trait_id, update_data):
    result = db.traits.update_one({'_id': ObjectId(trait_id)}, {'$set': update_data})
    return result.modified_count > 0

  @staticmethod
  def delete_by_name(db, trait_name):
    result = db.traits.delete_one({'name_slug': str_to_slug(trait_name)})
    return result.deleted_count > 0
  
  @staticmethod
  def delete_by_id(db, trait_id):
    result = db.traits.delete_one({'_id': ObjectId(trait_id)})
    return result.deleted_count > 0