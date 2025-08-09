from bson import ObjectId
from typing import Dict, Optional, List

class Replay:
  def __init__(self, player: str, link: str):
    self.player = player
    self.link = link

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      player=data.get('player'),
      link=data.get('link'),
    )

  def to_dict(self) -> Dict:
    return {
      "player": self.player,
      "link": self.link
    }

class LevelReplay:
  def __init__(self, name: str, replays: List[Replay]):
    self.name = name
    self.replays = replays

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      name=data.get('name'),
      replays=[Replay.from_dict(replay) for replay in data.get('replays', []) if isinstance(replay, dict)],
    )

  def to_dict(self) -> Dict:
    return {
      "name": self.name,
      "replays": [replay.to_dict() for replay in self.replays]
    }

  def add_replay(self, player: str, link: str):
    for replay in self.replays:
      if replay.player == player and replay.link == link:
        return
    self.replays.append(Replay(player, link))


class EventReplays:
  def __init__(self, name: str, _id: Optional[str] = None, levels: Optional[List[LevelReplay]] = None):
    self._id = ObjectId(_id) if _id else None
    self.name = name
    self.level_replays = levels or []

  @classmethod
  def from_dict(cls, data: Dict):
    return cls(
      _id=str(data.get('_id')) if data.get('_id') else None,
      name=data.get('name'),
      levels=[LevelReplay.from_dict(replay_data) for replay_data in
               data.get('levels', []) if isinstance(replay_data, dict)],
    )

  def to_dict(self) -> Dict:
    event_replays = {
      "name": self.name,
      "levels": [level.to_dict() for level in self.level_replays]
    }
    if self._id:
      event_replays["_id"] = str(self._id)

    return event_replays

  def add_replay(self, db, level_name: str, player: str, replay: str):
    level = next((lev_replays for lev_replays in self.level_replays if lev_replays.name == level_name), None)
    if level:
      level.add_replay(player, replay)
    else:
      self.level_replays.append(LevelReplay(level_name, [Replay(player, replay)]))

    to_update = self.to_dict()
    del to_update['_id']

    db.replays.update_one({"name": self.name}, {"$set": to_update})
    return self

  @staticmethod
  def create(db, event_name:str, level_name: str, player: str, replay: str):
    replay = LevelReplay(level_name, [Replay(player, replay)])
    event_replays = EventReplays(event_name, None,[replay])

    db.replays.insert_one(event_replays.to_dict())
    return event_replays

  @staticmethod
  def read_by_name(db, name):
    data = db.replays.find_one({"name": name})
    return EventReplays.from_dict(data) if data else None

  @staticmethod
  def read_all(db):
    data = db.replays.find()
    return [EventReplays.from_dict(event_replays) for event_replays in data] if data else None
