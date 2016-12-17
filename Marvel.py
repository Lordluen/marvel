from bs4 import BeautifulSoup
import config as cfg
from hashlib import md5
import pandas as pd
import re
import requests
from time import time

class Marvel():
    def __init__(self, key=cfg.PUB_KEY, pkey=cfg.PRIV_KEY):
        self._key = key
        self._pkey = pkey
        self._host = cfg.HOST

    def _get_hash(self, ts):
        return md5((ts+self._pkey+self._key).encode('utf-8')).hexdigest()

    def get_character(self, name):
        ts = str(time())
        return requests.get(self._host,
                            headers={'Content-Type': 'application/json'},
                            params={'name': name,
                                    'apikey': self._key,
                                    'ts': ts,
                                    'hash': self._get_hash(ts)})

    def get_character_list_web(self, write=False):
        # Use Beutiful Soup to get all characters (does not use Marvel API)
        # set current source of characters below (this could change)
        char_source = 'https://marvel.com/characters/browse'
        char_soup = BeautifulSoup(requests.get(char_source).text, 'html.parser')
        char_list = [char.text.strip() for char in
                     char_soup.find_all(href=re.compile(r'^\/characters\/'))]
        if write:
            with open('char_list.txt', 'w') as char_file:
                for char in char_list:
                    char_file.write('{}\n'.format(char))
        return char_list

    def get_characters(self, write=True):
        # get all character ids and save this out to a file.
        chars = self.get_character_list_web(write=False)
        char_dict = {'name': chars, 'id': []}
        for char in chars:
            char_dict['id'].append(
                self.get_character(char)['data']['results'][0]['id']
            )
        char_df = pd.DataFrame().from_dict(char_dict)
        if write:
            char_df.to_csv('characters.csv', encoding='utf-8', index=False)
