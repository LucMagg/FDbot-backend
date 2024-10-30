from flask import current_app
from datetime import datetime
import pytesseract
import requests
import cv2
import numpy as np
from app.models.spireData import SpireData
from app.services.spire import SpireService


class SpireDataService:
  @staticmethod
  def get_spireDatas_by_username(username):
    spire_obj = SpireData.read_by_username(current_app.mongo_db, username)
    return spire_obj if spire_obj else None
  
  @staticmethod
  def get_spireDatas_by_spire_and_climb(spire, climb):
    spire_obj = SpireData.read_by_spire_and_climb(current_app.mongo_db, spire, climb)
    return spire_obj if spire_obj else None
  
  @staticmethod
  def get_spireDatas_by_best_scores(how_many):
    spires = sorted(SpireData.read_all(current_app.mongo_db), key=lambda x:(-x.score, x.date))
    return spires[:(how_many)]
  
  @staticmethod
  def get_all_spireDatas():
    return SpireData.read_all(current_app.mongo_db)
  
  @staticmethod
  def add_SpireData(spire_data: dict):
    spire_to_add = SpireData.from_dict(spire_data).to_dict()
    if None in spire_to_add.values():
      return None
    
    result = SpireData.create(SpireData.from_dict(spire_data), current_app.mongo_db)
    print('spire added')
    return result if result else None
  
  @staticmethod
  def extract_SpireData(spire_data: dict):
    spire_data['date'] = datetime.now()
    extracted_data_from_pic = SpireDataService.process_pic(spire_data)
    for k in extracted_data_from_pic.keys():
      spire_data[k] = extracted_data_from_pic.get(k)
    spire_data = SpireDataService.add_score(spire_data)
    print(spire_data)
    spire_data = SpireDataService.replace_tier(spire_data)
    print(spire_data)
    spire_data = SpireDataService.find_spire_and_climb(spire_data)
    print(spire_data)
    print(f'spire_data: {spire_data}')

    return spire_data

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
        print(matched_data)
        value = SpireDataService.find_value_in_line(line, matched_data.get('start'))

        if not result[matched_data['key']]:
          result[matched_data['key']] = value
          print(f"{matched_data['key']}: {value}")
    return result
  
  def find_value_in_line(line, starts):
    start = next((s for s in starts if s in line), None)
    print(start)
    to_return = line.split(start)[-1].split()[0].replace('#','')
    try:
      return int(to_return)
    except ValueError:
      return to_return
  
  def add_score(result):
    if not None in result.values() and not result.get('score'):
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
      matched_data = next((data for data in data_to_replace if result.get('tier') == data.get('match')), None)
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

