from flask import current_app
from app.models.heroXp import HeroXp


class HeroXpService:

  @staticmethod
  def get_heroXp():
    return HeroXp.read_all(current_app.mongo_db)