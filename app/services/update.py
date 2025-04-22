import requests #type ignore
from flask import current_app
from bs4 import BeautifulSoup
from app.models.wikiSchema import WikiSchema
from app.models.hero import Hero
from app.models.pet import Pet
from app.models.talent import Talent
from app.models.trait import Trait
from app.utils.strUtils import str_to_wiki_url


base_url = 'https://friends-and-dragons.fandom.com/wiki/'


class UpdateService:

##### main function #####
  def update(update_type_or_id=None):
    wiki_schemas = WikiSchema.read_all(current_app.mongo_db)
    schemas_to_update = [schema.to_dict() for schema in wiki_schemas if update_type_or_id is None or schema.type == update_type_or_id]
    if schemas_to_update:
      for schema in schemas_to_update:
        print(f'update {schema.get('name')}')
        current_app.logger.log_info('info', f'update {schema.get('name')}')
        if 'single' in schema.get('name'):
          UpdateService.parse_single_page(schema)
        else:
          UpdateService.parse_table(schema)
      return True
    return False


##### single pages parsing (heroes or talents) #####
  def parse_single_page(schema):
    if 'hero' in schema.get('type'):
      heroes = Hero.read_all(current_app.mongo_db)
      heroes_to_update = [hero.name for hero in heroes if len(hero.gear) == 0 or len(hero.talents) == 0 or hero.stars is None]
      updated_heroes = UpdateService.parse_heroes_one_by_one(schema, heroes_to_update)
      Hero.update_heroes(current_app.mongo_db, updated_heroes)
    else:
      talents = Talent.read_all(current_app.mongo_db)
      talents_to_update = [talent.name for talent in talents if talent.description is None or talent.description == '' or talent.image_url is None or talent.image_url == '']
      updated_talents = UpdateService.parse_talents_one_by_one(talents_to_update)
      Talent.update_talents(current_app.mongo_db, updated_talents)  


##### hero's page parsing #####
  def parse_heroes_one_by_one(schema, heroes):
    to_return = []
    for hero in heroes:
      rawdata = UpdateService.grab_hero_page_data(hero)
      to_add = {'name': rawdata.h2.get_text(), 'talents': [], 'gear': [], 'attack': {}, 'defense': {}}

      for item in schema.get('data'):
        if item.get('schema') == 'portrait':
          to_search = rawdata.find('h2', string = to_add.get('name')).find_next_sibling()
        else:  
          to_search = rawdata.find('h2', string = item.get('row')).parent

        match item.get('schema'):
          case 'portrait':
            to_add[item['property']] = to_search.find('span').find('a').get('href')
            if 'wiki/Special' in to_add[item['property']]:
              to_add[item['property']] = None
          case 'text':
            found_text = UpdateService.schema_text_in_heroes_page(to_search, item.get('property').get('then'))
            if item.get('type') == 'Talents':
              to_add['talents'].append({'name': found_text, 'position': item.get('property').get('then')[1]})
            else:
              for key, value in found_text:
                to_add[key] = value
          case 'stars':
            found_stars = UpdateService.schema_text_in_heroes_page(to_search, item.get('property').get('then'))
            to_add['stars'] = found_stars.count('⭐')
          case 'AI':
            found_AI = UpdateService.schema_text_in_heroes_page(to_search, item.get('property').get('then'))
            to_add['base_IA'] = found_AI.get('AI') + ' (' + found_AI.get('AI Speed') + ')'
          case 'talents':
            bs_talents = to_search.find('h3', string = item.get('property').get('then')[0]).find_next_sibling()
            found_talents = UpdateService.schema_multi_templates(bs_talents)
            for talent, index in found_talents:
              position = item.get('property').get('then')[1] + ' ' + str(index + 1)
              to_add['talents'].append({'name': talent, 'position': position})
          case 'gear':
            bs_gear = to_search.find('h3', string = item.get('property').get('then')[0]).find_next_sibling().get_text()
            found_gear = UpdateService.split_raw_gear_to_list(bs_gear)
            for gear, index in found_gear:
              ascend = item.get('property').get('then')[1]
              position = item.get('property').get('then')[index + 2]
              splitted_gear = gear.split(' ')
              quality = splitted_gear[0]
              name = ' '.join(splitted_gear[1:])
              to_add['gear'].append({'name': name, 'position': position, 'ascend': ascend, 'quality': quality})
          case 'stats':
            text_to_search = item.get('property').get('then')[0]
            property_to_add = item.get('property').get('then')[1]
            found_text = to_search.find('h3', string = text_to_search).find_next_sibling().get_text()
            to_add[item['property']['base']][property_to_add] = int(found_text.split('(Base ')[1].split(' + Gear')[0])

      to_return.append(to_add)
    return to_return
  

