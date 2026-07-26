import json, os, yaml
from pathlib import Path

class Translations:
  def __init__(self, app):
    self.app = app
    self.logger = app.logger
    self.json_path = None 
    self.yaml_paths = []
    self.sections = ['Heroes', 'Pets', 'Talents']
  
  def start(self):
    try:
      self.json_path = Path(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'default','languages.json'))
      self.yaml_paths = [Path(self.app.config.get(var)) for var in ('EN_YAML', 'FR_YAML')]
      if not self._validate_files():
        self.logger.log_info('debug', '[TRANSLATIONS] Update cancelled : missing files')
        return False
      try:
        json_data = self._load_json()
      except Exception as e:
        self.logger.log_info('debug', f'[TRANSLATIONS] Unable to read json file : {e}')
        return False
      for yp in self.yaml_paths:
        try:
          yaml_data = self._load_yaml(yp)
        except Exception as e:
          self.logger.log_info('debug', f'[TRANSLATIONS] Unable to read yaml file {yp} : {e}')
          return False
        langname = yaml_data.get('name') or yaml_data.get('code')
        self.logger.log_info('debug', f'[TRANSLATIONS] Updating {langname} language')
        add, update = self._update(json_data, yaml_data)
        self.logger.log_info('debug', f'[TRANSLATIONS] {add} items added, {update} items updated')
        try:
          self._save_json(json_data)
        except Exception as e:
          self.logger.log_info('debug', f'[TRANSLATIONS] Unable to save json file : {e}')
          return False
      return True
    except Exception as e:
      self.logger.log_info('error', f'[TRANSLATIONS] An error occured during translation file update : {e}')
      return False
    
  # Validate file helper : checks if all files exist
  def _validate_files(self):
    if not self.json_path.exists():
      self.logger.log_info('debug', f'[TRANSLATIONS] Json not found : {self.json_path}')
      return False
    if not self.json_path.is_file():
      self.logger.log_info('debug', f'[TRANSLATIONS] Json path is not a file : {self.json_path}')
      return False
    for p in self.yaml_paths:
      if not p.exists():
        self.logger.log_info('debug', f'[TRANSLATIONS] Yaml not found : {p}')
        return False
      if not p.is_file():
        self.logger.log_info('debug', f'[TRANSLATIONS] Yaml path is not a file : {p}')
        return False
    self.logger.log_info('debug', '[TRANSLATIONS] All files succefully checked')
    return True
  
  # I/O helpers
  #    Json loader
  def _load_json(self) -> list:
    with open(self.json_path, encoding='utf-8') as f:
      return json.load(f)
    
  #    Json save
  def _save_json(self, data: list) -> None:
    with open(self.json_path, 'w', encoding='utf-8') as f:
      json.dump(data, f, ensure_ascii=False, indent=2)

  #    Yaml loader
  def _load_yaml(self, path: Path) -> dict:
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)
    
  # Update json with yaml data
  def _update(self, json_data: list, yaml_data: dict) -> tuple[int, int]:
    add, update = (0, 0)
    code = (yaml_data.get('Code') or '').lower()
    yaml_translations = yaml_data.get('Translations', {})
    entry = next((e for e in json_data if e.get('Code', '').lower() == code), None)
    if entry is None:
      self.logger.log_info('debug', f'[TRANSLATIONS] Unable to find langcode {code} in json - ignored')
      return (add, update)
    
    for section in self.sections:
      yaml_section = yaml_translations.get(section)
      if not yaml_section:
        self.logger.log_info('debug', f'[TRANSLATIONS] Unable to find section {section} in yaml - ignored')
        continue
      json_section: dict = entry.setdefault('Translations', {}).setdefault(section, {})
      for key, value in yaml_section.items():
        if key not in json_section:
          add += 1
        elif json_section[key] != value:
          update += 1
        json_section[key] = value 
    return (add, update)