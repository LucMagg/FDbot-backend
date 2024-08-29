from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.quality import Quality


class QualityService:

  @staticmethod
  def create_quality(quality_data):
    quality = Quality.from_dict(quality_data)
    return quality.create(current_app.mongo_db)

  @staticmethod
  def get_one_quality(quality_name_or_id):
    try:
      quality_obj = Quality.read_by_id(current_app.mongo_db, ObjectId(quality_name_or_id))
      return quality_obj if quality_obj else None
    except InvalidId:
      pass

    quality_obj = Quality.read_by_name(current_app.mongo_db, quality_name_or_id)
    return quality_obj if quality_obj else None
  
  @staticmethod
  def get_all_qualitys():
    return Quality.read_all(current_app.mongo_db)