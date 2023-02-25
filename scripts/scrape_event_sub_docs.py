#!/usr/local/bin/python

import pprint
import json

import requests
from bs4 import BeautifulSoup
import json

def get_type_required(soup, id):
    data = []
    header = soup.find(id=id)
    tbody = header.findNext('table').find('tbody')
    for row in tbody.find_all('tr'):
        cols = row.find_all('td')
        data.append(cols[0].text.strip())
    return data

def get_type_dict(soup, id):
    data = {}
    header = soup.find(id=id)
    tbody = header.findNext('table').find('tbody')
    for row in tbody.find_all('tr'):
        cols = row.find_all('td')
        if cols[1].find('a') and "array" in cols[2].text.strip().lower():
            next_id = cols[1].find('a')['href'][1:]
            data[cols[0].text.strip()] = {
                'description': cols[2].text.strip(),
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': get_type_dict(soup, next_id),
                    'required': get_type_required(soup, next_id)
                },
            }
        elif cols[1].find('a'):
            next_id = cols[1].find('a')['href'][1:]
            data[cols[0].text.strip()] = {
                'description': cols[2].text.strip(),
                'type': 'object',
                'properties': get_type_dict(soup, next_id),
                'required': get_type_required(soup, next_id)
            }
        else:
            data[cols[0].text.strip()] = {
                'description': cols[2].text.strip(),
                'type': cols[1].text.strip(),
            }

    return data


def get_condition_required(soup, id):
    data = []
    header = soup.find(id=id)
    tbody = header.findNext('table').find('tbody')
    for row in tbody.find_all('tr'):
        cols = row.find_all('td')
        if cols[2].text.strip().lower() == 'yes':
            data.append(cols[0].text.strip())
    return data

def get_condition_dict(soup, id):
    data = {}
    header = soup.find(id=id)
    tbody = header.findNext('table').find('tbody')
    for row in tbody.find_all('tr'):
        cols = row.find_all('td')
        key = cols[0].text.strip()
        type = cols[1].text.strip()
        required = cols[2].text.strip().lower() == 'yes'
        description = cols[3].text.strip()
        data[key] = {
            'description': description,
            'type': type,
        }
    return data

pp = pprint.PrettyPrinter(indent=4)

sub_types_url = 'https://dev.twitch.tv/docs/eventsub/eventsub-subscription-types'
sub_types_page = requests.get(sub_types_url)
reference_url = 'https://dev.twitch.tv/docs/eventsub/eventsub-reference'
reference_page = requests.get(reference_url)


sub_types_soup = BeautifulSoup(sub_types_page.content.decode('ascii','ignore'), 'html.parser')
reference_soup = BeautifulSoup(reference_page.content.decode('ascii','ignore'), 'html.parser')

# Iterate over Subscription Types Table
doc_elems = sub_types_soup.find('section', class_='text-content')
sub_tbody = doc_elems.find('table').find('tbody')
sub_rows = sub_tbody.find_all('tr')

event_api_data = []

for row in sub_rows:
    cols = row.find_all('td')
    name = cols[1].find('code').text.strip()
    if not name.startswith('channel'):
        continue
    sub_type_a = cols[0].find('a')
    sub_type = sub_type_a.text.strip()
    version = cols[2].find('code').text.strip()
    description = cols[3].text.strip()
    h3_id = sub_type_a['href'][1:]
    h3_ele = doc_elems.find('h3', id=h3_id)
    auth_p = h3_ele.findNext('h3').findNext('p')
    auth_code = auth_p.find('code')
    if auth_code:
        scope_required = auth_code.text.strip()
    else:
        scope_required = None
    #print(f'{sub_type}, {name}, {version}, {scope_required}')

    payload_h3 = h3_ele.findNext('h3').findNext('h3').findNext('h3').findNext('h3')
    payload_tbody = payload_h3.findNext('table').find('tbody')
    event_id = None
    for pr in payload_tbody.find_all('tr'):
        cols = pr.find_all('td')
        if cols[0].text.strip() == 'event':
            event_id = cols[1].find('a')['href'].split('#')[1]
            break
    
    if event_id is not None:
        event_type = {
            '$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': None,
            'title': sub_type,
            'description': description,
            'type': 'object',
            'properties': get_type_dict(reference_soup, event_id),
            'required': get_type_required(reference_soup, event_id)
        }
    else:
        event_type = None
    
    conditions_h3 = h3_ele.findNext('h3').findNext('h3')
    conditions_tbody = conditions_h3.findNext('table').find('tbody')
    condition_id = None
    for cr in conditions_tbody.find_all('tr'):
        cols = cr.find_all('td')
        if cols[0].text.strip() == 'condition':
            condition_id = cols[1].find('a')['href'].split('#')[1]
            break
    
    if condition_id is not None:
        condition = {
            '$schema': 'https://json-schema.org/draft/2020-12/schema',
            '$id': None,
            'title': f'{sub_type} request arguments',
            'description': f'Required and optional query parameters for requesting a {sub_type} event subscription',
            'type': 'object',
            'properties': get_condition_dict(reference_soup, condition_id),
            'required': get_condition_required(reference_soup, condition_id)
        }
    else:
        condition = None

    endpoint_data = {
        'subscription_type': sub_type,
        'name': name,
        'version': version,
        'description': description,
        'scope_required': scope_required,
        'event_schema': event_type,
        'condition_schema': condition
    }

    event_api_data.append(endpoint_data)

json_object = json.dumps(event_api_data, indent = 4)

with open("eventsub_subscriptions.json", "w") as outfile:
    outfile.write(json_object)
