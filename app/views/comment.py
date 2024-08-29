from flask import Blueprint, jsonify, request, current_app
from app.services.hero import HeroService
from app.services.pet import PetService

comment_blueprint = Blueprint('comment', __name__)


@comment_blueprint.route('/comment', methods=['POST'])
def add_comment():
  hero_or_pet = request.args.get('hero_or_pet')
  comment = request.args.get('comment')
  author = request.args.get('author')

  print(hero_or_pet)
  print(comment)
  print(author)

  if hero_or_pet and comment:
    to_comment = HeroService.get_one_hero(hero_or_pet)
    comment_type = 'hero'
    if to_comment is None:
      to_comment = PetService.get_one_pet(hero_or_pet)
      comment_type = 'pet'
    if to_comment:
      if comment_type == 'hero':
        HeroService.add_comment(to_comment, comment, author)
      else:
        PetService.add_comment(to_comment, comment, author)
      return jsonify({'message': 'comment added and/or modified'}), 201
  
    return jsonify({'error': 'Hero or pet not found'}), 404
  return jsonify({'error': 'Hero, pet or comment missing'}), 404
