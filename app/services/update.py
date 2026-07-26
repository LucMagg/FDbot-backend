import requests
import re
from flask import current_app
from bs4 import BeautifulSoup, NavigableString
from typing import Optional
from app.models.wikiSchema import WikiSchema
from app.models.hero import Hero
from app.models.pet import Pet
from app.models.talent import Talent
from app.models.map import Map
from app.models.grid import Grid


class HttpClient:
  api_url = 'https://friends-and-dragons.fandom.com/api.php'

  @classmethod
  def get_page(cls, page_name):
    params = {
      'action': 'parse',
      'page': page_name,
      'prop': 'text',
      'format': 'json'
    }
    r = requests.get(cls.api_url, params=params)
    r.raise_for_status()
    html = r.json()['parse']['text']['*']
    return BeautifulSoup(html, 'html.parser')
  
  @classmethod
  def get_category_members(cls, page_name):
    params = {
      'action': 'query',
      'list': 'categorymembers',
      'cmtitle': f'Category:{page_name}',
      'cmlimit': 100,
      'format': 'json'
    }
    r = requests.get(cls.api_url, params=params)
    r.raise_for_status()
    return r.json()['query']['categorymembers']
  

class Extractor:
  def extract(page, schema):
    base_selector = schema.get('base_selector')
    rows = page.select(base_selector)
    if not schema.get('no_header_skip'):
      rows = rows[1:]
    results = []
    for row in rows:
      obj = Extractor.extract_object(row, schema['fields'])
      if obj:
        results.append(obj)
    return results
  
  def extract_object(element, fields):
    obj = {}
    for field in fields:
      if field.get('attribute'):
        value = Extractor.extract_from_attribute(element, field)
      else:
        value = Extractor.extract_field(element, field)
      obj[field['name']] = value
    return obj
  
  def extract_from_attribute(element, field):
    selector = field.get('selector')
    node = element.select_one(selector) if selector else element
    if not node:
      return None
    value = node.get(field.get('attribute', ''), '')
    if field.get('transform'):
      value = Transform.apply(value, field['transform'])
    return value
  
  def extract_field(element, field):
    selector = field.get('selector')
    if selector:
      nodes = element.select(selector)
    else:
      nodes = [element]
    if not nodes:
      return None
    if field.get('multiple'):
      return Extractor.extract_multiple_nodes(nodes, field)
    return Extractor.extract_single_node(nodes[0], field)
  
  def extract_multiple_nodes(nodes, field):
    values = []
    for elem in nodes[0].contents:
      if elem.name == 'a' and not elem.find_parent('span'):
        values.append(elem.get_text(strip=True))
      elif elem.name == 'span' and 'new' in elem.get('class', []):
        values.append(elem.get_text(strip=True))
    if field.get('transform'):
      values = [Transform.apply(v, field['transform']) for v in values]
    return values
  
  def extract_single_node(node, field):
    match field.get('extract'):
      case 'columns_range':
        value = FieldParsers.parse_columns_range(node, field)
      case 'lead_bonus':
        value = FieldParsers.parse_lead(node)
      case 'gear_row':
        value = FieldParsers.parse_gear_row(node)
      case 'clean_text':
        value = FieldParsers.parse_trait_description(node)
      case _:
        selector = field.get('selector') or ''
        if selector.endswith('a[href]'):
          value = node.get('href')
        elif selector.endswith('a[title]'):
          value = node.get('title')
        else:
          value = node.get_text(strip=True)
    if field.get('transform'):
      value = Transform.apply(value, field['transform'])
    return value


class Transform:
  def apply(value, transform):
    if not value:
      return None
    match transform:
      case 'stars':
        return int(re.sub(r'[^0-9]', '', value))
      case 'int':
        return int(value)
      case 'remove_wiki_prefix':
        return value.removeprefix('/wiki/')
      

class Group:
  ascend_map = {'Basic': 'A0', '1st': 'A1', '2nd': 'A2', '3rd': 'A3', '4th': 'A4'}
  gear_meta_keys = {'name', 'ascension'}
  talent_positions = ['base', 'ascend', 'merge']
  pet_meta_keys = {'name', 'image_url'}

  def group(data, whichone):
    match whichone:
      case 'hero gear':
        return Group._gear(data)
      case 'hero talents':
        return Group._hero_talents(data)
      case 'pet talents':
        return Group._pet_talents(data)
  
  @classmethod
  def _gear(cls, data):
    result = {}
    for row in data:
      hero = row.get('name')
      if not hero:
        continue
      gear_items = [(k, v) for k, v in row.items() if k not in cls.gear_meta_keys]
      if all(not v for _, v in gear_items):
        continue
      if hero not in result:
        result[hero] = {'name': hero, 'gear': []}
      ascend = cls.ascend_map.get(row.get('ascension'))
      for key, value in gear_items:
        value = value or ''
        parts = value.strip().split(' ', 1) if value else []
        result[hero]['gear'].append({
          'ascend': ascend,
          'position': key,
          'quality': parts[0] if len(parts) > 0 else '',
          'name': parts[1] if len(parts) > 1 else ''
        })
    return list(result.values())
  
  @classmethod
  def _hero_talents(cls, data):
    result = []
    for hero in data:
      talents = []
      for pos in cls.talent_positions:
        items = hero.get(pos) or []
        for idx, name in enumerate(items, start=1):
          talents.append({'name': name, 'position': f'{pos} {idx}'})
      result.append({'name': hero.get('name'), 'talents': talents})
    return result

  @classmethod
  def _pet_talents(cls, data):
    result = []
    for pet in data:
      talents = []
      for key, value in pet.items():
        if key not in cls.pet_meta_keys:
          talents.append({'position': key, 'name': value})
      result.append({'name': pet.get('name'), 'image_url': pet.get('image_url'), 'talents': talents})
    return result


