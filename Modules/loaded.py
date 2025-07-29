import requests
import random
from collections import OrderedDict
from sys import *
from bs4 import BeautifulSoup as soup
from discord_webhook import DiscordEmbed, DiscordWebhook
from time import sleep, time
from colorama import init
from Helpers.utils import *
from Helpers.logger import logger
log = logger().log
init()



class Loaded:
    def __init__(self, thread_id, profile, proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion):
        print()
        self.headers = OrderedDict({
            'authority': 'www.research.net',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.research.net',
            'pragma': 'no-cache',
            'referer': raffleInfo['url'],
            'sec-ch-ua': chromeVersion,
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': userAgent
        })
        self.userInfo = userInfo
        self.version = VERSION
        self.raffleInfo = raffleInfo
        self.ids = raffleInfo['ids']
        self.sizeID = raffleInfo['sizeID']
        self.thread = thread_id + 1
        self.session = requests.session()
        self.proxies = proxies
        self.surveyData = ''
        self.delay = config['entryDelay']
        self.entryRetries = config['entryRetries']
        self.timeoutDelay = config['timeoutDelay']
        self.errorDelay = config['errorDelay']
        self.url = self.raffleInfo['url']
        self.webhook = config['webhook']
        self.profile = nicify(profile)
        self.profile = check_address(self.profile)
        if self.profile['city'] == 'Auckland':
            self.optionIDS = raffleInfo['optionIDAuckland'].split(' ')
        else:
            self.optionIDS = raffleInfo['optionID'].split(' ')
        self.profileLength = profileLength
        if len(self.delay) == 2:
            self.randomDelay = True
        else:
            self.randomDelay = False
        if len(self.profile['phone']) == 0:
            self.profile['phone'] = gen_phone()
        else:
            self.profile['phone'] = check_phone(self.profile['phone'])

        self.sizeInfo = ''
        if self.profile['size'].lower() == 'random' or len(self.profile['size']) == 0:
            self.sizeInfo = random.choice(self.raffleInfo['sizes'])
        else:
            for i in self.raffleInfo['sizes']:
                if self.profile['size'] in i['size']:
                    self.sizeInfo = i
                    break
        
        
        if len(self.sizeInfo) == 0:
            print()
            sel = input('Failed to find size matching profile. Do you want to continue with a random size? (y/n):  ')
            print()
            if sel.lower() == 'y':
                self.size = random.choice(self.profile['size'])
            else:
                return
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


    def getRaffle(self):
        
        o = 0
        while True:
            o+=1
            log(self.slug+'Getting raffle entry data...')
            try:
                if self.proxies == 'Local Host':
                    r = self.session.get(self.url, headers=self.headers, timeout=self.timeoutDelay)
                else:
                    r = self.session.get(self.url, headers=self.headers, proxies=self.proxy, timeout=self.timeoutDelay)
            except:
                log(self.slug+'Failed to connect to Loaded')
                sleep(self.errorDelay)
                continue
            if r.status_code == 200:
                page = soup(r.text, 'html.parser')
                try:
                    self.surveyData = page.find('input', {'name':'survey_data'})['value']
                    log(self.slug+'Successfully got raffle data')
                    break
                except Exception as e:
                    log(self.slug+'Failed to get raffle data')
                    send_error(self.raffleInfo, self.url, r.text, self.version, str(r.status_code), 'Failed to get raffle data: '+str(e), self.userInfo)
                    if self.entryRetries == o:
                        break
            else:
                log(self.slug+'Failed to get raffle page. [Status Code: {}]'.format(str(r.status_code)))
                send_error(self.raffleInfo, self.url, r.text, self.version, str(r.status_code), 'Failed to get raffle page', self.userInfo)
                if self.entryRetries == o:
                    break

            sleep(self.errorDelay)

    def enter(self):
        self.getRaffle()
        o = 0
        while True:
            o+=1
            entered = False
            instagram = gen_instagram(self.profile['fname'], self.profile['lname'], self.profile['instagram'].lower())
            log(self.slug+'Entering raffle...')
            timeSpent = random.randint(1000,50000)
            endTime = str(time()*1000).split('.')[0]
            data ={
                self.ids[0]: self.profile['fname'],
                self.ids[1]: self.profile['lname'],
                self.ids[2]: self.profile['street'],
                self.ids[3]: '',
                self.ids[4]: self.profile['suburb'],
                self.ids[5]: self.profile['city'],
                self.ids[6]: self.profile['postcode'],
                self.ids[7]: instagram,
                self.ids[8]: self.profile['email'],
                self.ids[9]: self.profile['phone'],
                self.sizeID: self.sizeInfo['variant'],
                self.optionIDS[0].split(':')[0]: self.optionIDS[0].split(':')[1],
                self.optionIDS[1].split(':')[0]: self.optionIDS[1].split(':')[1],
                'survey_data': self.surveyData,
                'response_quality_data': '{"question_info":{"qid_'+self.ids[0].split('_')[0]+'":{"number":1,"type":"contact","option_count":null,"has_other":false,"other_selected":null,"relative_position":null,"dimensions":null,"input_method":null,"is_hybrid":false},"qid_'+self.sizeID+'":{"number":2,"type":"dropdown","option_count":'+str(len(self.raffleInfo['sizes'])+1)+',"has_other":false,"other_selected":null,"relative_position":[[9,0]],"dimensions":[12,1],"input_method":null,"is_hybrid":false},"qid_'+self.optionIDS[0].split(':')[0]+'":{"number":3,"type":"single_choice_vertical","option_count":2,"has_other":false,"other_selected":null,"relative_position":[[1,0]],"dimensions":[2,1],"input_method":null,"is_hybrid":false},"qid_'+self.optionIDS[1].split(':')[0]+'":{"number":4,"type":"single_choice_vertical","option_count":4,"has_other":false,"other_selected":null,"relative_position":[[0,0]],"dimensions":[4,1],"input_method":null,"is_hybrid":false},"qid_'+str(int(self.sizeID)-1)+'":{"number":-1,"type":"presentation_text","option_count":null,"has_other":false,"other_selected":null,"relative_position":null,"dimensions":null,"input_method":null,"is_hybrid":false}},"tooltip_open_count":0,"opened_tooltip":false,"start_time":'+str(int(endTime)-int(timeSpent))+',"end_time":'+endTime+',"time_spent":'+str(timeSpent)+',"previous_clicked":false,"has_backtracked":false,"bi_voice":{}}',
                'is_previous': 'false',
                'disable_survey_buttons_on_submit': ''
            }

            try:
                if self.proxies == 'Local Host':
                    r = self.session.post(self.url, headers=self.headers, timeout=self.timeoutDelay, data=data)
                else:
                    r = self.session.post(self.url, headers=self.headers, proxies=self.proxy, timeout=self.timeoutDelay, data=data)
            except:
                log(self.slug+'Failed to connect to Loaded')
                sleep(self.errorDelay)
                continue


            if r.status_code == 200:
                if 'Thank you for entering our Raffle for the right to Purchase' in r.text or 'https://www.research.net/billing/pw/' in r.url:
                    log(self.slug+'Successfully entered raffle for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                    self.sendWebhook()
                    send_entry(self.raffleInfo, self.version, self.userInfo)
                    save_entry(self.raffleInfo, self.profile, '', '', '', instagram)
                    entered=True
                    break
                else:
                    log(self.slug+'Failed to enter raffle for profile: {} with email: {}'.format(self.profile['id'], self.profile['email']))
                    send_error(self.raffleInfo, self.url, r.text, self.version, str(r.status_code), 'Failed to enter raffle', self.userInfo)
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

        return delay, entered


    def sendWebhook(self):
        try:   
            webhook = DiscordWebhook(url=self.webhook, username = 'Swine Raffles', avatar_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png', content='Entry '+str(self.thread))
            embed = DiscordEmbed(title = ':pig:  Successfully entered raffle!  :pig: ', description = self.raffleInfo['title'], color=16761035)
            embed.set_thumbnail(url=self.raffleInfo['image'])
            embed.url = self.raffleInfo['url']
            embed.add_embed_field(name = 'Store', value = 'Loaded',inline = True) 
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
