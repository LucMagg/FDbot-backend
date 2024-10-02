from flask import Blueprint, jsonify, request, current_app
from app.services.hero import HeroService
from app.services.talent import TalentService
from app.utils.strUtils import slug_to_str

hero_blueprint = Blueprint('hero', __name__)


@hero_blueprint.route('/hero', methods=['POST'])
def add_hero():
  hero_data = request.json
  new_hero = HeroService.create_hero(hero_data)
  return jsonify(new_hero.to_dict()), 201


@hero_blueprint.route('/hero/<hero>', methods=['GET'])
def get_hero(hero):
  req = '/hero GET'
  current_app.logger.req(req)
  current_app.logger.log_info('info', f'hero : {hero}')
  hero_dict = HeroService.get_one_hero(hero)

  if hero_dict:
    current_app.logger.req_ok(req)
    return jsonify(hero_dict)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Hero not found'}), 404


@hero_blueprint.route('/hero', methods=['GET'])
def get_heroes():
  req = '/hero GET'
  current_app.logger.req(req)

  heroes = HeroService.get_all_heroes()
  if heroes:
    current_app.logger.req_ok(req)
    return jsonify(heroes)

  current_app.logger.req_404(req)
  return jsonify({'error': 'Heroes not found'}), 404


@hero_blueprint.route('/hero/class', methods=['GET'])
def get_heroes_by_class():
  req = '/hero/class GET'
  current_app.logger.req(req)

  heroclass = request.args.get('class')
  current_app.logger.log_info('info', f'class : {heroclass}')

  heroes = HeroService.get_heroes_by_class(heroclass)
  if heroes:
    current_app.logger.req_ok(req)
    return jsonify(heroes)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Heroes not found'}), 404


@hero_blueprint.route('/hero/gear', methods=['GET'])
def get_heroes_by_gear_name_and_quality():
  req = '/hero/gear GET'
  current_app.logger.req(req)

  gear_name = request.args.get('gear_name')
  gear_quality = request.args.get('gear_quality')
  current_app.logger.log_info('info', f'gear name : {gear_name} | gear quality : {gear_quality}')

  heroes = HeroService.get_heroes_by_gear_name_and_quality(gear_name, gear_quality)
  if heroes:
    current_app.logger.req_ok(req)
    return jsonify(heroes)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Heroes not found'}), 404


@hero_blueprint.route('/hero/talent', methods=['GET'])
def get_heroes_by_talent():
  req = '/hero/talent GET'
  current_app.logger.req(req)

  talent = request.args.get('talent')
  current_app.logger.log_info('info', f'talent : {talent}')

  talent_to_find = TalentService.get_one_talent(talent)

  if talent_to_find:
    heroes = HeroService.get_heroes_by_talent(talent_to_find.name)
    if heroes:
      current_app.logger.req_ok(req)
      return jsonify(heroes)
    current_app.logger.req_404(req, 'Heroes not found')
    return jsonify({'error': 'Heroes not found'}), 404
  
  current_app.logger.req_404(req, 'Talent not found')
  return jsonify({'error': 'Talent not found'}), 404

@hero_blueprint.route('/hero/pet', methods=['GET'])
def get_heroes_by_pet():
  req = '/hero/pet GET'
  current_app.logger.req(req)

  pet = request.args.get('pet')
  current_app.logger.log_info('info', f'pet : {pet}')

  heroes = HeroService.get_heroes_by_pet(pet)
  if heroes:
    current_app.logger.req_ok(req)
    return jsonify(heroes)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Heroes not found'}), 404