from flask import current_app
from datetime import datetime, timezone
from app.models.spire import Spire


class SpireService:
  def convert_to_utc(date_str):
    date = datetime.fromisoformat(date_str)
    return date if date.tzinfo else date.replace(tzinfo=timezone.utc)

  @staticmethod
  def get_one_spire(spire_date):
    spire_obj = Spire.read_by_date(current_app.mongo_db, SpireService.convert_to_utc(spire_date.get('date')))
    return spire_obj if spire_obj else None
  
  @staticmethod
  def get_all_spires():
    return Spire.read_all(current_app.mongo_db)
  
  @staticmethod
  def add_channel_to_spire(data):
    spire_date = SpireService.convert_to_utc(data.get('date'))
    channel_id = data.get('channel_id')
    guild = data.get('guild')

    spire_obj = Spire.add_channel(current_app.mongo_db, spire_date, channel_id, guild)
    return spire_obj if spire_obj else None
  
  @staticmethod
  def add_ranking_message_id_to_channel(data):
    spire_date = SpireService.convert_to_utc(data.get('date'))
    channel_id = data.get('channel_id')
    message_id = data.get('ranking_message_id')

    spire_obj = Spire.add_ranking_message_id(current_app.mongo_db, spire_date, channel_id, message_id)
    return spire_obj if spire_obj else None
  
  @staticmethod
  def delete_ranking_message_id_from_channel(data):
    spire_date = SpireService.convert_to_utc(data.get('date'))
    channel_id = data.get('channel_id')

    spire_obj = Spire.delete_ranking_message_id(current_app.mongo_db, spire_date, channel_id)
    return spire_obj if spire_obj else None
  
  @staticmethod
  def add_climb_details_message_id_to_channel(data):
    spire_date = SpireService.convert_to_utc(data.get('date'))
    channel_id = data.get('channel_id')
    message_id = data.get('climb_details_message_id')

    spire_obj = Spire.add_climb_details_message_id(current_app.mongo_db, spire_date, channel_id, message_id)
    return spire_obj if spire_obj else None
  
  @staticmethod
  def delete_climb_details_message_id_from_channel(data):
    spire_date = SpireService.convert_to_utc(data.get('date'))
    channel_id = data.get('channel_id')

    spire_obj = Spire.delete_climb_details_message_id(current_app.mongo_db, spire_date, channel_id)
    return spire_obj if spire_obj else None
  
  @staticmethod
  def add_climb_details(date, climb_details):
    spire_date = SpireService.convert_to_utc(date)

    spire_obj = Spire.add_climb_details(current_app.mongo_db, spire_date, climb_details)
    return spire_obj if spire_obj else None