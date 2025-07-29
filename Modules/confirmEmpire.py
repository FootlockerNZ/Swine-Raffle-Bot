import requests
import random
from time import sleep
from colorama import init
from collections import OrderedDict
from Helpers.utils import *
from Helpers.logger import logger
init()
log = logger().log




class EmpireConfirm:
    def __init__(self, thread_id, links, config, userAgent, chromeVersion, proxies, userInfo, profileLength):
        print()
        self.thread_id = thread_id
        self.links = links
        self.profileLength = profileLength
        self.proxies = proxies
        self.userInfo = userInfo
        self.headers = OrderedDict({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': userAgent,
            'sec-ch-ua': chromeVersion,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
        self.entryRetries = config['entryRetries']
        self.delay = config['confirmDelay']
        self.timeoutDelay = config['timeoutDelay']
        self.errorDelay = config['errorDelay']
        if len(self.delay) == 2:
            self.randomDelay = True
        else:
            self.randomDelay = False

        self.slug = '[EMPIRE SKATE] [Confirm {}] : '.format(str(self.thread_id+1))
        if self.proxies != 'Local Host':
            try:
                self.proxy = self.proxies[self.thread_id]
            except:
                try:
                    self.proxy = random.choice(self.proxies)
                except:
                    self.proxy = 'Local Host'
                    log(self.slug+'Failed to get proxy. Running Local Host')

        

    def confirm(self):
        o = 0
        while True:
            o+=1
            log(self.slug+'Confirming link...')
            try:
                if self.proxies == 'Local Host':
                    r = requests.get(self.links[self.thread_id], headers=self.headers,timeout=self.timeoutDelay)
                else:
                    r = requests.get(self.links[self.thread_id], headers=self.headers, proxies = self.proxy,timeout=self.timeoutDelay)
            except:
                log(self.slug+'Failed to connect to kmail-lists.com')
                sleep(self.errorDelay)
                continue


            if r.status_code == 200:
                log(self.slug+'Successfully confirmed entry: '+self.links[self.thread_id])
                break
            else:
                log(self.slug+'Failed to confirm entry: '+self.links[self.thread_id]+'. [Status Code: {}]'.format(str(r.status_code)))

            if self.entryRetries == o:
                break
            
            log('Sleeping {} seconds until next trying again'.format(str(self.errorDelay)))
            sleep(self.errorDelay)
            

        if self.thread_id+1 == self.profileLength:
            return

        delay = get_delay(self.randomDelay, self.delay)
        log(self.slug+'Sleeping {}s till next confirm'.format(str(delay)))
        sleep(delay)
        return