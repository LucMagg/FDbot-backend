import os
import logging
from logging.handlers import RotatingFileHandler
from app.utils.strUtils import str_now

class Logger:
  def __init__(self, log_file):
    self.setup_logger(log_file)

  def setup_logger(self, log_file):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    self.logger = logging.getLogger()
    self.logger.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(log_file, maxBytes=10485760, backupCount=5, encoding='utf-8')
    file_formatter = logging.Formatter('%(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    if not any(isinstance(h, RotatingFileHandler) for h in self.logger.handlers):
      self.logger.addHandler(file_handler)

  def error_log(self, msg):
    message = f'{str_now()} {msg}'
    print(message)
    self.logger.error(message)

  def back_log(self, msg):
    message = f'{str_now()} {msg}'
    print(message)
    self.logger.info(message)

  def req(self, req):
    message = f'{str_now()} Requête {req} reçue'
    print(message)
    self.logger.info(message)

  def req_ok(self, req):
    message = f'{str_now()} Requête {req} aboutie'
    print(message)
    self.logger.info(message)

  def req_404(self, req, msg=None):
    message = ''
    if msg is not None:
      message = f' - {msg}'
    message = f'{str_now()} Requête {req} 404{message}'
    print(message)
    self.logger.info(message)

  def log_info(self, level, msg):
    message = f'{str_now()} {msg}'
    match level:
      case 'debug':
        self.logger.debug(message)
      case 'info':
        self.logger.info(message)
      case 'warning':
        self.logger.warning(message)
      case 'error':
        self.logger.error(message)
      case _:
        self.logger.info(message)