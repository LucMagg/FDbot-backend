from flask import Blueprint, jsonify, request, current_app
from app.services.hero import HeroService
from app.services.pet import PetService

comment_blueprint = Blueprint('comment', __name__)


@comment_blueprint.route('/comment', methods=['POST'])
def add_comment():
  req = '/comment POST'
  current_app.logger.req(req)
  hero_or_pet = request.args.get('hero_or_pet')
  comment = request.args.get('comment')
  author = request.args.get('author')
  current_app.logger.log_info('info', f"arg : {hero_or_pet} | author : {author} | comment : {comment}")

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

      current_app.logger.req_ok(req)
      return jsonify({'message': 'comment added and/or modified'}), 201

    return_msg = 'Hero or pet not found'
    current_app.logger.req_404(req, return_msg)
    return jsonify({'error': return_msg}), 404
  
  return_msg = 'Hero, pet or comment missing'
  current_app.logger.req_404(req, return_msg)
  return jsonify({'error': return_msg}), 404
