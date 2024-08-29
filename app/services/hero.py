from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from math import ceil
from datetime import datetime

from app.models.hero import Hero
from app.services.pet import PetService



class HeroService:
  def att_gear(hero):
    return ceil(hero['attack']['max'] * 5 / 100 * hero['ascend'])
  
  def def_gear(hero):
    return ceil(hero['defense']['max'] * 5 / 100 * hero['ascend'])
  
  def att_merge(hero):
    return ceil(hero['attack']['max'] * 15 / 100)
  
  def def_merge(hero):
    return ceil(hero['defense']['max'] * 15 / 100)
  
  def att_pet_boost(hero):
    if hero['pet'] is not None:
      pet = PetService.get_one_pet(hero['pet'])
      if pet is not None:
        return ceil(hero['attack']['max'] * pet['attack'] / 100)
      else:
        return 0
    else:
      return 0
  
  def def_pet_boost(hero):
    if hero['pet'] is not None:
      pet = PetService.get_one_pet(hero['pet'])
      if pet is not None:
        return ceil(hero['defense']['max'] * pet['defense'] / 100)
      else:
        return 0
    else:
      return 0
    
  def att_max(hero):
    return hero['attack']['max'] + hero['att_gear'] + hero['att_merge'] + hero['att_pet_boost']
  
  def def_max(hero):
    return hero['defense']['max'] + hero['def_gear'] + hero['def_merge'] + hero['def_pet_boost']
  
  def add_stats(hero, heroes):
    hero['att_gear'] = HeroService.att_gear(hero)
    hero['att_merge'] = HeroService.att_gear(hero)
    hero['att_pet_boost'] = HeroService.att_pet_boost(hero)
    hero['att_max'] = HeroService.att_max(hero)
    hero['def_gear'] = HeroService.def_gear(hero)
    hero['def_merge'] = HeroService.def_gear(hero)
    hero['def_pet_boost'] = HeroService.def_pet_boost(hero)
    hero['def_max'] = HeroService.def_max(hero)
    hero = HeroService.add_stats_rank(hero, heroes)
    return hero
  
  def add_stats_rank(hero, heroes):
    for stat, rank in [('att_max', 'att_rank'), ('def_max', 'def_rank')]:
      if all(stat in h for h in heroes):
        sorted_list = sorted(heroes, key=lambda h: h[stat], reverse=True)
        
        for i, item in enumerate(sorted_list):
          item[rank] = i + 1
          if i > 0 and item[stat] == sorted_list[i-1][stat]:
            item[rank] = sorted_list[i-1][rank]
        
        for item in heroes:
          for sorted_item in sorted_list:
            if item[stat] == sorted_item[stat]:
              item[rank] = sorted_item[rank]
              break

        for item in heroes:
          if hero['name'] == item['name']:
            hero[rank] = item[rank]
            break

    hero['class_count'] = len(heroes)
    return hero

  @staticmethod
  def create_hero(hero_data):
    hero = Hero.from_dict(hero_data)
    return hero.create(current_app.mongo_db)

  @staticmethod
  def get_one_hero(hero_name_or_id):
    try:
      to_return = Hero.read_by_id(current_app.mongo_db, ObjectId(hero_name_or_id))
    except InvalidId:
      to_return = Hero.read_by_name(current_app.mongo_db, hero_name_or_id)
    
    if to_return:
      heroes = HeroService.get_heroes_by_class(to_return.heroclass)
      hero = HeroService.add_stats(to_return.to_dict(), heroes)
      return hero
    else:
      return None
  
  @staticmethod
  def get_all_heroes():
    heroes = Hero.read_all(current_app.mongo_db)
    
    if heroes:
      to_return = []
      for hero in heroes:
        to_return.append(hero.to_dict())
      return to_return
    else:
      return None

  @staticmethod
  def get_heroes_by_class(heroclass):
    heroes = Hero.read_by_class(current_app.mongo_db, heroclass)
    to_return = []
    for hero in heroes:
      hero = HeroService.add_stats(hero, heroes)
      to_return.append(hero)

    return to_return

  @staticmethod
  def get_heroes_by_gear_name_and_quality(gear_name, gear_quality):
    if gear_quality is None:
      heroes = Hero.read_by_gear_name(current_app.mongo_db, gear_name)
    else:
      heroes = Hero.read_by_gear_name_and_quality(current_app.mongo_db, gear_name, gear_quality)

    if heroes:
      return heroes
    else:
      return None

  @staticmethod
  def get_heroes_by_talent(talent_name):
    heroes = Hero.read_by_talent(current_app.mongo_db, talent_name)

    if heroes:
      return heroes
    else:
      return None
    
  @staticmethod
  def add_comment(hero_to_comment, comment, author):
    existing_comment = next((c for c in hero_to_comment['comments'] if c['author'] == author), None)
    if existing_comment:
      existing_comment['commentaire'] = comment
      existing_comment['date'] = datetime.now()
    else:
      hero_to_comment['comments'].append({'author': author, 'commentaire': comment, 'date': datetime.now()})

    Hero.update_by_name(current_app.mongo_db, hero_to_comment['name'], hero_to_comment)