##### talent's page parsing #####
  def parse_talents_one_by_one(talent_names):
    to_return = []
    raw_bs_data = UpdateService.grab_table_page_data('Traits2')
    talent_schema = WikiSchema.read_by_name(current_app.mongo_db, 'single_talent').to_dict()

    for talent in talent_names:
      to_add = {'name': talent}            
      found_talent = next((tr for tr in raw_bs_data if tr.find_all('td')[0].find('span').find('a').get('title') == talent), None)
      if found_talent:
        for item in talent_schema.get('data'):
          td = found_talent.find_all('td')[item['row']]
          match item.get('schema'):
            case 'portrait':
              to_add[item['property']] = UpdateService.schema_template(td, item['property'])
            case 'text':
              to_add[item['property']] = td.get_text().strip()
      updatable = False
      for key, value in to_add.items():
        if key != 'name' and value is not None:
          updatable = True
      if updatable:
        to_return.append(to_add)
    return to_return
  

##### trait's page parsing #####
  def parse_traits_table(schema, raw_bs_object):
    to_return = []
    for tr in raw_bs_object:
      to_add = {}
      td = tr.find_all('td')
      for item in schema.get('data'):
        match item.get('schema'):
          case 'portrait':
            to_add[item.get('property')] = UpdateService.schema_template(td[item.get('row')], item.get('property'))
          case 'text':
            to_add[item.get('property')] = td[item.get('row')].get_text().strip().strip('\n')
      to_return.append(to_add)
    return to_return


##### table page parsing #####
  def parse_table(schema):
    raw_bs_object = UpdateService.grab_table_page_data(schema.get('name'))
    #get table infos
    match schema.get('name'):
      case 'Hero_Gear':
        to_update = UpdateService.parse_hero_gear_table(schema, raw_bs_object)
      case 'Hero_Talents'|'Pet_Talents':
        to_update = UpdateService.parse_talents_table(schema, raw_bs_object)
      case 'Traits2':
        to_update = UpdateService.parse_traits_table(schema, raw_bs_object)
      case _:
        to_update = UpdateService.parse_stats_table(schema, raw_bs_object)
    #update bdd
    match schema.get('type'):
      case 'hero':
        Hero.update_heroes(current_app.mongo_db, to_update)
      case 'pet':
        if any('signature' in d for d in to_update):
          heroes_to_update = []
          for pet in to_update:
            heroes_to_update.append({'name': pet['signature'], 'pet': pet['name']})
            if pet['signature_bis'] is not None:
              heroes_to_update.append({'name': pet['signature_bis'], 'pet': pet['name']})
          Hero.update_heroes(current_app.mongo_db, heroes_to_update)
        if any('talents' in d for d in to_update):
          unique_talents = list(set(talent.get('name') for pet in to_update for talent in pet.get('talents') if talent.get('position') not in ['base', 'silver']))
          talents_to_update = UpdateService.parse_talents_one_by_one(unique_talents)
          Talent.update_talents(current_app.mongo_db, talents_to_update)
        Pet.update_pets(current_app.mongo_db, to_update)

      case 'talent':
        Talent.update_talents(current_app.mongo_db, to_update)
      
      case 'traits':
        Trait.update_traits(current_app.mongo_db, to_update)


