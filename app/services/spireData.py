from flask import current_app
from datetime import datetime, timezone
from dateutil import parser
import pytesseract
import requests
import cv2
import numpy as np
from app.models.spireData import SpireData
from app.services.spire import SpireService


class SpireDataService:
  @staticmethod
  def get_spiredatas_by_username(username):
    spire_obj = SpireData.read_by_username(current_app.mongo_db, username)
    return spire_obj if spire_obj else None
  
  @staticmethod
  def get_spiredatas_by_spire_and_climb(spire, climb):
    spire_obj = SpireData.read_by_spire_and_climb(current_app.mongo_db, spire, climb)
    return spire_obj if spire_obj else None
  
  staticmethod  
  def get_spiredatas_by_spire(spire):
    spire_obj = SpireData.read_by_spire(current_app.mongo_db, spire)
    return spire_obj if spire_obj else None
  
  @staticmethod
  def get_spiredatas_by_best_scores(how_many):
    spires = sorted(SpireData.read_all(current_app.mongo_db), key=lambda x:(-x.score, x.date))
    return spires[:(how_many)]
  
  @staticmethod
  def get_all_spiredatas():
    return SpireData.read_all(current_app.mongo_db)
  
  @staticmethod
  def add_spiredata(spire_data: dict):
    if spire_data.get('score') is None:
      spire_data = SpireDataService.add_score(spire_data)
      spire_data['date'] = datetime.now(tz=timezone.utc)
      spire_data = SpireDataService.find_spire_and_climb(spire_data)

    spire_to_add = SpireData.from_dict(spire_data).to_dict()
    del spire_to_add['_id']
    if None in spire_to_add.values():
      return None
    
    result = SpireData.create(SpireData.from_dict(spire_data), current_app.mongo_db)
    if result:
      return result
    
    return None
  
  @staticmethod
  def extract_spiredata(spire_data: dict):
    if 'date' in spire_data.keys():
      spire_data['date'] = parser.parse(spire_data.get('date'))
      spire_data['date'] = spire_data['date'] if spire_data['date'].tzinfo else spire_data['date'].replace(tzinfo=timezone.utc)
    else:
      spire_data['date'] = datetime.now(tz=timezone.utc)

    extracted_data_from_pic = SpireDataService.process_pic(spire_data)
    for k in extracted_data_from_pic.keys():
      spire_data[k] = extracted_data_from_pic.get(k)
    spire_data = SpireDataService.add_score(spire_data)
    spire_data = SpireDataService.replace_tier(spire_data)
    spire_data = SpireDataService.find_spire_and_climb(spire_data)

    return SpireData.from_dict(spire_data).to_dict()

  def process_pic(spire_data):
    pytesseract.pytesseract.tesseract_cmd = f'{current_app.config.get('TESSERACT_PATH')}\\tesseract.exe'

    pic = requests.get(spire_data.get('image_url'))
    img_array = np.array(bytearray(pic.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast_enhanced = clahe.apply(gray)
    _, binary = cv2.threshold(contrast_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.medianBlur(binary, 3)

    kernel = np.ones((1,1), np.uint8)
    dilated = cv2.dilate(denoised, kernel, iterations=1)
    processed_image = cv2.erode(dilated, kernel, iterations=1)
    text = pytesseract.image_to_string(processed_image).split('\n')

    result = SpireDataService.process_extracted_text(text, spire_data)
    return result

  def process_extracted_text(text, result):
    extract_data = [
      {'key': 'climb', 'start': ['Ascension n°', 'Climb #']},
      {'key': 'tier', 'start': ['Dragonspire : niveau ', 'Dragonspire ']},
      {'key': 'floors', 'start': ['terminés x', 'Completed x']},
      {'key': 'loss', 'start': ['perdus x', 'Lost x']},
      {'key': 'turns', 'start': ['joués x', 'Taken x']},
      {'key': 'bonus', 'start' : ['gagnés x', 'Earned x']}
    ]

    for k in [e.get('key') for e in extract_data]:
      if k not in result.keys():
        result[k] = None
    
    for line in text:
      print(line)
      matched_data = next((data for data in extract_data if any(s in line for s in data.get('start'))), None)
      
      if matched_data:
        value = SpireDataService.find_value_in_line(line, matched_data.get('start'))

        if not result[matched_data['key']]:
          result[matched_data['key']] = value
          print(f"{matched_data['key']}: {value}")
    return result
  
  def find_value_in_line(line, starts):
    start = next((s for s in starts if s in line), None)
    to_return = line.split(start)[-1].split()[0].replace('#','')
    try:
      return int(to_return)
    except ValueError:
      return to_return
  
  def add_score(result):
    if not None in [result.get('floors'), result.get('loss'), result.get('turns'), result.get('bonus')]:
      result['score'] = result['floors'] * 50000 - result['loss'] * 1000 - result['turns'] * 100 + result['bonus'] * 250
    return result

  def replace_tier(result):
    data_to_replace = [
      {'match': 'Platine', 'replace': 'Platinum'},
      {'match': 'Or', 'replace': 'Gold'},
      {'match': 'Argent', 'replace': 'Silver'},
      {'match': 'Héros', 'replace': 'Hero'},
      {'match': 'Aventurier', 'replace': 'Adventurer'}
    ]

    if result.get('tier'):
      matched_data = next((data for data in data_to_replace if result.get('tier').lower() == data.get('match').lower()), None)
      if matched_data:
        result['tier'] = matched_data.get('replace')
    return result
  
  def find_spire_and_climb(result):
    spires = [spire.to_dict() for spire in SpireService.get_all_spires()]

    matched_spire = next((spire for spire in spires if spire.get('start_date') <= result.get('date') < spire.get('end_date')), None)
    if matched_spire:
      result['spire'] = matched_spire.get('number')

      found_climb = next((c.get('number') for c in matched_spire.get('climbs') if c.get('start_date') <= result.get('date') < c.get('end_date')), None)
      if not result.get('climb'):
        result['climb'] = found_climb
    
    return result

  def get_guilds():
    guilds = SpireData.get_all_guilds(current_app.mongo_db)
    return guilds if guilds else None

  def get_scores(score_data):
    if score_data.get('type') == 'all_time':
      return SpireDataService.get_all_time_rankings()
    return SpireDataService.get_current_spire_rankings(score_data)
  
  def get_current_spire_rankings(score_data):
    if 'date' in score_data.keys():
      score_data['date'] = parser.parse(score_data.get('date'))
      score_data['date'] = score_data['date'] if score_data['date'].tzinfo else score_data['date'].replace(tzinfo=timezone.utc)
    else:
      score_data['date'] = datetime.now(tz=timezone.utc)
    score_data = SpireDataService.find_spire_and_climb(score_data)
    
    current_climb_data = SpireDataService.get_spiredatas_by_spire_and_climb(spire=score_data.get('spire'), climb=score_data.get('climb'))
    current_spire_data = SpireDataService.get_spiredatas_by_spire(spire=score_data.get('spire'))

    to_return = {'climb': score_data.get('climb'), 'spire': score_data.get('spire')}
    to_return['current_climb'] = SpireDataService.calc_scores(current_climb_data, score_data)
    if current_climb_data == current_spire_data:
      return to_return
    
    to_return['current_spire'] = SpireDataService.calc_scores(current_spire_data, score_data)
    return to_return
  
  def calc_scores(input_list, score_data):
    if input_list is None:
      return None
    
    to_return = {}
    group_by_tier = SpireDataService.group_spiredata_tiers(input_list)
    for tier_group in group_by_tier:
      group_scores_by_username = SpireDataService.group_scores(tier_group)

      if score_data.get('type') == 'guild':
        to_return[tier_group[0].get('tier')] = SpireDataService.group_spiredata_tiers_by_guild(group_scores_by_username, top_count=3) #ICI est paramétré le nombre max de participants par tier
      else:
        to_return[tier_group[0].get('tier')] = group_scores_by_username
    return to_return

  def group_spiredata_tiers(input_list):
    to_return = {}
    for item in input_list:
      key_item = item.get('tier')
      if key_item not in to_return:
        to_return[key_item] = []
      to_return[key_item].append(item)
    return [to_return[key_item] for key_item in to_return.keys()]
  
  def group_spiredata_tiers_by_guild(input_list, top_count):
    groups = {}
    for item in input_list:
      guild = item.get('guild')
      if guild not in groups:
        groups[guild] = []
      groups[guild].append(item)
    
    to_return = []
    for guild, guild_items in groups.items():
      sorted_items = sorted(guild_items, key=lambda x: x.get('score'), reverse=True)
      top_items = sorted_items[:top_count] if len(sorted_items) >= top_count else sorted_items

      if top_items:
        to_return.append({
          'guild': guild,
          'score': sum(item.get('score') for item in top_items)
        })
    return sorted(to_return, key=lambda x: -x.get('score'))
  
  def group_scores(input_list):
    users = {}
    for item in input_list:
      username = item.get('username')
      if username not in users:
        users[username] = {
            'username': username,
            'score': item.get('score'),
            'guild': item.get('guild'),
        }
      else:
        users[username]['score'] += item.get('score')
    return sorted(list(users.values()), key=lambda x: -x.get('score'))