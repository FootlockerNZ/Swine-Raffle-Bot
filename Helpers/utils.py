import os
import random
import subprocess
import requests
import psutil
from uuid import uuid4
from csv import writer
from discord_webhook import DiscordEmbed, DiscordWebhook
from time import sleep
from pathlib import Path
from .logger import logger
from dotenv import load_dotenv


load_dotenv()
log = logger().log

SEND_TASK_WEBHOOK = os.getenv('SEND_TASK_WEBHOOK')
SEND_ENTRY_WEBHOOK = os.getenv('SEND_ENTRY_WEBHOOK')
SEND_LOGIN_WEBHOOK = os.getenv('SEND_LOGIN_WEBHOOK')
SEND_RESET_WEBHOOK = os.getenv('SEND_RESET_WEBHOOK')
SEND_FINISH_WEBHOOK = os.getenv('SEND_FINISH_WEBHOOK')
SEND_ERROR_WEBHOOK = os.getenv('SEND_ERROR_WEBHOOK')

def t():
    print(SEND_ENTRY_WEBHOOK)

def save_entry(raffleInfo, profile, PayPalLink, entryLink, reference, instagram):
    try:
        f = open(os.path.dirname(__file__) + '\\..\\entries.csv', 'a', newline='')
        writer = writer(f)
        data = [' '+raffleInfo['store'], ' '+raffleInfo['title'], ' '+raffleInfo['url'], ' '+profile['id'], ' '+profile['email'], ' '+profile['phone'], ' '+entryLink, ' '+PayPalLink, ' '+reference, ' '+instagram]
        writer.writerow(data)
        f.close()
        return True
    except:
        return False