##### Hero_Gear table parsing #####
  def parse_hero_gear_table(schema, raw_bs_object):
    to_return = []
    for tr in raw_bs_object:
      td = tr.find_all('td')
      to_add = {'gear': []}

      for item in schema.get('data'):
        match item.get('schema'):
          case 'name':
            to_add[item.get('property')] = td[item.get('row')].get_text().strip().strip('\n')
          case 'text':
            ascend = UpdateService.schema_ascend_text(td[item.get('row')])
          case 'item':
            for index, row in enumerate(item.get('row')):
              splitted_gear = td[row].get_text().strip().split(' ')
              quality = splitted_gear[0]
              name = ' '.join(splitted_gear[1:]).replace('\n', '')
              to_add['gear'].append({'ascend': ascend, 'position': item.get('property').get('then')[index], 'quality': quality, 'name': name})
      to_return.append(to_add)
    
    grouped_heroes = {}
    for hero in to_return:
      hero_name = hero.get('name')
      if hero_name not in grouped_heroes:
        grouped_heroes[hero_name] = {'name': hero_name, 'gear': []}
      grouped_heroes[hero_name]['gear'].extend(hero['gear'])
    return list(grouped_heroes.values())

##### Talents tables parsing (hero or pet) #####
  def parse_talents_table(schema, raw_bs_object):
    to_return = []
    for tr in raw_bs_object:
      td = tr.find_all('td')
      to_add = {'talents': []}

      for item in schema.get('data'):
        match item.get('schema'):
          case 'template':
            to_add[item.get('property')] = UpdateService.schema_template(td[item.get('row')], item.get('property'))
            if item.get('property') == 'name' and to_add.get(item.get('property')) == 'Upload file':
              to_add[item.get('property')] = td[item.get('row')].get_text().strip().strip('\n')
          case 'talent':
            found_talents = UpdateService.schema_multi_templates(td[item.get('row')])
            for index, talent in enumerate(found_talents):
              position = f'{item.get('property')} {str(index + 1)}'
              to_add['talents'].append({'name': talent, 'position': position})
          case 'portrait':
            to_add[item['property']] = UpdateService.schema_template(td[item.get('row')], item['property'])
          case 'pet_talent_text':
            talent = td[item.get('row')].get_text().strip().strip('\n')
            if item.get('type') == 'number':
              talent = int(talent)
            to_add['talents'].append({'name': talent, 'position': item.get('property')})
          case 'pet_full_talent':
            talent = UpdateService.schema_template(td[item.get('row')], item.get('property'))
            if talent == '':
              talent = None
            to_add['talents'].append({'name': talent, 'position': item.get('property')})
          case 'pet_merge_talents':
            for index, row in enumerate(item.get('row')):
              talent = td[row].get_text().strip().strip('\n')
              position = f'{item.get('property')} {str(index + 1)}'
              to_add['talents'].append({'name': talent, 'position': position})

      to_return.append(to_add)
    return to_return


##### Stats tables parsing (hero or pet) #####
  def parse_stats_table(schema, raw_bs_object):
    to_return = []
    for tr in raw_bs_object:
      td = tr.find_all('td')
      to_add = {}

      for item in schema.get('data'):
        match item.get('schema'):
          case 'template':
            found_text = UpdateService.schema_template(td[item.get('row')], item.get('property'))
            if found_text == '':
              found_text = None
            if item.get('type') == 'number':
              found_text = int(found_text.strip('Stars'))
            to_add[item.get('property')] = found_text
            if item.get('property') == 'name' and to_add.get(item.get('property')) == 'Upload file':
              to_add[item.get('property')] = td[item.get('row')].get_text().strip().strip('\n')
          case 'portrait':
            to_add[item['property']] = UpdateService.schema_template(td[item.get('row')], item['property'])
          case 'number':
            to_add[item.get('property')] = int(td[item.get('row')].get_text().strip().strip('\n'))
          case 'template/':
            to_add[item.get('property')] = '/'.join([span.find('a').get('title') for span in td[item.get('row')].find_all('span')])
          case 'att_def':
            if item.get('property').get('base') not in to_add.keys():
              to_add[item.get('property').get('base')] = {}
            for index, row in enumerate(item.get('row')):
              found_text = int(td[row].get_text().strip())
              to_add[item.get('property').get('base')][item.get('property').get('then')[index]] = found_text
          case 'lead':
            found_lead = UpdateService.schema_lead(td[item.get('row')])
            to_add[item.get('property')] = found_lead
      to_return.append(to_add)
    return to_return
  

