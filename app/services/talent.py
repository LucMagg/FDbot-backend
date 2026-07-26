from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.talent import Talent
from app.models.hero import Hero
from app.models.pet import Pet


class TalentService:

  @staticmethod
  def create_talent(talent_data):
    talent = Talent.from_dict(talent_data)
    return talent.create(current_app.mongo_db)

  @staticmethod
  def get_one_talent(talent_name_or_id):
    try:
      talent_obj = Talent.read_by_id(current_app.mongo_db, ObjectId(talent_name_or_id))
      return talent_obj if talent_obj else None
    except InvalidId:
      pass

    talent_obj = Talent.read_by_name(current_app.mongo_db, talent_name_or_id)
    return talent_obj if talent_obj else None
  
  @staticmethod
  def get_all_talents():
    return Talent.read_all(current_app.mongo_db)

  @staticmethod
  def get_heroes_and_pet_talents():
    heroes = Hero.read_all(current_app.mongo_db)
    pets = Pet.read_all(current_app.mongo_db)
    result = [{'name': name} for name in {talent.name for obj in heroes + pets for talent in obj.talents if talent.name and not isinstance(talent.name, int)}]
    return sorted(result, key=lambda x:x['name'])