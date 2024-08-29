from flask import Blueprint, jsonify, request
from app.services.pet import PetService
from app.services.talent import TalentService
from app.services.hero import HeroService

pet_blueprint = Blueprint('pet', __name__)


@pet_blueprint.route('/pet', methods=['POST'])
def add_pet():
  pet_data = request.json
  new_pet = PetService.create_pet(pet_data)
  return jsonify(new_pet.to_dict()), 201


@pet_blueprint.route('/pet/<pet>', methods=['GET'])
def get_pet(pet):
  pet_dict = PetService.get_one_pet(pet)
  if pet_dict:
    return jsonify(pet_dict)
  return jsonify({'error': 'Pet not found'}), 404


@pet_blueprint.route('/pet', methods=['GET'])
def get_pets():
  pets = PetService.get_all_pets()
  if pets:
    return jsonify([pet.to_dict() for pet in pets])
  return jsonify({'error': 'Pets not found'}), 404

@pet_blueprint.route('/pet/talent', methods=['GET'])
def get_pets_by_talent():
  talent = request.args.get('talent')
  talent_to_find = TalentService.get_one_talent(talent)

  if talent_to_find:
    pets = PetService.get_pets_by_talent(talent_to_find.name)
    if pets:
      return jsonify(pets)
    return jsonify({'error': 'Pets not found'}), 404
  
  return jsonify({'error': 'Talent not found'}), 404

@pet_blueprint.route('/pet/hero', methods=['GET'])
def get_pets_by_heroname():
  hero = request.args.get('hero')
  hero_to_find = HeroService.get_one_hero(hero)

  if hero_to_find:
    pets = PetService.get_pets_by_color_or_heroname(hero_to_find['color'], hero_to_find['name'])
    if pets:
      return jsonify(pets)
    return jsonify({'error': 'Pets not found'}), 404
  
  return jsonify({'error': 'Hero not found'}), 404