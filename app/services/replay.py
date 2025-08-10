from flask import current_app
from app.models.levelreplay import EventReplays


class ReplayService:

  @staticmethod
  def add_replay(replay_data):
    replay = EventReplays.read_by_name(current_app.mongo_db, replay_data.get('event'))
    if replay:
      event_replays = replay.add_replay(current_app.mongo_db, replay_data.get('level'), replay_data.get('player'), replay_data.get('replay'))
      return event_replays

    return EventReplays.create(current_app.mongo_db, replay_data.get('event'), replay_data.get('level'), replay_data.get('player'), replay_data.get('replay'))

  @staticmethod
  def get_replays_for_event_level(event_name, level_name):
    event_replays = EventReplays.read_by_name(current_app.mongo_db, event_name)
    current_app.logger.log_info('info', f'{level_name}')

    if event_replays is None:
      return None

    for lev_replays in event_replays.level_replays:
      current_app.logger.log_info('info', f'{lev_replays.to_dict()}')
      current_app.logger.log_info('info', f'{lev_replays.name}')
      current_app.logger.log_info('info', f'{lev_replays.name == level_name}')

    level = next((lev_replays for lev_replays in event_replays.level_replays if lev_replays.name == level_name), None)
    if level is not None:
      current_app.logger.log_info('info', f'Got level: {level.to_dict()}')

    return [lev.to_dict() for lev in level.replays] if level else None

  @staticmethod
  def get_all_levels():
    events = EventReplays.read_all(current_app.mongo_db)
    to_return = []
    for event in events:
      event_dict = dict()
      levels = [l.name for l in event.level_replays]
      event_dict["name"] = event.name
      event_dict["levels"] = levels
      to_return.append(event_dict)

    return to_return

  @staticmethod
  def get_all_event_names():
    events = EventReplays.read_all(current_app.mongo_db)
    return [event.name for event in events]
