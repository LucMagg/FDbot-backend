from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.language import Language


class LanguageService:

  @staticmethod
  def create_language(language_data):
    language = Language.from_dict(language_data)
    return language.create(current_app.mongo_db)

  @staticmethod
  def get_one_language(language_name_or_id):
    try:
      language_obj = Language.read_by_id(current_app.mongo_db, ObjectId(language_name_or_id))
      return language_obj if language_obj else None
    except InvalidId:
      pass

    language_obj = Language.read_by_name(current_app.mongo_db, language_name_or_id)
    return language_obj if language_obj else None
  
  @staticmethod
  def get_all_languages():
    return Language.read_all(current_app.mongo_db)