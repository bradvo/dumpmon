from .Site import Site
from .Paste import Paste
from bs4 import BeautifulSoup
from . import helper
from time import sleep
from settings import SLEEP_PASTIE
import logging
import requests


class PastiePaste(Paste):
    def __init__(self, id):
        self.id = id
        self.headers = {'User-agent': 'Mozilla/5.0'}
        self.url = 'http://pastie.org/pastes/' + self.id + '/text'
        super(PastiePaste, self).__init__()


class Pastie(Site):
    def __init__(self, last_id=None):
        if not last_id:
            last_id = None
        self.ref_id = last_id
        self.BASE_URL = 'http://pastie.org'
        self.sleep = SLEEP_PASTIE
        self.session = requests.Session()
        super(Pastie, self).__init__()

    def update(self):
        '''update(self) - Fill Queue with new Pastie IDs'''
        logging.info('Retrieving Pastie ID\'s')
        results = [tag for tag in BeautifulSoup(helper.download(
            self.BASE_URL + '/pastes', self.session)).find_all('p', 'link') if tag.a]
        new_pastes = []
        if not self.ref_id:
            results = results[:60]
        for entry in results:
            paste = PastiePaste(entry.a['href'].replace(
                self.BASE_URL + '/pastes/', ''))
            # Check to see if we found our last checked URL
            if paste.id == self.ref_id:
                break
            new_pastes.append(paste)
        for entry in new_pastes[::-1]:
            logging.debug('Adding URL: ' + entry.url)
            self.put(entry)

    def get_paste_text(self, paste):
        return BeautifulSoup(helper.download(paste.url, self.session)).pre.text