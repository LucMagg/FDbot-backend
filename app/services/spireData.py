from flask import current_app
from datetime import datetime
import pytesseract
import requests
import cv2
import numpy as np
from app.models.spireData import SpireData


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
    spires = sorted(SpireData.read_all(current_app.mongo_db), key=lambda x:-x.score)
    return spires[:(how_many)]
  
  @staticmethod
  def get_all_spireDatas():
    return SpireData.read_all(current_app.mongo_db)
  
  @staticmethod
  def post_SpireData(spire_data: dict):
    extracted_data_from_pic = SpireDataService.process_pic(spire_data.get('image_url'))
    for k in extracted_data_from_pic.keys():
      spire_data[k] = extracted_data_from_pic.get(k)
    spire_data['date'] = datetime.now()
    print(f'spire_data: {spire_data}')
    result = SpireData.create(SpireData.from_dict(spire_data), current_app.mongo_db)
    return result if result else None

  def process_pic(image_url):
    pytesseract.pytesseract.tesseract_cmd = f'{current_app.config.get('TESSERACT_PATH')}\\tesseract.exe'
    print(pytesseract.pytesseract.tesseract_cmd)

    response = requests.get(image_url)
    img_array = np.array(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # preprocess image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast_enhanced = clahe.apply(gray)
    _, binary = cv2.threshold(contrast_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.medianBlur(binary, 3)

    kernel = np.ones((1,1), np.uint8)
    dilated = cv2.dilate(denoised, kernel, iterations=1)
    processed_image = cv2.erode(dilated, kernel, iterations=1)
    text = pytesseract.image_to_string(processed_image).split('/n')

    result = {
      'floors': '',
      'loss': '',
      'turns': '',
      'bonus': ''
    }

    text_to_find = [
      ['floors', 'Completed x', 'terminés x'],
      ['loss', 'Lost x', 'perdus x'],
      ['turns', 'Taken x', 'joués x'],
      ['bonus', 'Earned x', 'gagnés x']
    ]

    for line in text:
      print(line)
      for to_find in text_to_find:
          for i in range(1,3):
            if (to_find[i] in line):
              to_write = line.split(to_find[i])[1]
              if ' ' in to_write:
                  to_write = to_write.split(' ')[0]
              if '\n' in to_write:
                  to_write = to_write.split('\n')[0]
              result[to_find[0]] = int(to_write)
              print(f'{to_find[0]} : {result[to_find[0]]}')
          
    result['score'] = result['floors'] * 50000 - result['loss'] * 1000 - result['turns'] * 100 + result['bonus'] * 250

    return result