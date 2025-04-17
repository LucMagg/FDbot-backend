from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.trait import Trait


class TraitService:

  @staticmethod
  def create_trait(trait_data):
    trait = Trait.from_dict(trait_data)
    return trait.create(current_app.mongo_db)

  @staticmethod
  def get_one_trait(trait_name_or_id):
    try:
      trait_obj = Trait.read_by_id(current_app.mongo_db, ObjectId(trait_name_or_id))
      return trait_obj if trait_obj else None
    except InvalidId:
      pass

    trait_obj = Trait.read_by_name(current_app.mongo_db, trait_name_or_id)
    return trait_obj if trait_obj else None
  
  @staticmethod
  def get_all_traits():
    return Trait.read_all(current_app.mongo_db)