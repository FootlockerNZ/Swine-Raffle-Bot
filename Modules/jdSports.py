import requests
import random
from discord_webhook import DiscordEmbed, DiscordWebhook
from time import sleep
from colorama import init
from collections import OrderedDict
from Helpers.utils import *
from Harvester import fetch
from Helpers.logger import logger
init()
log = logger().log




class JDSports:
    def __init__(self, thread_id, profile, proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion, usedCaptchas):
        print()
        self.headers = OrderedDict({
            'Host': 'nk7vfpucy5.execute-api.eu-west-1.amazonaws.com',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua': chromeVersion,
            'accept': 'text/plain, */*; q=0.01',
            'content-type': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'user-agent': userAgent,
            'sec-ch-ua-platform': '"Windows"',
            'origin': 'https://raffles.jdsports.co.nz',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://raffles.jdsports.co.nz/',
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
        if self.profile['province'].lower() == 'hawkes bay':
            self.profile['province'] == "Hawke's Bay" 
        self.entryRetries = config['entryRetries']
        self.city = ''
        if len(self.profile['suburb']) != 0:
            self.city = self.profile['suburb']
        else:
            if len(self.profile['city']) != 0:
                self.city = self.profile['city'] 
                
        self.session = requests.session()
        self.usedCaptchas = usedCaptchas
        self.profileLength = profileLength
        if len(self.profile['phone']) == 0:
            self.profile['phone'] = gen_phone()
        else:
            self.profile['phone'] = check_phone(self.profile['phone'])

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
            birthday = gen_birthday()
            if len(self.apiKey) == 0 or len(self.captchaProvider) == 0:
                if firstRun:
                    log(self.slug+'Waiting for captcha...')
                    sleep(10)

                log(self.slug+'Getting captcha...')
                firstRun = False
                try:
                    captchaToken = fetch.token('raffles.jdsports.co.nz', port=7777)
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
                    captchaToken = get_captcha(self.slug, self.captchaProvider, self.apiKey, self.raffleInfo['url'], self.timeoutDelay, self.errorDelay, self.captchaRetry, self.raffleInfo, 'v3')
                    if captchaToken != False:
                        break
                    sleep(1)                    

            data = {
                'firstName': self.profile['fname'],
                'rafflesID': self.raffleInfo['id'],
                'lastName': self.profile['lname'],
                'email': self.profile['email'],
                'paypalEmail': self.profile['email'],
                'mobile': '+64'+self.profile['phone'][1:],
                'dateofBirth': birthday,
                'shoeSize': self.sizeInfo['sizeID'],
                'shoeSizeSkuId': self.sizeInfo['skuID'],
                'address1': self.profile['street'],
                'address2': '',
                'city': self.city,
                'county': self.profile['province'].lower().title(),
                'siteCode': 'JDNZ',
                'postCode': self.profile['postcode'],
                'hostname': 'https://raffles.jdsports.co.nz',
                'sms_optin': 0,
                'email_optin': 1,
                'token': captchaToken,
            }

            
            log(self.slug+'Getting preauth link...')
            try:
                url = 'https://nk7vfpucy5.execute-api.eu-west-1.amazonaws.com/prod/save_entry'
                if self.proxies == 'Local Host':
                    r = self.session.post(url, headers=self.headers, json=data, timeout=self.timeoutDelay)
                else:
                    r = self.session.post(url, headers=self.headers, json=data, proxies=self.proxy, timeout=self.timeoutDelay)
            except:
                log(self.slug+'Failed to connect to JD Sports')
                sleep(self.errorDelay)
                continue

            
            
            if r.status_code == 202 or r.status_code == 201:
                try:
                    if r.json()['success']:
                        self.preAuth = r.json()['pre_auth']
                        log(self.slug+'Successfully got preauth link for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                        log(self.slug+'Link: '+self.preAuth)
                        log(self.slug+'Note: Make sure to complete the entry from the webhook')
                        self.sendWebhook()
                        save_entry(self.raffleInfo, self.profile, self.preAuth, '', '', '')
                        send_entry(self.raffleInfo, self.version, self.userInfo)
                        entered=True
                        break
                    else:
                        log(self.slug+'Failed to get preauth link for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                        send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to get preauth link', self.userInfo)
                except Exception as e:
                    log(self.slug+'Failed to get preauth link for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                    send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to get preauth link: '+str(e), self.userInfo)
            elif r.status_code == 403:
                if 'ERROR: The request could not be satisfied' not in r.text:
                    log(self.slug+'Failed to get preauth link for profile: {} with email: {}. [Error: Bad Captcha]'.format(self.profile['id'], self.profile['email']))
                else:
                    log(self.slug+'Failed to get preauth link for profile: {} with email: {}. [Status Code: {}] [Error: IP Ban/Server Down]'.format(self.profile['id'], self.profile['email'], str(r.status_code)))
            elif r.status_code == 203:
                log(self.slug+'Failed to get preauth link for profile: {} with email: {}. [Server Error] [Status Code: {}]'.format(self.profile['id'], self.profile['email'], str(r.status_code)))
            else:
                log(self.slug+'Failed to get preauth link for profile: {} with email: {}. [Status Code: {}]'.format(self.profile['id'], self.profile['email'], str(r.status_code)))
                send_error(self.raffleInfo, url, r.text, self.version, str(r.status_code), 'Failed to get preauth link', self.userInfo)

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
            embed = DiscordEmbed(title = ':pig:  Complete raffle entry!  :pig: ', description = self.raffleInfo['title'], color=16766336)
            embed.url = self.preAuth
            embed.set_thumbnail(url=self.raffleInfo['image'])
            embed.add_embed_field(name = 'Store', value = 'JD Sports NZ',inline = True) 
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

    