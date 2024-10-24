from bson import ObjectId
from typing import Dict, Optional
from datetime import date, datetime, timedelta


class Climb:
  def __init__(self, number: int, start_date: date, end_date: date):
    self.number = number
    self.start_date = start_date
    self.end_date = end_date

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      number = data.get('number'),
      start_date = data.get('start_date'),
      end_date = data.get('end_date')
    )

  def to_dict(self) -> Dict:
    return {
      "number": self.number,
      "start_date": self.start_date,
      "end_date": self.end_date
    } 

class Spire:
  def __init__(self, climbs: list[Climb], number: int, start_date: date=0, end_date: date=0, _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.number = number
    self.start_date = start_date
    self.end_date = end_date
    self.climbs = climbs or []

  @classmethod
  def from_dict(cls, data: Dict):
    if not data:
      return None
    return cls(
      _id = str(data.get('_id', {})) if '_id' in data else None,
      number = data.get('number'),
      start_date = data.get('start_date'),
      end_date = data.get('end_date'),
      climbs = [Climb.from_dict(climb_data) for climb_data in data.get('climbs')] if data.get('climbs') else []
    )

  def to_dict(self) -> Dict:
    return {
      "_id": str(self._id) if self._id else None,
      "number": self.number,
      "start_date": self.start_date,
      "end_date": self.end_date,
      'climbs': [climb.to_dict() for climb in self.climbs] if self.climbs else [],
    }

  def create(self, db):
    dict_to_insert = self.to_dict()
    if '_id' in dict_to_insert:
      del dict_to_insert['_id']
    result = db.spire.insert_one(dict_to_insert)
    self._id = result.inserted_id
    return self

  @staticmethod
  def read_by_id(db, spire_id):
    data = db.spire.find_one({"_id": ObjectId(spire_id)})
    return Spire.from_dict(data) if data else None
  
  @staticmethod
  def read_by_date(db, target_date):
    print(f'date : {target_date}')
    pipeline_doc = db.pipelines.find_one({'name': 'spire_by_date'})
    if not pipeline_doc:
      return None
    
    print(pipeline_doc)
    pipeline_stages = [stage.copy() for stage in pipeline_doc['pipeline']]

    for stage in pipeline_stages:
      if '$match' in stage:
        stage['$match']['start_date']['$lt'] = target_date
        stage['$match']['end_date']['$gt'] = target_date

    spire = list(db.spire.aggregate(pipeline_stages))
      
    if len(spire) > 0:
      print(spire[0])
      return Spire.from_dict(spire[0])
   
    print('create new spires')
    while True:
      last_spire = db.spire.find_one(sort=[("end_date", -1)])
        
      if last_spire:
        start_date = last_spire['end_date'] + timedelta(days=2)
        number = last_spire['number'] + 1
      else:
        start_date = datetime(2024, 10, 23, 13, 0, 0)
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
    data = db.spire.find()
    return [Spire.from_dict(d) for d in data] if data else None