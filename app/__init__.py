from flask import Flask
from config import config
from .utils.pipelines import init_pipelines
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


def create_app(config_name='default'):
  app = Flask(__name__)
  app.config.from_object(config[config_name])

  init_mongo(app)

  with app.app_context():
    init_collections()
    init_pipelines()

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

  return app