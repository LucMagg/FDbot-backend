from flask import current_app
from bson.objectid import ObjectId
from bson.errors import InvalidId
from app.models.pet import Pet
from datetime import datetime


class PetService:

  @staticmethod
  def create_pet(pet_data):
    pet = Pet.from_dict(pet_data)
    return pet.create(current_app.mongo_db)

  @staticmethod
  def get_one_pet(pet_name_or_id):
    try:
      pet = Pet.read_by_id(current_app.mongo_db, ObjectId(pet_name_or_id))
    except InvalidId:
      pet = Pet.read_by_name(current_app.mongo_db, pet_name_or_id)
    return pet.to_dict() if pet else None
  
  @staticmethod
  def get_all_pets():
    return Pet.read_all(current_app.mongo_db)
  
  @staticmethod
  def get_pets_by_class(petclass):
    pets = Pet.read_by_class(current_app.mongo_db, petclass)

    if pets:
      return pets
    else:
      return None
  
  @staticmethod
  def get_pets_by_talent(talent_name):
    pets = Pet.read_by_talent(current_app.mongo_db, talent_name)

    if pets:
      return pets
    else:
      return None
    
  @staticmethod
  def get_pets_by_color_or_heroname(color, heroname):
    pets = Pet.read_by_color_or_heroname(current_app.mongo_db, color, heroname)

    if pets:
      return pets
    else:
      return None
    
  @staticmethod
  def add_comment(pet_to_comment, comment, author):
    existing_comment = next((c for c in pet_to_comment['comments'] if c['author'] == author), None)
    if existing_comment:
      existing_comment['commentaire'] = comment
      existing_comment['date'] = datetime.now()
    else:
      pet_to_comment['comments'].append({'author': author, 'commentaire': comment, 'date': datetime.now()})

    Pet.update_by_name(current_app.mongo_db, pet_to_comment['name'], pet_to_comment)