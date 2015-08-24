# -*- coding: utf-8 -*-
'''
helper.py - provides misc. helper functions
Author: Jordan

'''

import requests
import settings
from time import sleep, strftime
import logging
import os.path
from datetime import datetime
import re
import urllib2
from bs4 import BeautifulSoup


#r = requests.Session()
### Not used right now
pastebin_header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'es,ca;q=0.8,en-GB;q=0.6,en;q=0.4',
    'Cache-Control': 'max-age=0',
    'Connection':'keep-alive',
    'Host': 'pastebin.com',
    'HTTPS': 1,
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36'
}
h0 = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.89 Safari/537.36'}
###

t = 0
f = 0

def download(url, r, headers=None):
    if not headers:
        headers = None
    if headers:
        r.headers.update(headers)
    try:
        response = r.get(url).text
        t = t+1
    except requests.ConnectionError:
        logging.warn('[!] Critical Error - Cannot connect to site')
        sleep(5)
        logging.warn('[!] Retrying...')
        response = download(url, r)
    if response == "Please refresh the page to continue...":
        f = f+1
        p = f/t*100
        log("{0} Failed to access: {1} {2}%".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), url, p))
        #log(datetime.now().strftime("(%d/%m/%Y) [%H:%M:%S]")+" Failed to access: "+url+" "+p+"%")
    return response


def log(text):
    '''
    log(text): Logs message to both STDOUT and to .output_log file

    '''
    print(text)
    with open(settings.log_file, 'a') as logfile:
        logfile.write(text + '\n')


def build_tweet(paste):
    '''
    build_tweet(url, paste) - Determines if the paste is interesting and, if so, builds and returns the tweet accordingly

    '''
    tweet = None
    name = None
    if paste.match():
        tweet = paste.url
        if paste.type == 'db_dump':
            if paste.num_emails > 0:
                tweet += ' Emails: ' + str(paste.num_emails)
            if paste.num_hashes > 0:
                tweet += ' Hashes: ' + str(paste.num_hashes)
            if paste.num_hashes > 0 and paste.num_emails > 0:
                tweet += ' E/H: ' + str(round(
                    paste.num_emails / float(paste.num_hashes), 2))
            tweet += ' Keywords: ' + str(paste.db_keywords)
            ### SAVE IN OUTPUT FILE ###
            loop = True
            name = datetime.now().strftime("%d%H%M")
            if not os.path.isdir("saves"):
				try:
					os.makedirs("saves")
				except Exception:
					log("[ERROR] Failed creating \'saves\' directory")
            if os.path.isfile('saves/' + name):
                i = 0
                while loop:
                    if os.path.isfile('saves/' + name + '_' + str(i)):
                        i = i + 1
                    else:
                        name = name + '_' + str(i)
                        loop = False
            with open('saves/' + name,'w') as output_file:
                content = requests.get(paste.url)
                if 'pastebin' in paste.url:
                    url = re.sub('raw\.php\?i\=', '', paste.url)
                elif 'pastie' in paste.url:
                    url = paste.url[:-4]
                elif 'slexy' in paste.url:
                    url = re.sub('view', 'raw', paste.url)
                else:
                    url = paste.url
                soup = BeautifulSoup(urllib2.urlopen(url))
                output_file.write("python hacktivism.py -i "+name+" --map email password --site  --source "+url+'\n\n')
                output_file.write(soup.title.string.encode('utf-8')+'\n\n')
                output_file.write(content.text.encode('utf-8'))
            if paste.num_emails >= settings.EMAIL_THRESHOLD:
                log(datetime.now().strftime("(%d/%m/%Y) [%H:%M:%S]") + " Emails found: " + str(paste.num_emails) + " ---> Saving in file " + name)
            elif paste.num_hashes >= settings.HASH_THRESHOLD:
                log(datetime.now().strftime("(%d/%m/%Y) [%H:%M:%S]") + " Possible hashes found: " + str(paste.num_hashes) + " ---> Saving in file " + name)
            ###########################
        ''' elif paste.type == 'google_api':
            tweet += ' Found possible Google API key(s)'
        elif paste.type in ['cisco', 'juniper']:
            tweet += ' Possible ' + paste.type + ' configuration'
        elif paste.type == 'ssh_private':
            tweet += ' Possible SSH private key'
        elif paste.type == 'honeypot':
            tweet += ' Dionaea Honeypot Log'
        elif paste.type == 'pgp_private':
            tweet += ' Found possible PGP Private Key'
        tweet += ' #infoleak' '''

    if not name and paste.num_emails > 0:
        log(datetime.now().strftime("(%d/%m/%Y) [%H:%M:%S]") + " Emails found: " + str(paste.num_emails))
    return tweet
