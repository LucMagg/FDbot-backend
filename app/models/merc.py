from bson import ObjectId
from typing import Dict, Optional, List
from ..utils.strUtils import str_to_slug


class Hero:
  def __init__(self, name, ascend = None, pet = False, pet_talent = None, name_slug = None, a2_talent = None, a3_talent = None, a4_talent = None, merge = None):
    self.name = name
    self.name_slug = name_slug if name_slug else str_to_slug(name)
    self.ascend = ascend
    self.pet = pet
    self.pet_talent = pet_talent
    self.a2_talent = a2_talent
    self.a3_talent = a3_talent
    self.a4_talent = a4_talent
    self.merge = merge

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name = data.get('name'),
      name_slug = data.get('name_slug', None) if data.get('name_slug') else str_to_slug(data.get('name')),
      ascend = data.get('ascend'),
      pet = data.get('pet'),
      pet_talent = data.get('pet_talent'),
      a2_talent = data.get('a2_talent'),
      a3_talent = data.get('a3_talent'),
      a4_talent = data.get('a4_talent'),
      merge = data.get('merge')
    )

  def to_dict(self) -> Dict:
    return {
      'name': self.name,
      'name_slug': self.name_slug if self.name_slug else str_to_slug(self.name),
      'ascend': self.ascend,
      'pet': self.pet,
      'pet_talent': self.pet_talent,
      'a2_talent': self.a2_talent,
      'a3_talent': self.a3_talent,
      'a4_talent': self.a4_talent,
      'merge': self.merge
    }
    

class Merc:
  def __init__(self, user: str, user_id: str, guild_id: str, mercs: List[Hero] = None, _id: Optional[str] = None):
    self._id = ObjectId(_id) if isinstance(_id, str) and _id.strip() else None
    self.user = user
    self.user_id = user_id
    self.guild_id = guild_id
    self.mercs = mercs if mercs else []

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') and data.get('_id') != {} else None,
      user = data.get('user'),
      user_id = data.get('user_id'),
      guild_id = data.get('guild_id'),
      mercs = [Hero.from_dict(merc) for merc in data.get('mercs')] if data.get('mercs') else []
    )

  def to_dict(self) -> Dict:
    result = {
      'user': self.user,
      'user_id': self.user_id,
      'guild_id': self.guild_id,
      'mercs': [merc.to_dict() for merc in self.mercs] if self.mercs else []
    }
    if self._id:
      result['_id'] = str(self._id)
    return result


  def create(self, db):
    if not self._id:
      already_exists = Merc.read_by_user(db, self.user)
      if not already_exists:
        insert_data = {
          'user': self.user,
          'user_id': self.user_id,
          'guild_id': self.guild_id,
          'mercs': [merc.to_dict() for merc in self.mercs] if self.mercs else []
        }
        result = db.mercs.insert_one(insert_data)
        self._id = result.inserted_id
      else:
        return self.add_merc_to_existing_user(db, already_exists)
    else:
      update_data = {
        'user': self.user,
        'user_id': self.user_id,
        'guild_id': self.guild_id,
        'mercs': [merc.to_dict() for merc in self.mercs] if self.mercs else []
      }
      db.mercs.update_one({'_id': self._id}, {'$set': update_data})
    return self

  @staticmethod
  def read_by_id(db, merc_id):
    data = db.mercs.find_one({'_id': ObjectId(merc_id)})
    return Merc.from_dict(data) if data else None
  
  @staticmethod
  def read_by_user(db, user):
    data = db.mercs.find_one({'user': user})
    return Merc.from_dict(data) if data else None

  @staticmethod
  def read_by_user_id(db, user_id):
    data = db.mercs.find_one({'user_id': user_id})
    return Merc.from_dict(data) if data else None
  
  @staticmethod
  def read_all(db):
    data = db.mercs.find()
    return data if data else None
  
  @staticmethod
  def read_by_merc(db, name, guild_id):
    pipeline_doc = db.pipelines.find_one({'name': 'users_by_merc_name_and_guild_id'})
    if not pipeline_doc:
      return None
    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]
    for stage in pipeline_stages:
      if '$match' in stage:
        if 'guild_id' in stage['$match']:
          stage['$match']['guild_id'] = guild_id
        if 'mercs.name' in stage['$match']:
          stage['$match']['mercs.name'] = name
    users = list(db.mercs.aggregate(pipeline_stages))
    if len(users) > 0:
      return users
    return None          
  
  def add_merc_to_existing_user(self, db, existing_user):
    merc = self.mercs[0]
    merc_data = merc.to_dict()
    existing_mercs_data = existing_user.to_dict()['mercs']
    merc_exists = any(existing_merc['name'] == merc.name for existing_merc in existing_mercs_data)
    if merc_exists:
      update_fields = {}
      if merc_data.get('name_slug'):
        update_fields['mercs.$.name_slug'] = merc_data['name_slug']
      else:
        update_fields['mercs.$.name_slug'] = str_to_slug(merc_data.get('name'))
      if merc_data.get('ascend'):
        update_fields['mercs.$.ascend'] = merc_data['ascend']
      if 'pet' in merc_data and merc_data['pet'] is not None:
        update_fields['mercs.$.pet'] = merc_data['pet']
      if 'pet_talent' in merc_data and merc_data['pet_talent'] is not None:
        update_fields['mercs.$.pet_talent'] = merc_data['pet_talent']
      if 'a2_talent' in merc_data and merc_data['a2_talent'] is not None:
        update_fields['mercs.$.a2_talent'] = merc_data['a2_talent']
      if 'a3_talent' in merc_data and merc_data['a3_talent'] is not None:
        update_fields['mercs.$.a3_talent'] = merc_data['a3_talent']
      if 'a4_talent' in merc_data and merc_data['a4_talent'] is not None:
        update_fields['mercs.$.a4_talent'] = merc_data['a4_talent']
      if 'merge' in merc_data and merc_data['merge'] is not None:
        update_fields['mercs.$.merge'] = merc_data['merge']
      db.mercs.update_one(
        {'user': self.user, 'mercs.name': merc.name},
        {'$set': update_fields}
      )
    else:
      new_merc_data = {
        'name': merc_data.get('name'),
        'ascend': merc_data.get('ascend'),
        'pet': merc_data.get('pet', False),
        'pet_talent': merc_data.get('pet_talent', False),
        'name_slug': merc_data.get('name_slug') if merc_data.get('name_slug') else str_to_slug(merc_data.get('name')),
        'a2_talent': merc_data.get('a2_talent'),
        'a3_talent': merc_data.get('a3_talent'),
        'a4_talent': merc_data.get('a4_talent'),
        'merge': merc_data.get('merge'),
      }
      db.mercs.update_one(
        {'user': self.user}, 
        {'$push': {'mercs': new_merc_data}}
      )
    if self.user_id != existing_user.user_id:
      db.mercs.update_one(
        {'user': self.user}, 
        {'$set': {'user_id': self.user_id}}
      )

    updated_data = db.mercs.find_one({'user': self.user})
    updated_merc = Merc.from_dict(updated_data)
    
    self._id = updated_merc._id
    self.mercs = updated_merc.mercs
    return self
  
  def read_all_unique_mercs(db):
    pipeline_doc = db.pipelines.find_one({'name': 'unique_mercs'})
    if not pipeline_doc:
      return
    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]
    result = list(db.mercs.aggregate(pipeline_stages))
    if result:
      return result
    return None