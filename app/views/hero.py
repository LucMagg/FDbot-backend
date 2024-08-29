from flask import Blueprint, jsonify, request, current_app
from app.services.hero import HeroService

hero_blueprint = Blueprint('hero', __name__)


@hero_blueprint.route('/hero', methods=['POST'])
def add_hero():
  hero_data = request.json
  new_hero = HeroService.create_hero(hero_data)
  return jsonify(new_hero.to_dict()), 201


@hero_blueprint.route('/hero/<hero>', methods=['GET'])
def get_hero(hero):
  hero_dict = HeroService.get_one_hero(hero)
  if hero_dict:
    return jsonify(hero_dict)
  return jsonify({'error': 'Hero not found'}), 404


@hero_blueprint.route('/hero', methods=['GET'])
def get_heroes():
  heroes = HeroService.get_all_heroes()
  if heroes:
    return jsonify(heroes)
  return jsonify({'error': 'Heroes not found'}), 404


@hero_blueprint.route('/hero/class', methods=['GET'])
def get_heroes_by_class():
  heroclass = request.args.get('heroclass')
  heroes = HeroService.get_heroes_by_class(heroclass)
  if heroes:
    return jsonify(heroes)
  return jsonify({'error': 'Heroes not found'}), 404

@hero_blueprint.route('/hero/gear', methods=['GET'])
def get_heroes_by_gear_name_and_quality():
  gear_name = request.args.get('gear_name')
  gear_quality = request.args.get('gear_quality')
  print(gear_quality)
  heroes = HeroService.get_heroes_by_gear_name_and_quality(gear_name, gear_quality)
  if heroes:
    return jsonify(heroes)
  return jsonify({'error': 'Heroes not found'}), 404

@hero_blueprint.route('/hero/talent', methods=['GET'])
def get_heroes_by_talent():
  talent = request.args.get('talent')
  heroes = HeroService.get_heroes_by_talent(talent)
  if heroes:
    return jsonify(heroes)
  return jsonify({'error': 'Heroes not found'}), 404


"""
@hero_blueprint.route('/hero-lead', methods=['PUT'])
def update_leads():
  heroes = current_app.mongo_db.heroes.find()

  for hero in heroes:
    hero['lead_color'] = {'attack': None, 'defense': None, 'talent': None, 'color': None, 'species': None}
    hero['lead_species'] = {'attack': None, 'defense': None, 'talent': None, 'color': None, 'species': None}

    if hero['lead_bonus_color'] is not None:
      print(hero['lead_bonus_color'])

      if 'att' in hero['lead_bonus_color']:
        hero['lead_color']['attack'] = float(hero['lead_bonus_color'].split(' att')[0].split('x')[1].replace(',','.'))
        hero['lead_bonus_color'] = hero['lead_bonus_color'].split(' att')[1]

      if 'def' in hero['lead_bonus_color']:
        hero['lead_color']['defense'] = float(hero['lead_bonus_color'].split(' def')[0].split('x')[1].replace(',','.'))

      for color in ['Red','Green','Blue','Light','Dark']:
        if color in hero['lead_bonus_color']:
          hero['lead_color']['color'] = color
      
      for species in ['Beastfolk','Dragonborn','Dwarf','Elf','Human','Orc']:
        if species in hero['lead_bonus_color']:
          hero['lead_color']['species'] = species

      if hero['lead_color']['attack'] is None and hero['lead_color']['defense'] is None:
        hero['lead_color']['talent'] = hero['lead_bonus_color'].split(' for')[0]

      print(hero['lead_color'])

    if hero['lead_bonus_species'] is not None:
      print(hero['lead_bonus_species'])

      if 'att' in hero['lead_bonus_species']:
        hero['lead_species']['attack'] = float(hero['lead_bonus_species'].split(' att')[0].split('x')[1].replace(',','.'))
        hero['lead_bonus_species'] = hero['lead_bonus_species'].split(' att')[1]

      if 'def' in hero['lead_bonus_species']:
        hero['lead_species']['defense'] = float(hero['lead_bonus_species'].split(' def')[0].split('x')[1].replace(',','.'))

      for color in ['Red','Green','Blue','Light','Dark']:
        if color in hero['lead_bonus_species']:
          hero['lead_species']['color'] = color
      
      for species in ['Beastfolk','Dragonborn','Dwarf','Elf','Human','Orc']:
        if species in hero['lead_bonus_species']:
          hero['lead_species']['species'] = species

      if hero['lead_species']['attack'] is None and hero['lead_species']['defense'] is None:
        hero['lead_species']['talent'] = hero['lead_bonus_species'].split(' for')[0]

      print(hero['lead_species'])

    current_app.mongo_db.heroes.update_one({'name_slug': hero['name_slug']}, {'$set': hero})


      



  return jsonify({'done':'done'}), 200

"""