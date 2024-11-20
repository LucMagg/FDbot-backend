from bson import ObjectId
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from dateutil import parser


class Channel:
  def __init__(self, discord_channel_id: float, guilds: Optional[List[str]] = None, ranking_message_id: Optional[float] = None):
    self.discord_channel_id = discord_channel_id
    self.guilds = guilds if guilds is not None else []
    self.ranking_message_id = ranking_message_id if ranking_message_id else None

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      discord_channel_id = data.get('discord_channel_id'),
      guilds = data.get('guilds', []),
      ranking_message_id = data.get('ranking_message_id')
    )
  
  def to_dict(self) -> Dict:
    return {
      'discord_channel_id': self.discord_channel_id,
      'guilds': self.guilds,
      'ranking_message_id': self.ranking_message_id
    }

class Climb:
  def __init__(self, number: int, start_date: datetime, end_date: datetime):
    self.number = number
    if isinstance(start_date, datetime):
      self.start_date = start_date if start_date.tzinfo else start_date.replace(tzinfo=datetime.timezone.utc)
    else:
      parsed_date = parser.parse(start_date)
      self.start_date = parsed_date if parsed_date.tzinfo else parsed_date.replace(tzinfo=datetime.timezone.utc)
    if isinstance(end_date, datetime):
      self.end_date = end_date if end_date.tzinfo else end_date.replace(tzinfo=datetime.timezone.utc)
    else:
      parsed_date = parser.parse(end_date)
      self.end_date = parsed_date if parsed_date.tzinfo else parsed_date.replace(tzinfo=datetime.timezone.utc)

  @classmethod
  def from_dict(cls, data: Dict):
    start_date = data.get('start_date')
    if isinstance(start_date, datetime):
      start_date = start_date if start_date.tzinfo else start_date.replace(tzinfo=datetime.timezone.utc)
    else:
      start_date = parser.parse(start_date)
      start_date = start_date if start_date.tzinfo else start_date.replace(tzinfo=datetime.timezone.utc)
    end_date = data.get('end_date')
    if isinstance(end_date, datetime):
      end_date = end_date if end_date.tzinfo else end_date.replace(tzinfo=datetime.timezone.utc)
    else:
      end_date = parser.parse(end_date)
      end_date = end_date if end_date.tzinfo else end_date.replace(tzinfo=datetime.timezone.utc)

    return cls(
      number=data.get('number'),
      start_date=start_date,
      end_date=end_date
    )

  def to_dict(self) -> Dict:
    return {
      'number': self.number,
      'start_date': self.start_date if isinstance(self.start_date, datetime) else parser.parse(self.start_date),
      'end_date': self.end_date if isinstance(self.end_date, datetime) else parser.parse(self.end_date)
    } 

