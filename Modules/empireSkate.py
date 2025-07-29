import requests
import random
from discord_webhook import DiscordEmbed, DiscordWebhook
from time import sleep
from colorama import init
from collections import OrderedDict
from Helpers.utils import *
from Helpers.logger import logger
init()
log = logger().log



class EmpireSkate:
    def __init__(self, thread_id, profile, proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion):
        print()
        self.headers = OrderedDict({
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://www.empireskate.co.nz',
            'Pragma': 'no-cache',
            'Referer': 'https://www.empireskate.co.nz/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': userAgent,
            'sec-ch-ua': chromeVersion,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
        self.version=VERSION
        self.entryRetries = config['entryRetries']
        self.raffleInfo = raffleInfo
        self.thread = thread_id + 1
        self.session = requests.session()
        self.proxies = proxies
        self.profileLength = profileLength
        self.userInfo = userInfo
        self.delay = config['entryDelay']
        if len(self.delay) == 2:
            self.randomDelay = True
        else:
            self.randomDelay = False
        self.timeoutDelay = config['timeoutDelay']
        self.errorDelay = config['errorDelay']
        self.webhook = config['webhook']
        self.profile = nicify(profile)
        self.profile = check_address(self.profile)
        if len(self.profile['phone']) == 0:
            self.profile['phone'] = gen_phone()
        else:
            self.profile['phone'] = check_phone(self.profile['phone'])
        self.slug = '[{}] [{}] [Entry {}] : '.format(self.raffleInfo['store'].upper(), self.raffleInfo['title'], str(self.thread))
        if self.profile['size'].lower() == 'random':
            self.size = random.choice(self.raffleInfo['sizes'])
        else:
            if self.profile['size'] in self.raffleInfo['sizes']:
                self.size = self.profile['size']
            else:
                log(self.slug+'Failed to find size in profile. Choosing random...')
                self.size = random.choice(self.raffleInfo['sizes'])

        self.slug = '[{}] [{} - Size {}] [Entry {}] : '.format(self.raffleInfo['store'].upper(), self.raffleInfo['title'], self.size,str(self.thread))
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
        instagram = gen_instagram(self.profile['fname'], self.profile['lname'], self.profile['instagram'].lower())
        data = {
            'g': self.raffleInfo['list_id'],
            '$fields': 'email,$first_name,$last_name,draw_shoeSize,draw_instagram,$phone_number,$consent,sms_consent',
            'email': self.profile['email'],
            '$first_name': self.profile['fname'],
            '$last_name': self.profile['lname'],
            'draw_shoeSize': self.size,
            'draw_instagram': instagram,
            '$consent[]': 'email',
            '$consent[]': 'mobile',
            '$consent[]': 'sms',
            'sms_consent': 'false',
        }
        o = 0
        while True:
            o+=1
            entered=False
            log(self.slug+'Entering raffle...')
            try:
                
                url = 'https://manage.kmail-lists.com/ajax/subscriptions/subscribe'
                if self.proxies == 'Local Host':
                    r = requests.post(url, headers=self.headers, data=data, timeout=self.timeoutDelay)
                else:
                    r = requests.post(url, headers=self.headers, data=data, proxies=self.proxy, timeout=self.timeoutDelay)
            except Exception as e:
                log(self.slug+'Failed to connect to Empire Skate')
                sleep(self.errorDelay)
                continue

            

            if r.status_code == 200:
                try:
                    if r.json()['data']['is_subscribed'] == False:
                        if r.json()['success'] and r.json()['data']['email'].lower() == self.profile['email'].lower():
                            log(self.slug+'Successfully entered raffle for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                            log(self.slug+'Note: Make sure to confirm your entry from your email')
                            self.sendWebhook()
                            save_entry(self.raffleInfo, self.profile, '', '', '', instagram)
                            send_entry(self.raffleInfo, self.version, self.userInfo)
                            entered=True
                            break
                        else:
                            log(self.slug+'Failed to enter raffle for profile: {} with email: {}. [Error: {}]'.format(self.profile['id'], self.profile['email'], r.json()['errors']))
                            send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to enter raffle', self.userInfo)
                            break
                    else:
                        log(self.slug+'Failed to enter raffle for profile: {} with email: {}. [Error: Already entered!]'.format(self.profile['id'], self.profile['email']))
                        #send_error(self.raffleInfo, url, 'Already entered!', self.version, str(r.status_code), '', self.userInfo)
                        break
                except Exception as e:
                    log(self.slug+'Failed to enter raffle for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                    send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to enter raffle: '+str(e), self.userInfo)
            else:
                try:
                    log(self.slug+'Failed to enter raffle for profile: {} with email: {}. [Error: {}]'.format(self.profile['id'], self.profile['email'], r.json()['errors']))
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
            embed.add_embed_field(name = 'Store', value = 'Empire Skate',inline = True) 
            embed.add_embed_field(name = 'Profile', value = self.profile['id'], inline = True) 
            embed.add_embed_field(name = 'Size', value = self.size, inline = True) 
            embed.add_embed_field(name = 'Email', value = '||'+self.profile['email']+'||', inline = True) 
            embed.add_embed_field(name = 'Phone', value = '||'+self.profile['phone']+'||', inline = True) 
            embed.set_footer(text='Swine Raffles (v'+self.version+')', icon_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
        except Exception as e:
            log(self.slug+'Failed to send entry webhook. Please check config.json')