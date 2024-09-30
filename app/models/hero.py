from bson import ObjectId
from bson.errors import InvalidId
from typing import Dict, Optional, Union, List
from datetime import date
from pymongo import UpdateOne

from app.models.talent import Talent
from app.models.pet import Pet
from app.utils.strUtils import str_to_slug, slug_to_str
from app.utils.types import *


class Attack:
  def __init__(self, att75: int|None, att85: int|None, att95: int|None, att100: int|None):
    self.att75 = att75
    self.att85 = att85
    self.att95 = att95
    self.att100 = att100

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      att75 = data.get('att75', None),
      att85 = data.get('att85', None),
      att95 = data.get('att95', None),
      att100 = data.get('att100', None),

    )

  def to_dict(self) -> Dict:
    return {
      'att75': self.att75,
      'att85': self.att85,
      'att95': self.att95,
      'att100': self.att100,
      'max': self.att_max()
    }
  
  def att_max(self) -> int|None:
    to_compare = []
    if self.att75 is not None:
      to_compare.append(self.att75)
    if self.att85 is not None:
      to_compare.append(self.att85)
    if self.att95 is not None:
      to_compare.append(self.att95)
    if self.att100 is not None:
      to_compare.append(self.att100)
    
    to_return = 0
    for n in to_compare:
      if n > to_return:
        to_return = n
      
    if to_return > 0:
      return to_return
    else:
      return None
  

class Defense:
  def __init__(self, def75: int|None, def85: int|None, def95: int|None, def100: int|None):
    self.def75 = def75
    self.def85 = def85
    self.def95 = def95
    self.def100 = def100

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      def75 = data.get('def75', None),
      def85 = data.get('def85', None),
      def95 = data.get('def95', None),
      def100 = data.get('def100', None),
    )

  def to_dict(self) -> Dict:
    return {
      'def75': self.def75,
      'def85': self.def85,
      'def95': self.def95,
      'def100': self.def100,
      'max': self.def_max()
    }
    
  def def_max(self) -> int|None:
    to_compare = []
    if self.def75 is not None:
      to_compare.append(self.def75)
    if self.def85 is not None:
      to_compare.append(self.def85)
    if self.def95 is not None:
      to_compare.append(self.def95)
    if self.def100 is not None:
      to_compare.append(self.def100)
    
    to_return = 0
    for n in to_compare:
      if n > to_return:
        to_return = n
      
    if to_return > 0:
      return to_return
    else:
      return None
  


class Lead:
  def __init__(self, attack: str|None, defense: str|None, talent: str|None, color: ColorType|None, species: SpeciesType|None):
    self.attack = attack
    self.defense = defense
    self.talent = talent
    self.color = color
    self.species = species

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      attack = data.get('attack', None),
      defense = data.get('defense', None),
      talent = data.get('talent', None),
      color = data.get('color', None),
      species = data.get('species', None)
    )

  def to_dict(self) -> Dict:
    return {
      'attack': self.attack,
      'defense': self.defense,
      'talent': self.talent,
      'color': self.color,
      'species': self.species
    }
  


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
  


class Gear:
  def __init__(self, ascend: AscendType, name: str, quality: str, position: str):
    self.ascend = ascend
    self.name = name
    self.quality = quality
    self.position = position

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      ascend = data.get('ascend'),
      name = data.get('name'),
      quality = data.get('quality'),
      position = data.get('position')
    )

  def to_dict(self) -> Dict:
    return {
      'ascend': self.ascend,
      'name': self.name,
      'quality': self.quality,
      'position': self.position
    }



