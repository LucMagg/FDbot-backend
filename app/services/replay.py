from flask import current_app
from app.models.levelreplay import EventReplays, LevelReplay


class ReplayService:

  @staticmethod
  def add_replay(replay_data):
    replay = EventReplays.read_by_name(current_app.mongo_db, replay_data.get('event'))
    if replay:
      event_replays = replay.add_replay(current_app.mongo_db, replay_data.get('level'), replay_data.get('replay'))
      return event_replays

    return EventReplays.create(current_app.mongo_db, replay_data)

  @staticmethod
  def get_replays_for_event_level(event_name, level_name):
    event_replays = EventReplays.read_by_name(current_app.mongo_db, event_name)
    current_app.logger.log_info('info', f'{level_name}')

    for lev_replays in event_replays.level_replays:
      current_app.logger.log_info('info', f'{lev_replays.to_dict()}')
      current_app.logger.log_info('info', f'{lev_replays.name}')
      current_app.logger.log_info('info', f'{lev_replays.name == level_name}')

    level = next((lev_replays for lev_replays in event_replays.level_replays if lev_replays.name == level_name), None)
    current_app.logger.log_info('info', f'Got level: {level.to_dict()}')

    return level.replays if level else None

  @staticmethod
  def get_all_event_names():
    events = EventReplays.read_all(current_app.mongo_db)
    return [event.name for event in events]
