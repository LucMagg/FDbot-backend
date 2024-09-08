from bson import ObjectId
from typing import Dict, Optional, Union, List
from datetime import date
from pymongo import UpdateOne

from .talent import Talent
from ..utils.strUtils import str_to_slug, slug_to_str
from ..utils.types import *


class Comment:
  def __init__(self, author: str, commentaire: str, date: date):
    self.author = author
    self.commentaire = commentaire
    self.date = date

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      author = data.get('author'),
      commentaire = data.get('commentaire'),
      date = data.get('date')
    )

  def to_dict(self) -> Dict:
    return {
      'author': self.author,
      'commentaire': self.commentaire,
      'date': self.date
    }


class Pet:
  def __init__(
      self,
      attack: int,
      color: ColorType,
      petclass: ClassType,
      image_url: str | None,
      name: str,
      defense: int,
      manacost: int,
      stars: int,
      signature: str,
      signature_bis: str | None,
      name_slug: str,
      talents: Union[List[Talent], List] = None,
      comments: Union[List[Comment], List] = None,
      _id: Optional[str] = None
    ):
    self._id = ObjectId(_id) if _id else None
    self.attack = attack
    self.color = color
    self.petclass = petclass
    self.image_url = image_url
    self.name = name
    self.defense = defense
    self.manacost = manacost
    self.stars = stars
    self.signature = signature
    self.signature_bis = signature_bis
    self.name_slug = name_slug
    self.talents = talents
    self.comments = comments


  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id', {})),
      attack = data.get('attack'),
      color = data.get('color'),
      petclass = data.get('petclass'),
      image_url = data.get('image_url'),
      name = data.get('name'),
      defense = data.get('defense'),
      manacost = data.get('manacost'),
      stars = data.get('stars'),
      signature = data.get('signature'),
      signature_bis = data.get('signature_bis'),
      name_slug = str_to_slug(data.get('name')),
      talents = [Talent.from_dict(talent_data) for talent_data in data.get('talents', []) if isinstance(talent_data, dict)],
      comments = [Comment.from_dict(comment_data) for comment_data in data.get('comments', []) if isinstance(comment_data, dict)],
    )

  def to_dict(self) -> Dict:
    return {
      '_id': str(self._id) if self._id else None,
      'attack': self.attack,
      'color': self.color,
      'petclass': self.petclass,
      'image_url': self.image_url,
      'name': self.name,
      'defense': self.defense,
      'manacost': self.manacost,
      'stars': self.stars,
      'signature': self.signature,
      'signature_bis': self.signature_bis,
      'name_slug': self.name_slug,
      'talents': [{'name': talent.name, 'position': talent.position} for talent in self.talents] if self.talents else [],
      'comments': [comment.to_dict() for comment in self.comments] if self.comments else [],
    }
  
  def create(self, db):
    if not self._id:
      result = db.pets.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.pets.update_one({'_id': self._id}, {'$set': self.to_dict()})
    return self  

  @staticmethod
  def read_by_id(db, pet_id):
    data = db.pets.find_one({'_id': ObjectId(pet_id)})
    return Pet.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, pet_name):
    data = db.pets.find_one({'name_slug': str_to_slug(pet_name)})
    return Pet.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.pets.find()
    return [Pet.from_dict(pet) for pet in data] if data else None
  
  @staticmethod
  def read_by_class(db, petclass):
    pipeline_doc = db.pipelines.find_one({'name': 'pets_by_class'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        stage['$match']['petclass'] = slug_to_str(petclass)

    pets = list(db.pets.aggregate(pipeline_stages))
    data = []
    for pet in pets:
      pet['_id'] = str(pet['_id'])
      data.append(pet)
    return data
  
  @staticmethod
  def read_by_talent(db, talent):
    pipeline_doc = db.pipelines.find_one({'name': 'pets_by_talent'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        stage['$match']['talents.name'] = slug_to_str(talent)

    pets = list(db.pets.aggregate(pipeline_stages))
    data = []
    for pet in pets:
      pet['_id'] = str(pet['_id'])
      data.append(pet)
    return data
  
  @staticmethod
  def read_by_color_or_heroname(db, color, heroname):
    pipeline_doc = db.pipelines.find_one({'name': 'pets_by_color_or_heroname'})
    if not pipeline_doc:
      return None
    
    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
          stage['$match']['$or'][0]['color'] = color
          stage['$match']['$or'][1]['signature'] = heroname
          stage['$match']['$or'][2]['signature_bis'] = heroname

    pets = list(db.pets.aggregate(pipeline_stages))
    data = []
    for pet in pets:
      pet['_id'] = str(pet['_id'])
      data.append(pet)
    return data
  
  @staticmethod
  def update_pets(db, new_pets):
    existing_pets = list(db.pets.find())
    operations = []

    for new_pet in new_pets:
      pet_to_update = next((h for h in existing_pets if h['name'] == new_pet['name']), None)
      if pet_to_update:
        pet_to_return = {}
        for key, value in new_pet.items():
          if key not in ['talents', 'comments'] and value is not None:
            pet_to_return[key] = value

        if 'talents' in new_pet.keys():
          if 'talents' in pet_to_update.keys() and len(pet_to_update['talents']) > 1:
            pet_to_return['talents'] = []
            for new_talent in new_pet['talents']:
              existing_talent = next((t for t in pet_to_update['talents'] if 'position' in t and t['position'] == new_talent['position']), None)
              if existing_talent:
                if 'description' in new_talent.keys():
                  pet_to_return['talents'].append({'name': new_talent['name'], 'position': existing_talent['position'], 'description': new_talent['description']})
                else:
                  pet_to_return['talents'].append({'name': new_talent['name'], 'position': existing_talent['position']})
              else:
                pet_to_return['talents'].append(new_talent)
          else:
            pet_to_return['talents'] = new_pet['talents']

        if 'comments' in new_pet.keys():
          if 'comments' in pet_to_update.keys() and len(pet_to_update['comments']) > 1:
            pet_to_return['comments'] = []
            for new_comment in new_pet['comments']:
              existing_comment = next((c for c in pet_to_update['comments'] if c['author'] == new_comment['author']), None)
              if existing_comment:
                pet_to_return['comments'].append({'author': new_comment['author'], 'description': existing_comment['position']})
              else:
                pet_to_return['comments'].append(new_comment)
          else:
            pet_to_return['comments'] = new_pet['comments']

      else:
        pet_to_return = new_pet

      pet_to_return['name_slug'] = str_to_slug(pet_to_return['name'])

      operations.append(
        UpdateOne(
          {'name': pet_to_return['name']},
          {'$set': pet_to_return},
          upsert = True
        )
      )
    
    if len(operations) > 0:
      db.pets.bulk_write(operations)

    return True

  @staticmethod
  def update_by_name(db, pet_name, update_data):
    pet = Pet.from_dict(update_data).to_dict()

    if '_id' in pet:
      del pet['_id']

    result = db.pets.update_one(
      {'name_slug': str_to_slug(pet_name)},  
      {'$set': pet}
    )
    return True

  @staticmethod
  def update_by_id(db, pet_id, update_data):
    update_operations = Pet.create_update_operations(update_data)
    result = db.pets.update_one({'_id': ObjectId(pet_id)}, update_operations)
    return result.modified_count if result.modified_count > 0 else None

  @staticmethod
  def delete_by_name(db, pet_name):
    result = db.pets.delete_one({'name_slug': str_to_slug(pet_name)})
    return result.deleted_count if result.deleted_count > 0 else None
  
  @staticmethod
  def delete_by_id(db, pet_id):
    result = db.pets.delete_one({'_id': ObjectId(pet_id)})
    return result.deleted_count if result.deleted_count > 0 else None