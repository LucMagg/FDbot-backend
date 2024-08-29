from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.wikiSchema import WikiSchema


class WikiSchemaService:

  @staticmethod
  def create_wikiSchema(wikiSchema_data):
    wikiSchema = WikiSchema.from_dict(wikiSchema_data)
    return wikiSchema.create(current_app.mongo_db)

  @staticmethod
  def get_one_wikiSchema(wikiSchema_name_or_id):
    try:
      wikiSchema_obj = WikiSchema.read_by_id(current_app.mongo_db, ObjectId(wikiSchema_name_or_id))
      return wikiSchema_obj if wikiSchema_obj else None
    except InvalidId:
      pass

    wikiSchema_obj = WikiSchema.read_by_name(current_app.mongo_db, wikiSchema_name_or_id)
    return wikiSchema_obj if wikiSchema_obj else None
  
  @staticmethod
  def get_all_wikiSchemas():
    return WikiSchema.read_all(current_app.mongo_db)