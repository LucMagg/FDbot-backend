from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from math import ceil
from datetime import datetime

from app.models.hero import Hero
from app.services.pet import PetService


class HeroService:
  def add_ascend_stats(hero):
    ascend_levels = ['A0', 'A1', 'A2', 'A3', 'A4']
    max_infusion = [{},
      {'A0':0, 'A1': 0, 'A2': 0, 'A3': 5, 'A4': 10},
      {'A0':0, 'A1': 0, 'A2': 0, 'A3': 10, 'A4': 25},
      {'A0':0, 'A1': 0, 'A2': 0, 'A3': 25, 'A4': 50},
      {'A0':0, 'A1': 0, 'A2': 0, 'A3': 50, 'A4': 100},
      {'A0':0, 'A1': 0, 'A2': 0, 'A3': 100, 'A4': 150}
    ]
    available = [a for a in ascend_levels if hero['attack'].get(a)]
    pet = PetService.get_one_pet(hero['pet']) if hero.get('pet') else None
    pet_att_pct = pet['attack'] / 100 if pet else 0
    pet_def_pct = pet['defense'] / 100 if pet else 0
    att_slots = ['Amulet', 'Weapon', 'Ring']
    def_slots  = ['Head', 'Off-Hand', 'Body']
    attack_max = {}
    defense_max = {}

    for ascend in available:
      base_att = hero.get('attack').get(ascend)
      base_def = hero.get('defense').get(ascend)
      att_g = HeroService._gear_pct(hero, ascend, att_slots)
      def_g = HeroService._gear_pct(hero, ascend, def_slots)
      attack_max[ascend] = {
        'base':  base_att,
        'gear':  ceil(base_att * att_g),
        'merge': ceil(base_att * 0.15),
        'infusion': ceil(base_att * (max_infusion[int(hero.get('stars'))].get(ascend) / 1000)),
        'pet':   ceil(base_att * pet_att_pct),
      }
      attack_max[ascend]['total'] = sum(attack_max.get(ascend).values())
      defense_max[ascend] = {
        'base':  base_def,
        'gear':  ceil(base_def * def_g),
        'merge': ceil(base_def * 0.15),
        'infusion': ceil(base_def * (max_infusion[int(hero.get('stars'))].get(ascend) / 1000)),
        'pet':   ceil(base_def * pet_def_pct),
      }
      defense_max[ascend]['total'] = sum(defense_max.get(ascend).values())
    hero['attack_max'] = attack_max
    hero['defense_max'] = defense_max
    return hero
  
  def _gear_pct(hero, ascend, slots) -> int:
    return sum(1 for g in hero['gear'] if g['ascend'] == ascend and g['position'] in slots and g.get('name')) * 0.05
  
  def add_stats_rank(hero, heroes):
    for stat, rank, average in [('att_max', 'att_rank', 'att_average'), ('def_max', 'def_rank', 'def_average')]:
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
        
        total = 0
        for h in heroes:
          total += h[stat]
        hero[average] = round(total / len(heroes))
        
    hero['class_count'] = len(heroes)
    return hero
  
  def add_unique_talents(hero, heroes):
    talent_count = {}
    for h in heroes:
      if h['name'] != hero['name']:
        for talent in h['talents']:
          if talent['name'] in talent_count.keys():
            talent_count[talent['name']] += 1
          else:
            talent_count[talent['name']] = 1

    unique_talents = []
    for talent in hero['talents']:
      if talent['name'] not in talent_count.keys() and talent['name'] not in unique_talents:
        unique_talents.append(talent['name'])

    hero['unique_talents'] = unique_talents
    return hero
  
  def add_stats(hero, heroes):
    hero = HeroService.add_ascend_stats(hero)
    last = hero['ascend_max']
    hero['att_max'] = hero['attack_max'][last]['total']
    hero['def_max'] = hero['defense_max'][last]['total']
    hero = HeroService.add_stats_rank(hero, heroes)
    hero = HeroService.add_unique_talents(hero, heroes)
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
    return None
  
  @staticmethod
  def get_all_heroes():
    heroes = Hero.read_all(current_app.mongo_db)
    if heroes:
      to_return = []
      for hero in heroes:
        to_return.append(hero.to_dict())
      return to_return
    return None

  @staticmethod
  def get_heroes_by_class(heroclass):
    if heroclass == 'all':
      return Hero.read_all_classes(current_app.mongo_db)
    heroes = Hero.read_by_class(current_app.mongo_db, heroclass)
    for hero in heroes:
      hero = HeroService.add_ascend_stats(hero)
      last = hero['ascend_max']
      hero['att_max'] = hero['attack_max'][last]['total']
      hero['def_max'] = hero['defense_max'][last]['total']
    return heroes

  @staticmethod
  def get_heroes_by_gear_name_and_quality(gear_name, gear_quality):
    if gear_quality is None:
      heroes = Hero.read_by_gear_name(current_app.mongo_db, gear_name)
    else:
      heroes = Hero.read_by_gear_name_and_quality(current_app.mongo_db, gear_name, gear_quality)
    if heroes:
      return heroes
    return None

  @staticmethod
  def get_heroes_by_talent(talent_name):
    heroes = Hero.read_by_talent(current_app.mongo_db, talent_name)
    if heroes:
      return heroes
    return None
    
  @staticmethod
  def get_heroes_by_pet(pet_name):
    heroes = Hero.read_by_pet(current_app.mongo_db, pet_name)
    if heroes:
      return heroes
    return None
    
  @staticmethod
  def get_exclusive_heroes(exclusive_type=None):
    heroes = Hero.read_exclusives(current_app.mongo_db, exclusive_type)
    if heroes:
      return heroes
    return None
  
  @staticmethod
  def get_all_exclusive_types():
    exclusive_types = Hero.read_exclusive_types(current_app.mongo_db)
    if exclusive_types:
      return exclusive_types
    return None
    
  @staticmethod
  def add_comment(hero_to_comment, comment, author, lang):
    existing_comment = next((c for c in hero_to_comment['comments'] if c['author'] == author and c['lang'] == lang), None)
    if existing_comment:
      existing_comment['commentaire'] = comment
      existing_comment['date'] = datetime.now()
      existing_comment['lang'] = lang
    else:
      hero_to_comment['comments'].append({'author': author, 'commentaire': comment, 'date': datetime.now(), 'lang': lang})
    Hero.update_by_name(current_app.mongo_db, hero_to_comment['name'], hero_to_comment)