##### wiki's data grab functions #####
  def grab_hero_page_data(hero_name):
    hero_slug = str_to_wiki_url(hero_name)
    url = f'{base_url}{hero_slug}'
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser').find('aside', class_ = 'type-Hero_Character')
  
  def grab_table_page_data(whichone):
    url = f'{base_url}{whichone}'
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser').find_all('tr')[1:]


##### bs objects read functions #####
  def split_raw_gear_to_list(rawstring):
    to_return = []
    current = ''
    for char in rawstring:
      if char.isupper() and current and not current[-1].isspace() and not current[-1] in ['-', '&', ':']:
        to_return.append(current)
        current = char
      elif char == chr(10):
        pass
      else:
        current += char
    if current:
      to_return.append(current)
    return to_return
  
  def schema_text_in_heroes_page(bs_object, schema_item_list):
    i = 0
    to_return = []
    while i < len(schema_item_list):
      text_to_search = schema_item_list[i]
      property_to_add = schema_item_list[i + 1]
      to_return[property_to_add] = bs_object.find('h3', string = text_to_search).find_next_sibling().get_text().strip()
      i += 2
    return to_return
   
  def schema_multi_templates(bs_object):
    spans = bs_object.find_all('span')
    to_return = []
    for span in spans:
      if hasattr(span.find('a'), 'title'):
        if 'Upload' in span.find('a').get('title'):
          to_return.append(span.next_sibling.strip().strip('\n'))
        else:
          to_return.append(span.find('a').get('title').strip().strip('\n'))
    return to_return
  
  def schema_template(bs_object, whichone):
    match whichone:
      case 'image_url':
        to_return = bs_object.find('span', {'typeof': 'mw:File/Frameless'}).find_all('a')[0].get('href')
        if 'wiki/Special' in to_return:
          to_return = None
        return to_return
      case _:
        if bs_object.find('span'):
          return bs_object.find('span').find('a').get('title').strip().strip('\n')
        return None

  def schema_ascend_text(bs_object):
    text = bs_object.get_text()
    match text:
      case 'Basic': return 'A0'
      case '1st': return 'A1'
      case '2nd': return 'A2'
      case '3rd': return 'A3'

  def schema_lead(bs_object):
    to_return = {}
    td_text = bs_object.get_text()
    
    if 'att/def' in td_text:
      to_return['attack'] = td_text.split('att')[0].split('x')[1]
      to_return['defense'] = td_text.split('att')[0].split('x')[1]
    else:
      if 'att' in td_text:
        to_return['attack'] = td_text.split('att')[0].split('x')[1]
        while ' ' in to_return['attack']:
          to_return['attack'] = to_return['attack'].replace(' ','')
        to_return['attack'] = float(to_return['attack'].replace(',','.'))
      if 'def' in td_text:
        if 'att' in td_text:
          splitted = td_text.split('att')[1]
        else:
          splitted = td_text
        to_return['defense'] = splitted.split('def')[0].split('x')[1]
        while ' ' in to_return['defense']:
          to_return['defense'] = to_return['defense'].replace(' ','')
        to_return['defense'] = float(to_return['defense'].replace(',','.'))
    
    span = bs_object.find_all('span')
    if span:
      if len(span) == 1 and 'att' in td_text:
        to_return['color'] = span[0].find('a').get('title')
      elif len(span) == 1 and not('att') in td_text:
        to_return['species'] = span[0].find('a').get('title')
      elif len(span) == 2 and 'att' in td_text:
        to_return['color'] = span[0].find('a').get('title')
        to_return['species'] = span[1].find('a').get('title')
      elif len(span) == 2 and 'for' in td_text:
        to_return['talent'] = span[0].find('a').get('title')
        to_return['species'] = span[1].find('a').get('title')
    
    return to_return