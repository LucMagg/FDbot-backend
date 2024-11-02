from bson import ObjectId
from typing import Dict, Optional
from datetime import date

class SpireData:
  def __init__(self, username: str, image_url: str, climb: int, spire: int, tier: str, date: date, guild: str, score: int, floors: int, loss: int, turns: int, bonus: int, _id: Optional[str] = None):
    try:
      self._id = ObjectId(_id)
    except:
      self._id = None
    self.username = username
    self.image_url = image_url
    self.spire = spire
    self.climb = climb
    self.tier = tier
    self.date = date
    self.guild = guild
    self.score = score
    self.floors = floors
    self.loss = loss
    self.turns = turns
    self.bonus = bonus

  @classmethod
  def from_dict(cls, data: Dict):
    if not data:
      return None
    return cls(
      _id = str(data.get('_id', {})) if '_id' in data else None,
      username = data.get('username'),
      image_url = data.get('image_url'),
      spire = data.get('spire'),
      climb = data.get('climb'),
      tier = data.get('tier'),
      date = data.get('date'),
      guild = data.get('guild'),
      score = data.get('score'),
      floors = data.get('floors'),
      loss = data.get('loss'),
      turns = data.get('turns'),
      bonus = data.get('bonus')
    )

  def to_dict(self) -> Dict:
    return {
      "_id": str(self._id) if self._id else None,
      "username": self.username,
      "image_url": self.image_url,
      "spire": self.spire,
      "climb": self.climb,
      "tier": self.tier,
      "date": self.date,
      "guild": self.guild,
      "score": self.score,
      "floors": self.floors,
      "loss": self.loss,
      "turns": self.turns,
      "bonus": self.bonus
    }

  def create(self, db):
    dict_to_insert = self.to_dict()
    if '_id' in dict_to_insert:
      del dict_to_insert['_id']
    result = db.spireDatas.insert_one(dict_to_insert)
    self._id = result.inserted_id
    return self

  @staticmethod
  def read_by_id(db, spiredata_id):
    data = db.spireDatas.find({"_id": ObjectId(spiredata_id)})
    return [SpireData.from_dict(d) for d in data] if data else None
  
  @staticmethod
  def read_by_username(db, username):
    data = db.spireDatas.find({"username": username})
    return [SpireData.from_dict(d) for d in data] if data else None

  @staticmethod
  def read_all(db):
    data = db.spireDatas.find()
    return [SpireData.from_dict(d) for d in data] if data else None
  
  @staticmethod
  def get_all_guilds(db):
    pipeline_doc = db.pipelines.find_one({'name': 'existing_guilds_from_spiredata'})
    if not pipeline_doc:
      return None
    
    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    guilds = list(db.spireDatas.aggregate(pipeline_stages))
    return guilds if guilds else None