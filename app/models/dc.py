from bson import ObjectId
from typing import Dict, Optional, List


class Dc:
  def __init__(self, name: str, screenshots: Optional[List[str]] = [], replays: Optional[List[str]] = [], _id: Optional[str] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.screenshots = screenshots or []
    self.replays = replays or []

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id = str(data.get('_id')) if data.get('_id') else None,
      name = data.get('name'),
      screenshots = Dc._to_list(data.get('screenshots')),
      replays = Dc._to_list(data.get('replays')),
    )

  def to_dict(self) -> Dict:
    result = {
      'name': self.name,
      'screenshots': Dc._to_list(self.screenshots),
      'replays': Dc._to_list(self.replays)
    }
    if self._id:
      result['_id'] = str(self._id)
    return result


  def create(self, db):
    existing = self.read(db, self.name)
    if existing:
      return existing.update(db, self)
    result = db.dc.insert_one(self.to_dict())
    self._id = result.inserted_id
    return self

  @staticmethod
  def read(db, level_name: str):
    data = db.dc.find_one({'name': level_name})
    return Dc.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.dc.find()
    return [Dc.from_dict(dc) for dc in data] if data else None
  
  def update(self, db, new_data):
    print(new_data.to_dict())
    for i, screenshot in enumerate(new_data.screenshots):
      if i >= len(self.screenshots):
        self.screenshots.append(screenshot)
      elif screenshot not in self.screenshots and screenshot is not None:
        self.screenshots[i] = screenshot
    self.screenshots = self.screenshots[:3]

    for replay in new_data.replays:
      if replay not in self.replays and replay is not None:
        self.replays.append(replay)
    db.dc.update_one(
      {'_id': self._id},
      {'$set': {
        'screenshots': self.screenshots,
        'replays': self.replays
      }}
    )
    return self
  
  @staticmethod
  def clear(db):
    try:
      result = db.dc.delete_many({})
      if result.deleted_count > 0:
        return {'status': 200, 'message': f'{result.deleted_count} documents deleted'}
      return {'status': 404, 'message': 'Already empty'}
    except Exception as e:
      return {'status': 500, 'message': f'Server error : {str(e)}'}

  @staticmethod
  def _to_list(val) -> list:
    if val is None:
      return []
    return val if isinstance(val, list) else [val]