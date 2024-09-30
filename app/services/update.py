import requests #type ignore
from flask import current_app
from bs4 import BeautifulSoup
from app.models.wikiSchema import WikiSchema
from app.models.hero import Hero
from app.models.pet import Pet
from app.models.talent import Talent
from app.utils.strUtils import str_to_wiki_url, str_to_slug


base_url = 'https://friends-and-dragons.fandom.com/wiki/'


class UpdateService:

  @staticmethod
  def update_one(update_type_or_id):
    wikiSchemas = WikiSchema.read_all(current_app.mongo_db)

    to_update = []
    for schema in wikiSchemas:
      if schema.type == update_type_or_id:
        to_update.append(schema.to_dict())
    
    if to_update:
      UpdateService.update(to_update)
      return True
    else:
      return False
  

  @staticmethod
  def update_all():
    wikiSchemas = WikiSchema.read_all(current_app.mongo_db)

    to_update = []
    for schema in wikiSchemas:
      to_update.append(schema.to_dict())

    if to_update:
      UpdateService.update(to_update)
      return True
    else:
      return False
    

  @staticmethod
  def update(schemas):
    for schema in schemas:
      print(schema['name'])

      if 'single' in schema['name']:
        if 'hero' in schema['type']:
          heroes = Hero.read_all(current_app.mongo_db)
          heroes_to_update = []
          for hero in heroes:
            if len(hero.gear) == 0 or len(hero.talents) == 0 or hero.stars is None:
              heroes_to_update.append(hero.name)
          updated_array_of_dicts = UpdateService.parse_heroes_one_by_one(schema, heroes_to_update)
          Hero.update_heroes(current_app.mongo_db, updated_array_of_dicts)
        else:
          talents = Talent.read_all(current_app.mongo_db)
          talents_to_update = []
          for talent in talents:
            if talent.description is None or talent.description == '' or talent.image_url is None or talent.image_url == '':
              talents_to_update.append(talent.name)
          updated_array_of_dicts = UpdateService.parse_talents_one_by_one(schema, talents_to_update)
          Talent.update_talents(current_app.mongo_db, updated_array_of_dicts)
      else:
        url = f"{base_url}{schema['name']}"
        page = requests.get(url)
        rawdata = BeautifulSoup(page.content, 'html.parser').find_all('tr')[1:]

        updated_array_of_dicts = UpdateService.parse_table(schema, rawdata)
        match schema['type']:
          case 'hero':
            Hero.update_heroes(current_app.mongo_db, updated_array_of_dicts)
          case 'pet':
            if any('talents' in d for d in updated_array_of_dicts):
              pet_talents = []
              for pet in updated_array_of_dicts:
                if not any(pet['gold'] == talent['name'] for talent in pet_talents):
                  pet_talents.append({'name': pet['gold'], 'description': pet['gold_description']})
                del pet['gold']
                del pet['gold_description']
              
              Talent.update_talents(current_app.mongo_db, pet_talents)
            
            if any('signature' in d for d in updated_array_of_dicts):
              heroes_to_update = []
              for pet in updated_array_of_dicts:
                heroes_to_update.append({'name': pet['signature'], 'pet': pet['name']})
                if pet['signature_bis'] is not None:
                  heroes_to_update.append({'name': pet['signature_bis'], 'pet': pet['name']})
              Hero.update_heroes(current_app.mongo_db, heroes_to_update)  

            Pet.update_pets(current_app.mongo_db, updated_array_of_dicts)
          case 'talent':
            Talent.update_talents(current_app.mongo_db, updated_array_of_dicts)
        

  @staticmethod
  def parse_heroes_one_by_one(schema, heroes):
    to_return = []
    for hero in heroes:
      hero_slug = str_to_wiki_url(hero)
      url = f"{base_url}{hero_slug}"
      page = requests.get(url)
      rawdata = BeautifulSoup(page.content, 'html.parser').find('aside', class_ = 'type-Hero_Character')

      to_add = {}
      to_add['name'] = rawdata.h2.get_text()
      to_add['talents'] = []
      to_add['gear'] = []
      to_add['attack'] = {}
      to_add['defense'] = {}

      for item in schema['data']:
        if item['schema'] == 'portrait':
          to_search = rawdata.find('h2', string = to_add['name']).find_next_sibling()
        else:  
          to_search = rawdata.find('h2', string = item['row']).parent

        match item['schema']:
          case 'portrait':
            to_add[item['property']] = UpdateService.parse_HTML_to_data(to_search, item)

          case 'text':
            to_add = UpdateService.find_text_from_bs_object(to_search, to_add, item['property']['then'])
            if item['type'] == 'Talents':
              to_add['talents'].append({'name': to_add[item['property']['then'][1]], 'position': item['property']['then'][1]})
              del to_add[item['property']['then'][1]]

          case 'stars':
            to_add = UpdateService.find_text_from_bs_object(to_search, to_add, item['property']['then'])
            to_add['stars'] = to_add['stars'].count('⭐')

          case 'AI':
            to_add = UpdateService.find_text_from_bs_object(to_search, to_add, item['property']['then'])
            to_add['base_IA'] = to_add['AI'] + ' (' + to_add['AI Speed'] + ')'
            del to_add['AI']
            del to_add['AI Speed']

          case 'talents':
            raw_talents = to_search.find('h3', string = item['property']['then'][0]).find_next_sibling().get_text()
            result = UpdateService.split_str_to_list(raw_talents)

            for i in range(0, len(result)):
              position = item['property']['then'][1] + ' ' + str(i + 1)
              to_add['talents'].append({'name': result[i], 'position': position})

          case 'gear':
            raw_gear = to_search.find('h3', string = item['property']['then'][0]).find_next_sibling().get_text()
            result = UpdateService.split_str_to_list(raw_gear)

            for i in range(0, len(result)):
              ascend = item['property']['then'][1]
              position = item['property']['then'][i + 2]
              splitted_result = result[i].split(' ')
              quality = splitted_result[0]
              name = ' '.join(splitted_result[1:])

              to_add['gear'].append({'name': name, 'position': position, 'ascend': ascend, 'quality': quality})

          case 'stats':
            text_to_search = item['property']['then'][0]
            property_to_add = item['property']['then'][1]
            found_text = to_search.find('h3', string = text_to_search).find_next_sibling().get_text()
            to_add[item['property']['base']][property_to_add] = int(found_text.split('(Base ')[1].split(' + Gear')[0])

      to_return.append(to_add)
    return to_return


  @staticmethod
  def split_str_to_list(rawstring):
    result = []
    current = ''
    for char in rawstring:
      if char.isupper() and current and not current[-1].isspace() and not current[-1] in ['-', '&', ':']:
        result.append(current)
        current = char
      elif char == chr(10):
        pass
      else:
        current += char
    if current:
      result.append(current)

    to_return = []
    to_delete = False
    for elem in result:
      if 'File:' in elem:
        to_delete = True
      elif '.png' in elem:
        to_delete = False
      elif not to_delete:
        to_return.append(elem)

    return [' '.join(skill.split()) for skill in to_return]

  @staticmethod
  def find_text_from_bs_object(bs_obj, to_add, schema_item_list):
    i = 0
    while i < len(schema_item_list):
      text_to_search = schema_item_list[i]
      property_to_add = schema_item_list[i + 1]
      to_add[property_to_add] = bs_obj.find('h3', string = text_to_search).find_next_sibling().get_text()
      i += 2
    return to_add
  

  @staticmethod
  def parse_talents_one_by_one(schema, talents):
    to_return = []
    for talent in talents:
      talent_slug = str_to_wiki_url(talent)
      url = f"{base_url}{talent_slug}"
      page = requests.get(url)
      rawdata = BeautifulSoup(page.content, 'html.parser').find('main')

      to_add = {}
      for item in schema['data']:
        if item['row'] == 'h1':
          to_add['name'] = UpdateService.parse_HTML_to_data(rawdata.h1.span, item)
        else:
          match item['row']:
            case 'floatleft':
              to_search = rawdata.find('div', class_ = 'floatleft')
              if to_search:
                to_add['image_url'] = UpdateService.parse_HTML_to_data(to_search, item)
            case 'mw-parser-output':
              to_search = rawdata.find('div', class_ = 'mw-parser-output')
              if to_search:
                to_add['description'] = UpdateService.parse_HTML_to_data(to_search.p, item)
                while '  ' in to_add['description']:
                  to_add['description'] = to_add['description'].replace('  ', ' ')

                if to_add['description'][0] == ' ':
                  to_add['description'] = to_add['description'][1:]

      updatable = False        
      for key, value in to_add.items():
        if key != 'name' and value is not None:
          updatable = True

      if updatable:
        to_return.append(to_add)

    return to_return


  @staticmethod
  def parse_table(schema, rawdata):
    to_return = []

    for tr in rawdata:
      td = tr.find_all('td')
      to_add = {}
      ascend = ''
      talents = []

      for item in schema['data']:
        if type(item['row']) is list:
          if ascend == '':
            if item['type'] == 'number':
              i = 0
              to_add[item['property']['base']] = {}
              while i < len(item['row']):
                att_def_count = item['property']['then'][i]
                to_add[item['property']['base']][att_def_count] = UpdateService.parse_HTML_to_data(td[item['row'][i]], item)
                if to_add[item['property']['base']][att_def_count] is not None:
                  to_add[item['property']['base']][att_def_count] = int(to_add[item['property']['base']][att_def_count])
                i += 1
            else:
              i = 0
              while i < len(item['row']):
                property = item['property'] + ' ' + str(i + 1)
                to_add[property]= UpdateService.parse_HTML_to_data(td[item['row'][i]], item)
                i+=1
          else:
            gears = []
            i = 0
            while i < len(item['row']):
              to_add['ascend'] = ascend
              item_answer = UpdateService.parse_HTML_to_data(td[item['row'][i]], item)

              to_add['name'] = item_answer['name']
              if to_add['name'] != None:
                to_add['name'] = to_add['name'].replace('\n','')
                if to_add['name'][0] == ' ':
                  to_add['name'] = to_add['name'][1:]

              to_add['quality'] = item_answer['quality']
              gears.append({'ascend': ascend, 'name': to_add['name'], 'quality': to_add['quality'], 'position': item['property']['then'][i]})
              i += 1

        elif item['schema'] == 'lead':
          lead_answer = UpdateService.parse_HTML_to_data(td[item['row']], item)
          if lead_answer != {}:
            for key in lead_answer.keys():
              to_add[key] = lead_answer.get(key)

        elif item['schema'] == 'talent':
          if item['property'] != 'full':
            talent_list = UpdateService.parse_HTML_to_data(td[item['row']], item)

            if item['property'] == 'base':
              to_fill = 6
            else:
              to_fill = 3
            while len(talent_list) < to_fill:
              talent_list.append(None)

            i = 0
            while i < len(talent_list):
              asc = item['property'] + ' ' + str(i + 1)
              talents.append({'position': asc, 'name':talent_list[i]})
              i += 1
          else:
            if td[item['row']].get_text() != '':
              to_add['full'] = UpdateService.parse_HTML_to_data(td[item['row']], item)[0]
            else:
              to_add['full'] = None   

        else:
          if item['property'] != 'ascend':
            to_add[item['property']] = UpdateService.parse_HTML_to_data(td[item['row']], item)
            if item['type'] == 'number' and to_add[item['property']] !='' and to_add[item['property']] is not None:
              to_add[item['property']] = int(to_add[item['property']])
            if to_add[item['property']] == '':
              to_add[item['property']] = None
          else:
            ascend = UpdateService.parse_HTML_to_data(td[item['row']], item)
            match ascend:
              case 'Basic': ascend = 'A0'
              case '1st': ascend = 'A1'
              case '2nd': ascend = 'A2'
              case '3rd': ascend = 'A3'

      if schema['name']== 'Hero_Gear':
        to_update = next((h for h in to_return if h['name'] == to_add['heroname']), None)
        
        if to_update:
          to_update = next((h for h in to_return if h['name'] == to_add['heroname']), None)
          to_return.remove(to_update)

          for gear in gears:
            to_update['gear'].append({'ascend': gear['ascend'], 'position': gear['position'], 'name': gear['name'], 'quality': gear['quality']})

          to_return.append(to_update)
        else:
          items = []
          for gear in gears:
            items.append({'ascend': gear['ascend'], 'position': gear['position'], 'name': gear['name'], 'quality': gear['quality']})
          to_return.append({'name': to_add['heroname'], 'gear': items})     
                
      elif schema['name'] == 'Hero_Talents':
        to_add['talents'] = talents
        to_return.append(to_add)

      elif schema['name'] == 'Pet_Talents':
        talents = []
        keys_to_del = []
        for key in to_add.keys():
          if key not in ['name','image_url','gold_description']:
            if key == 'gold':
              talents.append({'position': key, 'name': to_add[key], 'description': to_add['gold_description']})
            else:
              talents.append({'position': key, 'name': to_add[key]})
            if key != 'gold':
              keys_to_del.append(key)
        to_add['talents'] = talents

        for key in keys_to_del:
          del to_add[key]

        to_return.append(to_add)
          
      else:
        to_return.append(to_add)
    
    return to_return


  @staticmethod
  def parse_HTML_to_data(td, schema):
    match schema['schema']:
      case 'name':
        to_return = td.get_text()
        if 'File:' in to_return: #exception du nom du perso sans image dans la table du Fandom Wiki
          to_return = td.find('a').get_text().split('File:')[1].split(' Portrait')[0]
        while '  ' in to_return:
          to_return = to_return.replace('  ',' ')
        while ' - ' in to_return:
          to_return = to_return.replace(' - ','-')
        to_return_len = int(len(to_return)/2)
        if to_return[:to_return_len] == to_return[to_return_len:]:
          to_return = to_return[:to_return_len]
        if to_return == '':
          to_return = None
        
      case 'portrait':
        to_return = td.find('a')['href']
        if 'wiki/Special' in to_return:
          to_return = None
          
      case 'a.title':
        to_return =  td.find('a')['title']
        if 'File:' in to_return:
          if 'Class' in to_return:
            to_return = to_return.split('File:Class')[1].split('.png')[0]
          else:
            to_return = to_return.split('File:Trait')[1].split('.png')[0]
        if schema['type'] == 'number':
          to_return = int(to_return)

      case 'a.title./':
        to_return = ''
        for a in td.find_all('a'):
          to_return += a['title'] + '/'
        to_return = to_return[:-1]

      case 'text':
        to_return = td.get_text()
        if '\n' in to_return:
          to_return = to_return.replace('\n','')
        to_return.replace('  ',' ')
        if to_return == '':
          to_return = None

      case 'lead':
        to_return = {}
        base_key = schema['property']
        to_return[base_key] = {}
        td_text = td.get_text()
        
        if 'att/def' in td_text:
          to_return[base_key]['attack'] = td_text.split('att')[0].split('x')[1]
          to_return[base_key]['defense'] = td_text.split('att')[0].split('x')[1]
        else:
          if 'att' in td_text:
            to_return[base_key]['attack'] = td_text.split('att')[0].split('x')[1]
            while ' ' in to_return[base_key]['attack']:
              to_return[base_key]['attack'] = to_return[base_key]['attack'].replace(' ','')
            to_return[base_key]['attack'] = float(to_return[base_key]['attack'].replace(',','.'))
          if 'def' in td_text:
            if 'att' in td_text:
              splitted = td.text.split('att')[1]
            else:
              splitted = td_text
            to_return[base_key]['defense'] = splitted.split('def')[0].split('x')[1]
            while ' ' in to_return[base_key]['defense']:
              to_return[base_key]['defense'] = to_return[base_key]['defense'].replace(' ','')
            to_return[base_key]['defense'] = float(to_return[base_key]['defense'].replace(',','.'))

        a = td.find_all('a')
        if len(a) > 0:
          if len(a) == 1 and 'att' in td_text:
            to_return[base_key]['color'] = a[0]['title']
          elif len(a) == 1 and not('att') in td_text:
            to_return[base_key]['species'] = a[0]['title']
          elif len(a) == 2 and 'att' in td_text:
            to_return[base_key]['color'] = a[0]['title']
            to_return[base_key]['species'] = a[1]['title']
          elif len(a) == 2 and 'for' in td_text:
            to_return[base_key]['talent'] = a[0]['title']
            to_return[base_key]['species'] = a[1]['title']

      case 'item':
        to_return = {}
        td_text = td.get_text()
        if td_text != '':
          to_return['quality'] = td_text.split(' ')[0]
          to_return['name'] = td_text.replace(to_return['quality'], '')
          while '  ' in to_return['name']:
            to_return['name'] = to_return['name'].replace('  ', ' ')
        else:
          to_return['name'] = None
          to_return['quality'] = None

      case 'talent':
        to_return = []
        talents = UpdateService.split_str_to_list(td.get_text())
        for talent in talents:
          talent = talent.split('1st')[0]
          talent = talent.split('2nd')[0]
          talent = talent.split('3rd')[0]
          to_return.append(talent)
        return to_return

    return to_return