class Spire:
  def __init__(self, climbs: list[Climb], number: int, start_date: datetime=0, end_date: datetime=0, channels: Optional[Channel] = [], _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.number = number
    if isinstance(start_date, datetime):
      self.start_date = start_date if start_date.tzinfo else start_date.replace(tzinfo=datetime.timezone.utc)
    else:
      parsed_date = parser.parse(start_date)
      self.start_date = parsed_date if parsed_date.tzinfo else parsed_date.replace(tzinfo=datetime.timezone.utc)
    if isinstance(end_date, datetime):
      self.end_date = end_date if end_date.tzinfo else end_date.replace(tzinfo=datetime.timezone.utc)
    else:
      parsed_date = parser.parse(end_date)
      self.end_date = parsed_date if parsed_date.tzinfo else parsed_date.replace(tzinfo=datetime.timezone.utc)
    self.channels = channels or []
    self.climbs = climbs or []

  @classmethod
  def from_dict(cls, data: Dict):
    if not data:
      return None
    start_date = data.get('start_date')
    if isinstance(start_date, datetime):
      start_date = start_date if start_date.tzinfo else start_date.replace(tzinfo=datetime.timezone.utc)
    else:
      start_date = parser.parse(start_date)
      start_date = start_date if start_date.tzinfo else start_date.replace(tzinfo=datetime.timezone.utc)
    end_date = data.get('end_date')
    if isinstance(end_date, datetime):
      end_date = end_date if end_date.tzinfo else end_date.replace(tzinfo=datetime.timezone.utc)
    else:
      end_date = parser.parse(end_date)
      end_date = end_date if end_date.tzinfo else end_date.replace(tzinfo=datetime.timezone.utc)
    return cls(
      _id = str(data.get('_id', {})) if '_id' in data else None,
      number = data.get('number'),
      start_date = start_date,
      end_date = end_date,
      channels = [Channel.from_dict(channel_data) for channel_data in data.get('channels')] if data.get('channels') else [],
      climbs = [Climb.from_dict(climb_data) for climb_data in data.get('climbs')] if data.get('climbs') else []
    )

  def to_dict(self) -> Dict:
    return {
      '_id': str(self._id) if self._id else None,
      'number': self.number,
      'start_date': self.start_date,
      'end_date': self.end_date,
      'channels': [channel.to_dict() for channel in self.channels] if self.channels else [],
      'climbs': [climb.to_dict() for climb in self.climbs] if self.climbs else []
    }

  def create(self, db):
    dict_to_insert = self.to_dict()
    if '_id' in dict_to_insert:
      del dict_to_insert['_id']
    result = db.spires.insert_one(dict_to_insert)
    self._id = result.inserted_id
    return self

  @staticmethod
  def read_by_id(db, spire_id):
    data = db.spires.find_one({"_id": ObjectId(spire_id)})
    return Spire.from_dict(data) if data else None
  
  @staticmethod
  def read_by_date(db, target_date):
    if target_date.tzinfo is None:
      target_date = target_date.replace(tzinfo=datetime.timezone.utc)

    pipeline_doc = db.pipelines.find_one({'name': 'spire_by_date'})
    if not pipeline_doc:
      return None
    
    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        stage['$match']['start_date']['$lt'] = target_date
        stage['$match']['end_date']['$gt'] = target_date

    spire = list(db.spires.aggregate(pipeline_stages))
      
    if len(spire) > 0:
      return Spire.from_dict(spire[0])
   
    while True:
      last_spire = db.spires.find_one(sort=[("end_date", -1)])
        
      if last_spire:
        start_date = last_spire['end_date'].replace(tzinfo=datetime.timezone.utc) + timedelta(days=2)
        number = last_spire['number'] + 1
      else:
        start_date = datetime(2024, 10, 23, 11, 0, 0, tzinfo=datetime.timezone.utc)
        number = 1
      end_date = start_date + timedelta(days=12)
        
      climbs = []
      for i in range(4):
        climb_start = start_date + (timedelta(days=3) * i)
        if i < 3:
          climb_end = climb_start + timedelta(days=3, seconds=-1)
        else:
          climb_end = end_date
        climbs.append(Climb(number=i+1, start_date=climb_start, end_date=climb_end))

      new_spire = Spire(climbs=climbs, start_date=start_date, end_date=end_date, number=number).create(db)
      
      if start_date <= target_date <= end_date:
        return new_spire

      if end_date > target_date:
        return None

  @staticmethod
  def read_all(db):
    data = db.spires.find()
    return [Spire.from_dict(d) for d in data] if data else None
  
  @staticmethod
  def add_channel(db, target_date, channel_id, guild):
    spire = Spire.read_by_date(db, target_date)

    channel = next((ch for ch in spire.channels if ch.discord_channel_id == channel_id), None)

    if channel:
      if guild not in channel.guilds:
        channel.guilds.append(guild)
    else:
      spire.channels.append(Channel(discord_channel_id=channel_id, guilds=[guild]))
    db.spires.update_one({'_id': spire._id}, {'$set': {k: v for k, v in spire.to_dict().items() if k != '_id'}})

    return spire

  @staticmethod
  def add_message_id(db, target_date, channel_id, message_id):
    spire = Spire.read_by_date(db, target_date)

    channel = next((ch for ch in spire.channels if ch.discord_channel_id == channel_id), None)

    if channel:
      if message_id != channel.ranking_message_id:
        channel.ranking_message_id = message_id
    else:
      return None
    db.spires.update_one({'_id': spire._id}, {'$set': {k: v for k, v in spire.to_dict().items() if k != '_id'}})

    return spire

  @staticmethod
  def delete_message_id(db, target_date, channel_id):
    spire = Spire.read_by_date(db, target_date)

    channel = next((ch for ch in spire.channels if ch.discord_channel_id == channel_id), None)

    if channel:
      channel.ranking_message_id = None
    else:
      return None
    db.spires.update_one({'_id': spire._id}, {'$set': {k: v for k, v in spire.to_dict().items() if k != '_id'}})

    return spire