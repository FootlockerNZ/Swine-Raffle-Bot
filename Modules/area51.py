import requests
import random
from collections import OrderedDict
from discord_webhook import DiscordEmbed, DiscordWebhook
from time import sleep
from colorama import init
from Helpers.logger import logger
from Helpers.utils import *
log = logger().log
init()



class Area51:
    def __init__(self, thread_id, profile, proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion):
            print()
            self.raffleInfo = raffleInfo
            self.userAgent = userAgent
            self.headers = OrderedDict({
                'authority': 'area51store.co.nz',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://area51store.co.nz',
                'referer': self.raffleInfo['url'],
                'sec-ch-ua': chromeVersion,
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': self.userAgent
            })
            provinceCode = {
                'wellington':'WLG',
                'auckland':'AUK',
                'bay of plenty':'BOP',
                'canterbury':'CAN',
                'gisborne':'GIS',
                'hawkes bay':'HKB',
                "hawke's bay":'HKB',
                'manawatu-wanganui':'MWT',
                'marlborough':'MBH',
                'nelson':'NSN',
                'northland':'NTL',
                'taranaki':'TKI',
                'tasman':'TAS',
                'waikato':'WKO',
                'west coast':'WTC',
                'otago':'OTA',
                'southland':'STL'
            }
            self.thread = thread_id + 1
            self.proxies = proxies
            self.profileLength = profileLength
            self.version = VERSION
            self.entryRetries = config['entryRetries']
            self.delay = config['entryDelay']
            if len(self.delay) == 2:
                self.randomDelay = True
            else:
                self.randomDelay = False
            self.timeoutDelay = config['timeoutDelay']
            self.errorDelay = config['errorDelay']
            self.webhook = config['webhook']
            self.userInfo = userInfo
            self.profile = nicify(profile)
            self.profile = check_address(self.profile)
            self.sizeInfo = ''
            if len(self.profile['size'].lower()) != 0:
                for i in self.raffleInfo['sizes']:
                    if self.profile['size'] in i['size']:
                        self.sizeInfo = i
                        break
            
            self.slug = '[{}] [{}] [Entry {}] : '.format(self.raffleInfo['store'].upper(), self.raffleInfo['title'], str(self.thread))
            if len(self.sizeInfo) == 0:
                if self.profile['size'].lower() != 'random':
                    log(self.slug+'Could not find chosen size for profile {}. Selecting random one...'.format(self.profile['id']))
                self.sizeInfo = random.choice(self.raffleInfo['sizes'])
            self.slug = '[{}] [{} - Size {}] [Entry {}] : '.format(self.raffleInfo['store'].upper(), self.raffleInfo['title'], self.sizeInfo['size'],str(self.thread))
            if len(self.profile['phone']) == 0:
                self.profile['phone'] = gen_phone()
            else:
                self.profile['phone'] = check_phone(self.profile['phone'])
            self.provinceCode = ''
            try:
                self.provinceCode = provinceCode[self.profile['province'].lower()]
            except:
                log(self.slug+'Failed to get province code. Please check that your province in profiles is the same as on the raffle page')
                return

            if self.proxies != 'Local Host':
                try:
                    self.proxy = self.proxies[self.thread-1]
                except:
                    try:
                        self.proxy = random.choice(self.proxies)
                    except:
                        self.proxy = 'Local Host'
                        log(self.slug+'Failed to get proxy. Running Local Host')



        

    def enter(self):
        data = {
            'variant_id': int(self.sizeInfo['variant']),
            'variant_title': self.sizeInfo['size'],
            'first_name': self.profile['fname'],
            'last_name': self.profile['lname'],
            'email': self.profile['email'],
            'phone': self.profile['phone'],
            'address': {
                'address1': self.profile['street'],
                'city': self.profile['city'],
                'first_name': self.profile['fname'],
                'last_name': self.profile['lname'],
                'province': self.profile['province'],
                'province_code': self.provinceCode,
                'country': 'New Zealand',
                'country_code': 'NZ',
                'zip': self.profile['postcode'],
            }
        }
        o = 0
        while True:
            entered = False
            log(self.slug+'Entering raffle...')
            try:
                url = 'https://area51store.co.nz/a/ps/raffle/{}'.format(self.raffleInfo['id'])
                if self.proxies == 'Local Host':
                    r = requests.post(url, headers=self.headers, json=data, timeout=self.timeoutDelay)
                else:
                    r = requests.post(url, headers=self.headers, json=data, proxies=self.proxy, timeout=self.timeoutDelay)
            except Exception as e:
                log(self.slug+'Failed to connect to Area 51')
                sleep(self.errorDelay)
                continue
            
            o+=1

            if r.status_code == 200:
                try:
                    if r.json()['message'].lower() == 'success':
                        log(self.slug+'Successfully entered raffle for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                        self.sendWebhook()
                        save_entry(self.raffleInfo, self.profile, '', '', '', '')
                        send_entry(self.raffleInfo, self.version, self.userInfo)
                        entered=True
                        break
                    else:
                        log(self.slug+'Failed to enter raffle for profile: {} with email: {}. [Error: {}]'.format(self.profile['id'], self.profile['email'], r.json()['message']))
                        if 'One email address can only' not in r.text and 'value does not match regex' not in r.text and 'Unable to attend this event' not in r.text:
                            send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to enter raffle', self.userInfo)
                        break
                except Exception as e:
                    log(self.slug+'Failed to enter raffle for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                    send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to enter raffle: '+str(e), self.userInfo)
            else:
                try:
                    log(self.slug+'Failed to enter raffle for profile: {} with email: {}. [Error: {}]'.format(self.profile['id'], self.profile['email'], r.json()['message']))
                    send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to enter raffle', self.userInfo)
                except Exception as e:
                    log(self.slug+'Failed to enter raffle for profile: {} with email: {}. [Status Code: {}]'.format(self.profile['id'], self.profile['email'], str(r.status_code)))
                    send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to enter raffle: '+str(e), self.userInfo)
            
            
            if self.entryRetries == o:    
                break

            log('Sleeping {} seconds until next trying again'.format(str(self.errorDelay)))
            sleep(self.errorDelay) 

        if self.thread == self.profileLength:
            return None

        print()
        delay = get_delay(self.randomDelay, self.delay)
        print()
        log('Sleeping {} seconds until next entry'.format(str(delay)))
        return delay, entered


    def sendWebhook(self):
        try:   
            webhook = DiscordWebhook(url=self.webhook, username = 'Swine Raffles', avatar_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png', content='Entry '+str(self.thread))
            embed = DiscordEmbed(title = ':pig:  Successfully entered raffle!  :pig: ', description = self.raffleInfo['title'], color=16761035)
            embed.set_thumbnail(url=self.raffleInfo['image'])
            embed.url = self.raffleInfo['url']
            embed.add_embed_field(name = 'Store', value = 'Area 51',inline = True) 
            embed.add_embed_field(name = 'Profile', value = self.profile['id'], inline = True) 
            embed.add_embed_field(name = 'Size', value = self.sizeInfo['size'], inline = True) 
            embed.add_embed_field(name = 'Email', value = '||'+self.profile['email']+'||', inline = True) 
            embed.add_embed_field(name = 'Phone', value = '||'+self.profile['phone']+'||', inline = True) 
            embed.set_footer(text='Swine Raffles (v'+self.version+')', icon_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
        except Exception as e:
            log(self.slug+'Failed to send entry webhook. Please check config.json')



