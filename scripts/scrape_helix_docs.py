#!/usr/local/bin/python

import requests
from bs4 import BeautifulSoup
import json

url = 'https://dev.twitch.tv/docs/api/reference'
page = requests.get(url)

soup = BeautifulSoup(page.content, 'html.parser')

doc_elems = soup.find_all('section', class_='doc-content')

endpoints = []

for doc in doc_elems[1:]:
    details = doc.find('section', class_='left-docs')
    title_tag = details.find('h2')
    reference_url = f'{url}#{title_tag["id"]}'
    description = title_tag.text.strip()

    auth_header = details.find('h3', text=lambda x: x and x.startswith('Auth'))
    auth_ul = auth_header.find_next_sibling("ul")
    if auth_ul:
        lis = auth_ul.find_all('li')
        token = lis[0].text.strip()
        if len(lis) > 1:
            scope = lis[1].find('code').text.strip()
        else:
            scope = None
    else:
        token = auth_header.find_next_sibling("p").text.strip()
        scope = None

    url_header = details.find('h3', text=lambda x: x and x.startswith('URL'))
    endpoint = url_header.find_next_sibling("p").find("code").text.strip().split(' ')
    if len(endpoint) > 1:
        method = endpoint[0]
        endpoint = endpoint[1].split('helix/')[1].split('?')[0]
    else:
        method = 'GET'
        endpoint = endpoint[0].split('helix/')[1].split('?')[0]
    if "entitlements" in endpoint:
        continue
    
    if token.lower() == 'app access token':
        token = 'AppAccess'
    else:
        token = 'OAuth'

    endpoints.append({
        'description': description,
        'endpoint': endpoint,
        'method': method,
        'reference_url': reference_url,
        'token_type': token,
        'scope': scope
    })

with open('helix_endpoints.json', 'w') as outfile:
    json.dump(endpoints, outfile, indent=4)
