from flask import Blueprint, jsonify, request, current_app
from app.services.language import LanguageService

language_blueprint = Blueprint('language', __name__)


@language_blueprint.route('/language', methods=['POST'])
def add_language():
  language_data = request.json
  new_language = LanguageService.create_language(language_data)
  return jsonify(new_language.to_dict()), 201


@language_blueprint.route('/language/<language>', methods=['GET'])
def get_language(language):
  language_obj = LanguageService.get_one_language(language)
  if language_obj:
    return jsonify(language_obj.to_dict())
  return jsonify({'error': 'Language not found'}), 404


@language_blueprint.route('/language', methods=['GET'])
def get_languages():
  req = '/language GET'
  current_app.logger.req(req)
  languages = LanguageService.get_all_languages()
  
  if languages:
    current_app.logger.req_ok(req)
    return jsonify([language.to_dict() for language in languages])
  
  current_app.logger.req_404(req)
  return jsonify({'error': 'Languages not found'}), 404