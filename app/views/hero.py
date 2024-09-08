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
  heroclass = request.args.get('class')
  heroes = HeroService.get_heroes_by_class(heroclass)
  if heroes:
    return jsonify(heroes)
  return jsonify({'error': 'Heroes not found'}), 404

@hero_blueprint.route('/hero/gear', methods=['GET'])
def get_heroes_by_gear_name_and_quality():
  gear_name = request.args.get('gear_name')
  gear_quality = request.args.get('gear_quality')
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

@hero_blueprint.route('/hero/pet', methods=['GET'])
def get_heroes_by_pet():
  pet = request.args.get('pet')
  heroes = HeroService.get_heroes_by_pet(pet)
  if heroes:
    return jsonify(heroes)
  return jsonify({'error': 'Heroes not found'}), 404