class Hero:
  def __init__(
      self,
      ascend_max: int,
      base_IA: str,
      color: ColorType,
      heroclass: ClassType,
      image_url: str | None,
      name: str,
      pet: str | None,
      pattern: PatternType,
      species: SpeciesType,
      stars: int,
      type: TypeType,
      name_slug: str,
      attack: Attack,
      defense: Defense,
      lead_color: Lead,
      lead_species: Lead,
      talents: Union[List[Talent], List] = None,
      comments: Union[List[Comment], List] = None,
      gear: Union[List[Gear], List] = None,
      _id: Optional[str] = None
    ):
    try:
      self._id = ObjectId(_id)
    except InvalidId:
      self._id = None
    self.ascend_max = ascend_max
    self.base_IA = base_IA
    self.color = color
    self.heroclass = heroclass
    self.image_url = image_url
    self.name = name
    self.pet = pet
    self.pattern = pattern
    self.species = species
    self.stars = stars
    self.type = type
    self.name_slug = name_slug
    self.attack = attack
    self.defense = defense
    self.lead_color = lead_color
    self.lead_species = lead_species
    self.talents = talents
    self.comments = comments
    self.gear = gear


  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id', {})),
      ascend_max = data.get('ascend_max'),
      base_IA = data.get('base_IA'),
      color = data.get('color'),
      heroclass = data.get('heroclass'),
      image_url = data.get('image_url'),
      name = data.get('name'),
      pet = data.get('pet', None),
      pattern = data.get('pattern'),
      species = data.get('species'),
      stars = data.get('stars'),
      type = data.get('type'),
      name_slug = str_to_slug(data.get('name')),
      attack = Attack.from_dict(data.get('attack', {})),
      defense = Defense.from_dict(data.get('defense', {})),
      lead_color = Lead.from_dict(data.get('lead_color', {})),
      lead_species = Lead.from_dict(data.get('lead_species', {})),
      talents = [Talent.from_dict(talent_data) for talent_data in data.get('talents', []) if isinstance(talent_data, dict)],
      comments = [Comment.from_dict(comment_data) for comment_data in data.get('comments', []) if isinstance(comment_data, dict)],
      gear = [Gear.from_dict(gear_data) for gear_data in data.get('gear', []) if isinstance(gear_data, dict)]
    )

  def to_dict(self) -> Dict:
    return {
      '_id': str(self._id) if self._id else None,
      'ascend_max': self.ascend_max,
      'base_IA': self.base_IA,
      'color': self.color,
      'heroclass': self.heroclass,
      'image_url': self.image_url,
      'name': self.name,
      'pet': self.pet,
      'pattern': self.pattern,
      'species': self.species,
      'stars': self.stars,
      'type': self.type,
      'name_slug': self.name_slug,
      'attack': self.attack.to_dict(),
      'defense': self.defense.to_dict(),
      'lead_color': self.lead_color.to_dict(),
      'lead_species': self.lead_species.to_dict(),
      'talents': [{'name': talent.name, 'position': talent.position} for talent in self.talents] if self.talents else [],
      'comments': [comment.to_dict() for comment in self.comments] if self.comments else [],
      'gear': [gear.to_dict() for gear in self.gear] if self.gear else [],
      'lvl_max': self.lvl_max(),
      'ascend': self.ascend()
    }
  
  def ascend(self) -> int|None:
    if self.ascend_max and self.stars:
      return self.ascend_max - self.stars
    else:
      return None
  
  def lvl_max(self) -> int:
    if self.ascend() == 2:
      return 95
    else:
      return 100

  @staticmethod
  def create(self, db):
    if not self._id:
      result = db.heroes.insert_one(self.to_dict())
      self._id = result.inserted_id
    else:
      db.heroes.update_one({'_id': self._id}, {'$set': self.to_dict()})
    return self  

  @staticmethod
  def read_by_id(db, hero_id):
    data = db.heroes.find_one({'_id': ObjectId(hero_id)})
    return Hero.from_dict(data) if data else None
  
  @staticmethod
  def read_by_name(db, hero_name):
    data = db.heroes.find_one({'name_slug': str_to_slug(hero_name)})
    return Hero.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.heroes.find()
    return [Hero.from_dict(hero) for hero in data] if data else None
  
  @staticmethod
  def read_all_classes(db):
    pipeline_doc = db.pipelines.find_one({'name': 'list_all_classes'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    classes = list(db.heroes.aggregate(pipeline_stages))  
    return classes
  
  @staticmethod
  def read_by_class(db, heroclass):
    pipeline_doc = db.pipelines.find_one({'name': 'heroes_by_class'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        stage['$match']['heroclass'] = heroclass

    heroes = list(db.heroes.aggregate(pipeline_stages))  
    data = []
    for hero in heroes:
      hero_obj = Hero.from_dict(hero)
      hero_dict_with_stats = Hero.to_dict(hero_obj)
      data.append(hero_dict_with_stats)
    return data
  
  @staticmethod
  def read_by_gear_name(db, gear_name):
    pipeline_doc = db.pipelines.find_one({'name': 'heroes_by_gear_name'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        stage['$match']['gear.name'] = gear_name

    heroes = list(db.heroes.aggregate(pipeline_stages))
    data = []
    for hero in heroes:
      hero['_id'] = str(hero['_id'])
      data.append(hero)
    return data
  
  @staticmethod
  def read_by_gear_name_and_quality(db, gear_name, gear_quality):
    pipeline_doc = db.pipelines.find_one({'name': 'heroes_by_gear_name_and_quality'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        stage['$match']['gear.name'] = gear_name
        stage['$match']['gear.quality'] = gear_quality

    heroes = list(db.heroes.aggregate(pipeline_stages))
    data = []
    for hero in heroes:
      hero['_id'] = str(hero['_id'])
      data.append(hero)
    return data
  
  @staticmethod
  def read_by_talent(db, talent):
    pipeline_doc = db.pipelines.find_one({'name': 'heroes_by_talent'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        stage['$match']['talents.name'] = talent

    heroes = list(db.heroes.aggregate(pipeline_stages))
    data = []
    for hero in heroes:
      hero['_id'] = str(hero['_id'])
      data.append(hero)
    return data
  
  @staticmethod
  def read_by_pet(db, pet):
    pet = Pet.read_by_name(db, pet)
    if not pet:
      return None
    
    pipeline_doc = db.pipelines.find_one({'name': 'heroes_by_pet'})
    if not pipeline_doc:
      return None

    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        stage['$match']['color'] = pet.color
        stage['$match']['heroclass'] = pet.petclass

    heroes = list(db.heroes.aggregate(pipeline_stages))
    data = []
    for hero in heroes:
      hero['_id'] = str(hero['_id'])
      data.append(hero)
    return data
  
  @staticmethod
  def update_by_name(db, hero_name, update_data):
    hero = Hero.from_dict(update_data).to_dict()
    del hero['ascend']
    del hero['lvl_max']

    if '_id' in hero:
      del hero['_id']

    result = db.heroes.update_one(
      {'name_slug': str_to_slug(hero_name)},  
      {'$set': hero}
    )
    return True

  @staticmethod
  def update_by_id(db, hero_id, update_data):
    return Hero.update_hero(db, hero_id, update_data)
  
  @staticmethod
  def update_heroes(db, new_heroes):
    existing_heroes = list(db.heroes.find())
    existing_pets = list(db.pets.find())
    operations = []

    for new_hero in new_heroes:
      hero_to_update = next((h for h in existing_heroes if h['name'] == new_hero['name']), None)
      if hero_to_update:
        hero_to_return = {}
        for key, value in new_hero.items():
          if key not in ['gear', 'talents', 'comments'] and value is not None:
            hero_to_return[key] = value

        if 'talents' in new_hero.keys():
          if 'talents' in hero_to_update.keys() and len(hero_to_update['talents']) > 1:
            hero_to_return['talents'] = []
            for new_talent in new_hero['talents']:
              existing_talent = next((t for t in hero_to_update['talents'] if 'position' in t and t['position'] == new_talent['position']), None)
              if existing_talent:
                hero_to_return['talents'].append({'name': new_talent['name'], 'position': existing_talent['position']})
              else:
                hero_to_return['talents'].append(new_talent)
          else:
            hero_to_return['talents'] = new_hero['talents']

        if 'comments' in new_hero.keys():
          if 'comments' in hero_to_update.keys() and len(hero_to_update['comments']) > 1:
            hero_to_return['comments'] = []
            for new_comment in new_hero['comments']:
              existing_comment = next((c for c in hero_to_update['comments'] if c['author'] == new_comment['author']), None)
              if existing_comment:
                hero_to_return['comments'].append({'author': new_comment['author'], 'description': existing_comment['position']})
              else:
                hero_to_return['comments'].append(new_comment)
          else:
            hero_to_return['comments'] = new_hero['comments']

        if 'gear' in new_hero.keys():
          if 'gear' in hero_to_update.keys() and len(hero_to_update['gear']) > 1:
            hero_to_return['gear'] = []
            for new_gear in new_hero['gear']:
              existing_gear = next((g for g in hero_to_update['gear']
                                    if (('position' in g and g['position'] == new_gear['position']) and ('ascend' in g and g['ascend'] == new_gear['ascend']))), None)
              if existing_gear:
                hero_to_return['gear'].append({'name': new_gear['name'], 'position': existing_gear['position'], 'ascend': existing_gear['ascend'], 'quality': new_gear['quality']})
              else:
                hero_to_return['gear'].append(new_gear)
          else:
            hero_to_return['gear'] = new_hero['gear']

      else:
        hero_to_return = new_hero

      if 'attack' in hero_to_return.keys() and 'stars' in hero_to_return.keys():
        if 'att100' in hero_to_return['attack'].keys():
          hero_to_return['ascend_max'] = hero_to_return['stars'] + 3
        else:
          hero_to_return['ascend_max'] = hero_to_return['stars'] + 2

      hero_to_return['name_slug'] = str_to_slug(hero_to_return['name'])

      existing_pet = next((p for p in existing_pets if p['signature'] == hero_to_return['name'] or p['signature_bis'] == hero_to_return['name']), None)
      if existing_pet:
        hero_to_return['pet'] = existing_pet['name']
      else:
        hero_to_return['pet'] = None


      operations.append(
        UpdateOne(
          {'name': hero_to_return['name']},
          {'$set': hero_to_return},
          upsert = True
        )
      )
    
    if len(operations) > 0:
      db.heroes.bulk_write(operations)

    return True

  @staticmethod
  def delete_by_name(db, hero_name):
    result = db.heroes.delete_one({'name_slug': str_to_slug(hero_name)})
    return result.deleted_count if result.deleted_count > 0 else None
  
  @staticmethod
  def delete_by_id(db, hero_id):
    result = db.heroes.delete_one({'_id': ObjectId(hero_id)})
    return result.deleted_count if result.deleted_count > 0 else None