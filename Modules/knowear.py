import requests
import random
from discord_webhook import DiscordEmbed, DiscordWebhook
from time import sleep
from colorama import init
from collections import OrderedDict
from Helpers.utils import *
from harvester import fetch
from Helpers.logger import logger
init()
log = logger().log




class Knowear:
    def __init__(self, thread_id, profile, proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion, usedCaptchas):
        print()
        self.headers = OrderedDict({
            'Host': 'submit-form.com',
            'sec-ch-ua': chromeVersion,
            'accept': 'application/json',
            'content-type': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'user-agent': userAgent,
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://www.knowear.co',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.knowear.co/',
            'accept-language': 'en-US,en;q=0.9',
        })        
        self.raffleInfo = raffleInfo
        self.thread = thread_id + 1
        self.proxies = proxies
        self.userInfo = userInfo
        self.delay = config['entryDelay']
        if len(self.delay) == 2:
            self.randomDelay = True
        else:
            self.randomDelay = False
        self.version = VERSION
        self.timeoutDelay = config['timeoutDelay']
        self.errorDelay = config['errorDelay']
        self.webhook = config['webhook']
        self.captchaProvider = config['captchaProvider']
        self.apiKey = config['captchaKey']
        self.captchaRetry = config['captchaRetries']
        self.profile = nicify(profile)
        self.profile = check_address(self.profile)
        self.entryRetries = config['entryRetries']
        
                
        self.session = requests.session()
        self.usedCaptchas = usedCaptchas
        self.profileLength = profileLength
        if len(self.profile['phone']) == 0:
            self.profile['phone'] = gen_phone()
        else:
            self.profile['phone'] = check_phone(self.profile['phone'])

        self.size = ''
        if len(self.profile['size'].lower()) != 0:
            for i in self.raffleInfo['sizes']:
                if self.profile['size'] in i:
                    self.size = i
                    break

        self.slug = '[{}] [{}] [Entry {}] : '.format(self.raffleInfo['store'].upper(), self.raffleInfo['title'], str(self.thread))

        if len(self.size) == 0:
            if self.profile['size'].lower() != 'random':
                log(self.slug+'Could not find chosen size for profile {}. Selecting random one...'.format(self.profile['id']))
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
        if self.thread == 1:
            firstRun = True
        else:
            firstRun = False
        o = 0
        while True:
            o+=1
            entered = False
            if len(self.apiKey) == 0 or len(self.captchaProvider) == 0:
                if firstRun:
                    log(self.slug+'Waiting for captcha...')
                    sleep(10)

                log(self.slug+'Getting captcha...')
                firstRun = False
                try:
                    captchaToken = fetch.token('www.knowear.co', port=8888)
                    if captchaToken not in self.usedCaptchas:
                        log(self.slug+'Got captcha')
                        self.usedCaptchas.append(captchaToken)
                    else:
                        log(self.slug+'Captcha received has already been used')
                        sleep(self.errorDelay)
                        continue
                except:
                    log(self.slug+'Failed to get captcha')
                    sleep(self.errorDelay)
                    continue
            else:
                while True:
                    captchaToken = get_captcha(self.slug, self.captchaProvider, self.apiKey, self.raffleInfo['url'], self.timeoutDelay, self.errorDelay, self.captchaRetry, self.raffleInfo, 'v2')
                    if captchaToken != False:
                        break
                    sleep(1)                    

            instagram = gen_instagram(self.profile['fname'], self.profile['lname'], self.profile['instagram'].lower())

            data = {
                'Product': self.raffleInfo['title'],
                'First Name': self.profile['fname'],
                'Last Name': self.profile['lname'],
                'Email': self.profile['email'],
                'Phone': self.profile['phone'],
                'Address': self.profile['street']+', '+self.profile['suburb']+', '+self.profile['city']+', '+self.profile['postcode'],
                'Delivery Method': 'Ship',
                'Instagram Handle': instagram,
                'Shoe Size': self.size,
                'g-recaptcha-response': captchaToken,
            }
            
            log(self.slug+'Entering raffle...')
            try:
                url = 'https://submit-form.com/'+self.raffleInfo['id']
                if self.proxies == 'Local Host':
                    r = self.session.post(url, headers=self.headers, json=data, timeout=self.timeoutDelay)
                else:
                    r = self.session.post(url, headers=self.headers, json=data, proxies=self.proxy, timeout=self.timeoutDelay)
            except Exception as e:
                log(self.slug+'Failed to connect to Knowear')
                sleep(self.errorDelay)
                continue

            
            
            if r.status_code == 200:
                try:
                    if r.json()['Email'] == self.profile['email']:
                        log(self.slug+'Successfully entered raffle for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                        self.sendWebhook()
                        send_entry(self.raffleInfo, self.version, self.userInfo)
                        save_entry(self.raffleInfo, self.profile, '', '', '', instagram)
                        entered=True
                        break
                    else:
                        log(self.slug+'Failed to enter raffle for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                        send_error(self.raffleInfo, self.url, r.text, self.version, str(r.status_code), 'Failed to enter raffle', self.userInfo)
                except Exception as e:
                    log(self.slug+'Failed to enter raffle for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                    send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to enter raffle '+str(e), self.userInfo)
            else:
                log(self.slug+'Failed to enter raffle for profile: {} with email: {}. [Status Code: {}]'.format(self.profile['id'], self.profile['email'], str(r.status_code)))
                send_error(self.raffleInfo, self.url, r.text, self.version, str(r.status_code), 'Failed to enter raffle', self.userInfo)

            if self.entryRetries == o:
                break
            
            log('Sleeping {} seconds until next trying again'.format(str(self.errorDelay)))
            sleep(self.errorDelay)
        
        if self.thread == self.profileLength:
            return None

        delay = get_delay(self.randomDelay, self.delay)
        print()
        log('Sleeping {} seconds until next entry'.format(str(delay)))

        return delay, entered, self.usedCaptchas


    def sendWebhook(self):
        try:   
            webhook = DiscordWebhook(url=self.webhook, username = 'Swine Raffles', avatar_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png', content='Entry '+str(self.thread))
            embed = DiscordEmbed(title = ':pig:  Successfully entered raffle!  :pig: ', description = self.raffleInfo['title'], color=16761035)
            embed.set_thumbnail(url=self.raffleInfo['image'])
            embed.url = self.raffleInfo['url']
            embed.add_embed_field(name = 'Store', value = 'Knowear',inline = True) 
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