class FieldParsers:
  def parse_columns_range(node, field):
    result = {}
    count = 0
    while count < field.get('count'):
      nth = field.get('start') + (count * field.get('step'))
      value = node.select_one(f'td:nth-child({nth})')
      if value and field.get('transform_all'):
        value = Transform.apply(value.get_text(strip=True), field.get('transform_all'))
      whichone = f'{field.get('prefix')}{count}'
      result[whichone] = value
      count += 1
    return result
  
  def parse_lead(node):
    to_return = {}
    td_text = node.get_text()
    if 'att' in td_text:
      attack = td_text.split('att')[0].split('x')[1].replace(' ', '')
      to_return['attack'] = float(attack.replace(',', '.'))
    if 'def' in td_text:
      if 'att' in td_text:
        defense = td_text.split('def')[0].split('and')[1].replace(' ', '')
      else:
        defense = td_text.split('def')[0].split('x')[1].replace(' ', '')
      to_return['defense'] = float(defense.replace(',', '.'))
    spans = node.find_all('span')
    if spans:
      if len(spans) == 1:
        title = spans[0].find('a').get('title')
        if 'att' in td_text:
          to_return['color'] = title
        else:
          if 'Leader' in td_text:
            to_return['talent'] = title
            to_return['species'] = 'the leader'
          else:
            to_return['species'] = title
      elif len(spans) == 2:
        title0 = spans[0].find('a').get('title')
        title1 = spans[1].find('a').get('title')
        if 'att' in td_text:
          to_return['color'] = title0
          if ' or ' in td_text:
            to_return['extra'] = title1
          else:
            to_return['species'] = title1
        elif 'for' in td_text:
          to_return['talent'] = title0
          to_return['species'] = title1
    return to_return

  def parse_trait_description(node):
    parts = []
    for child in node.children:
      if isinstance(child, NavigableString):
        text = str(child).strip()
        if text:
          parts.append(text)
      elif child.name == 'a' and not child.find('img'):
        text = child.get_text(strip=True)
        if text:
          parts.append(text)
      elif child.name == 'span':
        img = child.find('img')
        if img:
          alt = img.get('alt') or ''
          next_a = child.find_next_sibling('a')
          if not next_a or next_a.get_text(strip=True) != alt:
            parts.append(alt)
    parts = FieldParsers._compress_parts(parts)
    text = ' '.join(parts)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
  
  def _compress_parts(parts):
    if not parts:
      return ''
    compressed = []
    i = 0
    n = len(parts)
    while i < n:
      count = 1
      current = parts[i]
      while i + count < n and parts[i + count] == current:
        count += 1
      if count > 1:
        compressed.append(f"x{count} {current}")
      else:
        compressed.append(current)
      i += count
    final = []
    for idx, part in enumerate(compressed):
      if final:
        prev = final[-1]
        if part.startswith(prev):
          part = part[len(prev):].lstrip()
      final.append(part)
    return final
  

class UpdateService:
  def update(update_type_or_id: Optional[list] = None):
    wiki_schemas = WikiSchema.read_all(current_app.mongo_db)
    schemas_to_update = [schema.to_dict() for schema in wiki_schemas if update_type_or_id is None or schema.type == update_type_or_id]
    if not schemas_to_update:
      return False
    for schema in schemas_to_update:
      current_app.logger.log_info('info', f'update {schema.get('name')}')
      match schema.get('parse_type'):
        case 'category':
          pages = [HttpClient.get_page(page.get('title')) for page in HttpClient.get_category_members(schema.get('name'))]
          for page in pages:
            UpdateService.process(page, schema)
        case None:
          page = HttpClient.get_page(schema.get('name'))
          UpdateService.process(page, schema)
    return True
  
  def process(page, schema):
    data = Extractor.extract(page, schema)
    if schema.get('follow'):
      data = UpdateService.fetch_follow(data, schema.get('follow'))
    if schema.get('group'):
      data = Group.group(data, schema.get('group'))
    UpdateService.save(schema.get('type'), data)
  
  def fetch_follow(data, follow):
    for item in data:
      sub_page_name = item.pop(follow.get('field'), None)
      if not sub_page_name:
        continue
      sub_page = HttpClient.get_page(sub_page_name)
      nodes = sub_page.select(follow.get('base_selector'))
      item[follow.get('into')] = [
        Extractor.extract_object(node, follow.get('fields', []))
        for node in nodes
      ]
    return data
  
  def save(type, data):
    match type:
      case 'hero':
        Hero.update_heroes(current_app.mongo_db, data)
      case 'pet':
        Pet.update_pets(current_app.mongo_db, data)
      case 'talent':
        Talent.update_talents(current_app.mongo_db, data)
      case 'grid':
        Grid.update(current_app.mongo_db, data)
      case 'map':
        Map.update(current_app.mongo_db, data)