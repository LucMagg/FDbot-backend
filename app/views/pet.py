from flask import Blueprint, jsonify, request, current_app
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
  req = '/pet GET'
  current_app.logger.req(req)
  current_app.logger.log_info('info', f'pet : {pet}')

  pet_dict = PetService.get_one_pet(pet)
  if pet_dict:
    current_app.logger.req_ok(req)
    return jsonify(pet_dict)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Pet not found'}), 404


@pet_blueprint.route('/pet', methods=['GET'])
def get_pets():
  req = '/pet GET'
  current_app.logger.req(req)

  pets = PetService.get_all_pets()
  if pets:
    current_app.logger.req_ok(req)
    return jsonify([pet.to_dict() for pet in pets])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Pets not found'}), 404

@pet_blueprint.route('/pet/class', methods=['GET'])
def get_pets_by_class():
  req = '/pet/class GET'
  current_app.logger.req(req)

  petclass = request.args.get('class')
  current_app.logger.log_info('info', f'class : {petclass}')

  pets = PetService.get_pets_by_class(petclass)
  if pets:
    current_app.logger.req_ok(req)
    return jsonify(pets)
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Pets not found'}), 404

@pet_blueprint.route('/pet/talent', methods=['GET'])
def get_pets_by_talent():
  req = '/pet/talent GET'
  current_app.logger.req(req)

  talent = request.args.get('talent')
  current_app.logger.log_info('info', f'talent : {talent}')

  talent_to_find = TalentService.get_one_talent(talent)

  if talent_to_find:
    pets = PetService.get_pets_by_talent(talent_to_find.name)
    if pets:
      current_app.logger.req_ok(req)
      return jsonify(pets)
    
    current_app.logger.req_404(req, 'Pets not found')
    return jsonify({'error': 'Pets not found'}), 404
  
  current_app.logger.req_404(req, 'Talent not found')
  return jsonify({'error': 'Talent not found'}), 404

@pet_blueprint.route('/pet/hero', methods=['GET'])
def get_pets_by_heroname():
  req = '/pet/hero GET'
  current_app.logger.req(req)

  hero = request.args.get('hero')
  current_app.logger.log_info('info', f'hero : {hero}')
  hero_to_find = HeroService.get_one_hero(hero)

  if hero_to_find:
    pets = PetService.get_pets_by_color_or_heroname(hero_to_find['color'], hero_to_find['name'])
    if pets:
      current_app.logger.req_ok(req)
      return jsonify(pets)
    
    current_app.logger.req_404(req, 'Pets not found')
    return jsonify({'error': 'Pets not found'}), 404
  
  current_app.logger.req_404(req, 'Hero not found')
  return jsonify({'error': 'Hero not found'}), 404