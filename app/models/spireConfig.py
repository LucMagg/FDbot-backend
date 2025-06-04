class SpireConfig:
  @staticmethod
  def add_one_channel(db, channel_id, type):
    result = db.spireConfigs.update_one(
      {'name': 'channels'},
      {'$addToSet': {type: channel_id}},
      upsert=True
    )
    return SpireConfig.read_all_channels(db)

  @staticmethod
  def read_all_channels(db):
    channels = db.spireConfigs.find_one({'name': 'channels'})
    if channels and '_id' in channels:
      channels['_id'] = str(channels['_id'])
      return channels
    return None
  
  @staticmethod
  def read_all_map_bonuses(db):
    map_bonuses = db.spireConfigs.find_one({'name': 'map_bonuses'})
    if map_bonuses and '_id' in map_bonuses:
      map_bonuses['_id'] = str(map_bonuses['_id'])
      return map_bonuses
    return None