def send_entry(raffleInfo, version, userInfo):
    try:
        webhook = DiscordWebhook(url=SEND_ENTRY_WEBHOOK, username = 'Swine Raffles', avatar_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed = DiscordEmbed(title = ':pig:  New raffle entry!  :pig:', color=16761035)
        embed.set_thumbnail(url=raffleInfo['image'])
        embed.add_embed_field(name = 'Store', value = raffleInfo['store'], inline = True)
        embed.add_embed_field(name = 'Raffle', value = raffleInfo['title'], inline = True)
        embed.add_embed_field(name = 'User', value = userInfo['discord'], inline = True)
        embed.add_embed_field(name = 'Key', value = userInfo['licence'], inline = True)
        embed.add_embed_field(name = 'Device', value = userInfo['hardware_id'], inline = True)
        embed.set_footer(text='Swine Raffles (v'+str(version)+')', icon_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
        return True
    except Exception as e:
        try:
            send_error(raffleInfo, 'send_entry', '', version, '', str(e), userInfo)
        except:
            pass
        return False
        

def send_tasks(raffleInfo, discordName, profileLength, licence, hardware_id, version, proxies):
    try:
        webhook = DiscordWebhook(url=SEND_TASK_WEBHOOK, username = 'Swine Raffles', avatar_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed = DiscordEmbed(title = ':pig:  User started tasks!  :pig:', color=16761035)
        embed.set_thumbnail(url=raffleInfo['image'])
        embed.add_embed_field(name = 'Store', value = raffleInfo['store'], inline = True)
        embed.add_embed_field(name = 'Raffle', value = raffleInfo['title'], inline = True)
        embed.add_embed_field(name = 'Amount', value = profileLength, inline = True)
        embed.add_embed_field(name = 'User', value = discordName, inline = True)
        embed.add_embed_field(name = 'Key', value = licence, inline = True)
        embed.add_embed_field(name = 'Device', value = hardware_id['id'], inline = True)
        embed.add_embed_field(name = 'IP', value = hardware_id['ip'], inline = True)
        if proxies == 'Local Host':
            embed.add_embed_field(name = 'Proxies', value = 'False', inline = True)
        else:
            embed.add_embed_field(name = 'Proxies', value = 'True', inline = True)
        embed.set_footer(text='Swine Raffles (v'+str(version)+')', icon_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
        return True
    except Exception as e:
        try:
            userInfo = {
                "discord":discordName,
                "licence":licence,
                "hardware_id": hardware_id
            }
            send_error(raffleInfo, 'send_tasks', '', version, '', str(e), userInfo)
        except:
            pass
        return False


def send_login(discordName, licence, hardware_id, version):
    try:
        webhook = DiscordWebhook(url=SEND_LOGIN_WEBHOOK, username = 'Swine Raffles', avatar_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed = DiscordEmbed(title = ':pig:  User logged in!  :pig:', color=16761035)
        embed.add_embed_field(name = 'User', value = discordName, inline = True)
        embed.add_embed_field(name = 'Key', value = licence, inline = True)
        embed.add_embed_field(name = 'Device', value = hardware_id['id'], inline = True)
        embed.add_embed_field(name = 'IP', value = hardware_id['ip'], inline = True)
        embed.set_footer(text='Swine Raffles (v'+str(version)+')', icon_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
        return True
    except Exception as e:  
        try:
            send_error('', 'send_login', '', version, '', str(e), {"discord":discordName,"licence":licence,"hardware_id": hardware_id})
        except:
            pass
        return False


def send_reset(discordName, licence, hardware_id, version):
    try:
        webhook = DiscordWebhook(url=SEND_RESET_WEBHOOK, username = 'Swine Raffles', avatar_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed = DiscordEmbed(title = ':pig:  User reset key!  :pig:', color=16761035)
        embed.add_embed_field(name = 'User', value = discordName, inline = True)
        embed.add_embed_field(name = 'Key', value = licence, inline = True)
        embed.add_embed_field(name = 'Device', value = hardware_id['id'], inline = True)
        embed.add_embed_field(name = 'IP', value = hardware_id['ip'], inline = True)
        embed.set_footer(text='Swine Raffles (v'+str(version)+')', icon_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
        return True
    except Exception as e:
        try:
            send_error('', 'send_reset', '', version, '', str(e), {"discord":discordName,"licence":licence,"hardware_id": hardware_id})
        except:
            pass
        return False


def send_task_finish(raffleInfo, discordName, licence, hardware_id, version, entries):
    try:
        webhook = DiscordWebhook(url=SEND_FINISH_WEBHOOK, username = 'Swine Raffles', avatar_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed = DiscordEmbed(title = ':pig:  Entry tasks finished!  :pig:', color=16761035)
        embed.set_thumbnail(url=raffleInfo['image'])
        embed.add_embed_field(name = 'Store', value = raffleInfo['store'], inline = True)
        embed.add_embed_field(name = 'Raffle', value = raffleInfo['title'], inline = True)
        embed.add_embed_field(name = 'Total', value = str(entries), inline = True)
        embed.add_embed_field(name = 'User', value = discordName, inline = True)
        embed.add_embed_field(name = 'Key', value = licence, inline = True)
        embed.add_embed_field(name = 'Device', value = hardware_id['id'], inline = True)
        embed.add_embed_field(name = 'IP', value = hardware_id['ip'], inline = True)
        embed.set_footer(text='Swine Raffles (v'+str(version)+')', icon_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
        return True
    except Exception as e:
        try:
            send_error('', 'send_reset', '', version, '', str(e), {"discord":discordName,"licence":licence,"hardware_id": hardware_id})
        except:
            pass
        return False



            
def send_error(raffleInfo, url, response, version, statusCode, error, userInfo):
    try:
        webhook = DiscordWebhook(url=SEND_ERROR_WEBHOOK, username = 'Swine Raffles', avatar_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed = DiscordEmbed(title = ':pig:  Error detected!  :pig:', color=16761035)
        if len(raffleInfo) != 0:
            embed.set_thumbnail(url=raffleInfo['image'])
            embed.add_embed_field(name = 'Store', value = raffleInfo['store'], inline = True)
            embed.add_embed_field(name = 'Raffle', value = raffleInfo['title'], inline = True)
        if len(str(url)) != 0:
            embed.add_embed_field(name = 'URL', value = url, inline = True)
        if len(str(statusCode)) != 0:
            embed.add_embed_field(name = 'Status Code', value = str(statusCode), inline = True)
        if len(str(response)) != 0:
            embed.add_embed_field(name = 'Response', value = response, inline = True)
        if len(str(error)) != 0:
            embed.add_embed_field(name = 'Error', value = str(error), inline = True)
        embed.add_embed_field(name = 'User', value = userInfo['discord'], inline = True)
        embed.add_embed_field(name = 'Licence', value = userInfo['licence'], inline = True)
        embed.set_footer(text='Swine Raffles (v'+str(version)+')', icon_url='https://cdn.discordapp.com/attachments/606880150579314708/915910214761455626/unknown.png')
        embed.set_timestamp()
        webhook.add_embed(embed)
        webhook.execute()
        return True
    except Exception as e:
        return False


def gen_phone():
    start = ['021', '027']
    length= [7, 8]
    phone = random.choice(start)
    for i in range(random.choice(length)):
        phone += str(random.randint(0,9))
        
    return phone


def gen_instagram(fname, lname, instagram):
    choices = ['_', '.', '']
    numbers = [True, False, True, False, False, False]
    if len(instagram) == 0:
        if random.choice(numbers):
            return fname.lower()+random.choice(choices)+lname.lower()+str(random.randint(1,9))
        else:
            return fname.lower()+random.choice(choices)+lname.lower()

    return instagram

def check_phone(phone):
    if phone[0] != '0':
        phone = '0'+phone

    return phone


def get_delay(randomDelay, delay):
    if randomDelay:
        return random.randint(delay[0], delay[1])

    return delay[0]


def gen_birthday():
    month = str(random.randint(1,12))
    if len(month) == 1:
        month = '0'+month
    birthday ='{}{}/{}/{}'.format(str(random.randint(0,2)), str(random.randint(1, 7)), month, str(random.randint(1970,2003)))

    return birthday


def get_device():
    ip = 'null'
    try:
        ip = requests.get('https://api.ipify.org/', timeout=5).text
    except:
        pass
    try:
        deviceUUID = str(subprocess.check_output('wmic csproduct get uuid')).split('\\r\\n')[1].strip('\\r').strip()
        if deviceUUID == '00000000-0000-0000-0000-000000000000':
            raise Exception
    except:
        deviceUUID = str(uuid4())

    return deviceUUID, ip



def nicify(profile):
    for i in profile:
        if i == 'email' or i == 'id':
            pass
        else:
            profile[i] = profile[i].lower().title()

    return profile


def check_address(profile):
    add = True
    space = profile['street'].split(' ')
    for q in space:
        for i in q:
            if i.isdigit():
                add=False
    if add:
        profile['street'] = str(random.randint(0,400))+ ' ' + profile['street']

    return profile


def get_captcha(slug, captchaProvider, apiKey, url, timeoutDelay, errorDelay, captchaRetry, raffleInfo, typeOf):
    if captchaProvider.lower() ==  '2captcha':
        #&version=v3
        typeOf
        while True:
            log(slug+'Getting captcha (1/2)...')
            try:
                r = requests.post(f'http://2captcha.com/in.php?key={apiKey}&method=userrecaptcha&googlekey={raffleInfo["captcha"]}&pageurl={url}', timeout=timeoutDelay)
            except Exception as e:
                log(slug+'Failed to connect to 2Captcha API')
                sleep(errorDelay)
                continue

            if r.status_code == 200:
                try:
                    captcha_id = r.text.split('|')[1]
                    log(slug+'Got captcha (1/2)')
                    count = 0
                    log(slug+'Solving captcha (2/2)...')
                    while True:
                        if count > captchaRetry:
                            log(slug+'Captcha retry exceeded limit. Restarting...')
                            return False
                        
                        try:
                            r = requests.get(f'http://2captcha.com/res.php?key={apiKey}&action=get&id={captcha_id}', timeout=timeoutDelay)
                        except:
                            log(slug+'Failed to connect to 2Captcha API')
                            sleep(errorDelay)
                            continue

                        if r.status_code == 200:
                            if 'CAPCHA_NOT_READY' not in r.text:
                                try:
                                    recaptcha_answer = r.text.split('|')[1]
                                    log(slug+'Solved captcha (2/2)')
                                    return recaptcha_answer
                                except:
                                    pass
                            else:
                                pass
                        else:
                            log(slug+'Failed to get captcha (2/2). [Status Code {}]'.format(str(r.status_code)))

                        count+=1
                        sleep(5)
                except:
                    pass
            else:
                log(slug+'Failed to get captcha (1/2). [Status Code {}]'.format(str(r.status_code)))

            sleep(5)
    elif captchaProvider.lower() == 'capmonster':
        while True:
            log(slug+'Getting captcha (1/2)...')
            if typeOf == 'v3':
                data = {
                    "clientKey":apiKey,
                    "task": {
                        "type":"RecaptchaV3TaskProxyless",
                        "websiteURL":url,
                        "websiteKey":raffleInfo["captcha"]
                    }
                }
            else:
                data = {
                    "clientKey":apiKey,
                    "task": {
                        "type":"RecaptchaV2EnterpriseTaskProxyless",
                        "websiteURL":url,
                        "websiteKey":raffleInfo["captcha"]
                    }
                }
            try:
                r = requests.post('https://api.capmonster.cloud/createTask', timeout=timeoutDelay, json=data)
            except Exception as e:
                log(slug+'Failed to connect to CapMonster API')
                sleep(errorDelay)
                continue
            if r.status_code == 200:
                try:
                    captcha_id = r.json()['taskId']
                    log(slug+'Got captcha (1/2)')
                    count = 0
                    log(slug+'Solving captcha (2/2)...')
                    while True:
                        if count > captchaRetry:
                            log(slug+'Captcha retry exceeded limit. Restarting...')
                            return False
                        
                        data = {
                            "clientKey":apiKey,
                            "taskId": captcha_id
                        }
                        try:
                            r = requests.post('https://api.capmonster.cloud/getTaskResult', timeout=timeoutDelay, json=data)
                        except:
                            log(slug+'Failed to connect to CapMonster API')
                            sleep(errorDelay)
                            continue

                        if r.status_code == 200:
                            if r.json()['status'].lower() == 'ready':
                                try:
                                    recaptcha_answer = r.json()['solution']['gRecaptchaResponse']
                                    log(slug+'Solved captcha (2/2)')
                                    return recaptcha_answer
                                except:
                                    pass
                            else:
                                pass
                        else:
                            log(slug+'Failed to get captcha (2/2). [Status Code {}]'.format(str(r.status_code)))

                        count+=1
                        sleep(5)
                except:
                    pass
            else:
                log(slug+'Failed to get captcha (1/2). [Status Code {}]'.format(str(r.status_code)))

            sleep(5)
    else:
        log(slug+'Captcha provider is not supported. [Supported: CapMonster, 2Captcha]')
        return False
    


def checkIfProcessRunning(discordHandle, key):
    sleep(15)
    current_system_pid = os.getpid()
    ThisSystem = psutil.Process(current_system_pid)
    processes = ['fiddler', 'charles', 'proxyman', 'tuts', 'james', 'httpdebugger', 'httptoolkit', 'crossapi', 'wireshark', 'smartsniff','inproxy','mitm','burp']
    while True:      
        for proc in psutil.process_iter():
            try:
                for p in processes:
                    if p.lower() in proc.name().lower():
                        try:
                            url = 'https://discord.com/api/webhooks/1011496530135494717/cO8N0Hm3o0v80ddP28Nqhnz9Vys4K7VuhPHpTNs3Qw4Yu6gwak25FsDPDp05eaWhR35Y'
                            colour = 0xfc5151
                            webhook = DiscordWebhook(url, username="bozo detector")
                            embed = DiscordEmbed()
                            embed.set_title(title="BOZO DETECTED")
                            embed.set_color(colour)
                            embed.add_embed_field(name='BOZO', value=str(discordHandle), inline=False)
                            embed.add_embed_field(name='Key', value=key, inline=False)
                            webhook.add_embed(embed)
                            webhook.execute()
                            sleep(2)
                            os._exit(0)
                        except:
                            pass
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass


        sleep(5)




