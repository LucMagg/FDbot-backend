from flask import Flask
from config import config
from .utils.logger import Logger
from backup import init_backup
from .utils.collections import init_collections

from .extensions import init_mongo
from .views.dust import dust_blueprint
from .views.message import message_blueprint
from .views.talent import talent_blueprint
from .views.quality import quality_blueprint
from .views.hero import hero_blueprint
from .views.pet import pet_blueprint
from .views.wikiSchema import wikiSchema_blueprint
from .views.update import update_blueprint
from .views.comment import comment_blueprint
from .views.level import levels_blueprint
from .views.command import command_blueprint
from .views.gear import gear_blueprint
from .views.ready import ready_blueprint


def create_app(config_name='default'):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  app.logger = Logger(log_file=f'logs/{app.config.get('LOG_FILE')}')

  init_mongo(app)

  with app.app_context():
    init_backup(app)
    init_collections()

  app.register_blueprint(dust_blueprint)
  app.register_blueprint(message_blueprint)
  app.register_blueprint(talent_blueprint)
  app.register_blueprint(quality_blueprint)
  app.register_blueprint(hero_blueprint)
  app.register_blueprint(pet_blueprint)
  app.register_blueprint(wikiSchema_blueprint)
  app.register_blueprint(update_blueprint)
  app.register_blueprint(comment_blueprint)
  app.register_blueprint(levels_blueprint)
  app.register_blueprint(command_blueprint)
  app.register_blueprint(gear_blueprint)
  app.register_blueprint(ready_blueprint)

  app.logger.back_log('Application en ligne')

  return app