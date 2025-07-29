import json
import requests
import threading
import sys
import ctypes
import logging
import time
import base64
from colorama import init
from os import listdir
from pypresence import Presence
from bs4 import BeautifulSoup as soup
from time import sleep
from harvester import Harvester
from Helpers.logger import logger
from Helpers.load import *
from Helpers.auth import *
from Helpers.utils import *
from Modules.loaded import Loaded
from Modules.jdSports import JDSports
from Modules.area51 import Area51
from Modules.empireSkate import EmpireSkate
from Modules.confirmEmpire import EmpireConfirm
from Modules.knowear import Knowear

log = logger().log
init()
sys.tracebacklimit = 0
sys.setrecursionlimit(1000)
inUse = False
VERSION = '1.11'

try:
    rpc = Presence('1015896654685155398', pipe=0)
    rpc.update(state='Superior Automation Technology', details='Version '+VERSION, start=time.time(), large_image='swine_logo', button=[{"label": "Dashboard", "url": "https://swine-raffles.hyper.co/"}, {'label': 'Twitter', 'url': 'https://twitter.com/SwineScripts'}])
except Exception as e:
    pass

chromeVersion = '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"'

userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"

hardware_id = ''

discordName = 'Unknown'

proxyFormat = ''

profileFormat = ''

entries = 0

ctypes.windll.kernel32.SetConsoleTitleW("Swine Raffles v{}".format(str(VERSION)))

deviceInfo = get_device()

hardware_id = {
    'id':str(deviceInfo[0]),
    'ip':str(deviceInfo[1])
}


raffles = False

confirmer = False

raffleInfo = {}



def update():
    title_parts = [f"Swine Raffles v{VERSION}"]

    if discordName:
        title_parts.append(f"User: {discordName}")
    if profileFormat:
        title_parts.append(f"Profiles: {profileFormat}")
    if proxyFormat:
        title_parts.append(f"Proxies: {proxyFormat}")

    title_parts.append(f"Entries: {entries}")

    ctypes.windll.kernel32.SetConsoleTitleW(" | ".join(title_parts))


def check_delay(delay):
    if int(delay) > 10:
        return True, int(delay)-10

    return False, int(delay)



def loaded():
    global entries
    global config
    global raffleInfo
    while True:
        print_info()
        url = input('Enter raffle url: ')
        try:
            url = url.split('?')[0]
        except:
            pass
        print()
        if 'https://www.research.net/r/' not in url:
            print('Invalid raffle link')
            sleep(2)
            clear()
        else:
            break


    while True:
        try:
            log('Getting raffle info...')
            try:
                r = requests.get(url, timeout=config['timeoutDelay'])
            except:
                log('Failed to connect to Loaded')
                sleep(config['errorDelay'])
                continue

            if r.status_code == 200:
                if 'survey-closed' not in r.url:
                    page = soup(r.text, 'html.parser')
                    try:
                        image = page.find('img', {'class':'logo user-generated'})['src']
                    except:
                        image  = 'https://cdn.discordapp.com/attachments/694012581555470396/779083760943366174/swine.jpg'
                    try:
                        title = page.find('span',{'class':'title-text'}).text.strip().replace('"', '')
                        try:
                            title = title.replace('Raffle to Purchase', '')
                        except:
                            pass
                    except:
                        title = 'Loaded Raffle'

                    questionIDS = page.findAll('div', {'class':'text-input-container clearfix'})
                    ids = []
                    for q in questionIDS:
                        page1 = soup(str(q), 'html.parser')
                        ids.append(page1.find('label')['for'])

                    allOptions = page.findAll('div', {'class':"radio-button-container"})
                    page4 = soup(str(allOptions[0]), 'html.parser')
                    page2 = soup(str(allOptions[1]), 'html.parser')
                    page3 = soup(str(allOptions[2]), 'html.parser')
                    optionID = page2.find('input')['id'].replace('_', ':') + ' '+ page3.find('input')['id'].replace('_', ':')
                    optionIDAuckland = page4.find('input')['id'].replace('_', ':') + ' '+ page3.find('input')['id'].replace('_', ':')

                    try:
                        sizes = []
                        sizesDisplay = []
                        init = page.find('select', {'class':'select no-touch'}).findAll('option')
                        sizesID = page.find('select', {'class':'select no-touch'})['name']
                        for i in init:
                            if len(i.text) != 0:
                                sizesDisplay.append(i.text.strip().replace('>','').replace("SIZE ",'').replace('SIZE\xa0','').strip())
                                size = i.text.strip().replace('>','').replace("SIZE ",'').replace('SIZE\xa0','').strip()
                                try:
                                    size = size.split('(')[0]
                                except:
                                    pass
                                sizes.append({"size":size, "variant":i['value']})
                    except Exception as e:
                        log('Failed to get sizes. Random selection is not available')
                    log('Successfully got raffle details')

                    break
                else:
                    log('Raffle has closed')
            else:
                log('Failed to request raffle page. [Status Code: {}]'.format(str(r.status_code)))

            sleep(config['errorDelay'])
        except Exception as e:
            log('Failed to get raffle info. [Error: {}]'.format(str(e)))
            input()

    raffleInfo = {
        "store":store,
        "url":url,
        "title":title,
        "image":image,
        "sizes":sizes,
        'ids':ids,
        "optionID":optionID,
        'optionIDAuckland':optionIDAuckland,
        "sizeID":sizesID
    }

    clear()
    print_info()
    print('Raffle: '+title)
    print('Sizes: '+', '.join(sizesDisplay))
    #add try except above


    while True:
        print()
        cont = input('Do you want to start? (y/n): ')
        print()
        if cont.lower()=='y':
            send_tasks(raffleInfo, discordName, profileLength, config['licence'], hardware_id, VERSION, proxies)
            for x in range(len(profiles)):
                config = load_config_tasks()
                if inUse:
                    print('Licence is in use on another device. Please reset the key or click enter to retry authentication')
                    input()
                    checkLoggedInTemp(config['licence'], hardware_id['id'])
                    if inUse:
                        continue

                delay = Loaded(x, profiles[x], proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion).enter()
                if delay != None:
                    if delay[1]:
                        entries+=1
                    update()

                    d = check_delay(delay[0])
                    if d[0]:
                        sleep(d[1])
                        log('10s till next entry...')
                        sleep(10)
                    else:
                        sleep(d[1])

            entries+=1
            update()
            break
        else:
            sleep(2)


def jdsports():
    global raffleInfo
    global entries
    global config
    while True:
        print_info()
        url = input('Enter raffle url: ')
        try:
            url = url.split('?')[0]
        except:
            pass
        print()
        if 'https://raffles.jdsports.co.nz/' not in url:
            print('Invalid raffle link')
            sleep(2)
            clear()
        else:
            break
    
    while True:
        try:
            raffleID = url.split('/')[3].split('-')[-1]
            try:
                raffleID = raffleID.split('?')[0]
            except:
                pass
            sizes = []
            log('Getting raffle info...')
            headers = {
                'authority': 'raffles-resources.jdsports.co.uk',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'sec-ch-ua': chromeVersion,
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': userAgent,
            }
            try:
                r = requests.get(f'https://raffles-resources.jdsports.co.uk/raffles/raffles_{raffleID}.js', headers=headers, timeout=config['timeoutDelay'])
            except Exception as e:
                log('Failed to connect to JD Sports')
                sleep(config['errorDelay'])
                continue

            if r.status_code == 200:
                try:
                    resp = json.loads(r.text.split('raffles = [')[1].split('];')[0])
                    try:
                        try:
                            title = resp['product_name'].replace('Jd New Zealand ', '').replace('Access', '').strip()
                        except:
                            title = 'JD Sports NZ Raffle'
                        try:
                            image = resp['product_image']
                        except:
                            image = 'https://cdn.discordapp.com/attachments/694012581555470396/779083760943366174/swine.jpg'
                        captchaKey = resp['captcha']
                        for i in resp['size_categories'][0]['group_skus']:
                            size = i['size'].split('-')[0].strip()
                            try:
                                size = size.split('(')[0]
                            except:
                                pass
                            sizes.append({'size':size, 'skuID':i['sku_id'], 'sizeID':i['sku_size_id']})
                        log('Successfully got raffle info')

                        sizesDisplay = []
                        for i in sizes:
                            sizesDisplay.append(i['size'])

                        break
                    except:
                        log('Failed to get raffle info')    
                except:
                    log('Failed to load raffle info')
            else:
                log('Failed to get raffle info. [Status Code: {}]'.format(str(r.status_code)))

            sleep(config['errorDelay'])
        except Exception as e:
            log('Failed to get raffle info. [Error: {}]'.format(str(e)))
            input()
    
    raffleInfo = {
        "store":store,
        "url":url,
        "title":title,
        "image":image,
        "sizes":sizes,
        "id":raffleID,
        "captcha":captchaKey
    }
    clear()
    print_info()
    print('Raffle: '+title)
    print('Sizes: '+', '.join(sizesDisplay))

    if len(config['captchaKey']) == 0 or len(config['captchaProvider']) == 0:
        print()
        print('Starting captcha harvester...')
        logging.getLogger('harvester').setLevel(logging.CRITICAL)
        try: 
            harvester = Harvester('localhost', 7777)
            harvester.intercept_recaptcha_v3(
                domain='raffles.jdsports.co.nz',
                sitekey=captchaKey
            )
            server_thread = threading.Thread(target=harvester.serve, daemon=True)
            server_thread.start()
            harvester.launch_browser()
            print('Successfully started captcha harvester')
            print()
        except:
            print('Failed to open captcha harvester. Please add a Captcha solving services (2Captcha or CapMonster) API key to the config file')
            input()
            return
    else:
        if config['captchaProvider'].lower() != '2captcha' and config['captchaProvider'].lower() != 'capmonster':
            print()
            print('Captcha provider is not supported. Please change it to 2Captcha or CapMonster')
            input()
            sys.exit()


    usedCaptchas = []
    while True:
        print()
        cont = input('Do you want to start? (y/n): ')
        print()
        if cont.lower()=='y':
            send_tasks(raffleInfo, discordName, profileLength, config['licence'], hardware_id, VERSION, proxies)
            for x in range(len(profiles)):
                config = load_config_tasks()
                if inUse:
                    print('Licence is in use on another device. Please reset the key or click enter to retry authentication')
                    input()
                    checkLoggedInTemp(config['licence'], hardware_id['id'])
                    if inUse:
                        continue

                delay = JDSports(x, profiles[x], proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion, usedCaptchas).enter()

                if delay != None:
                    usedCaptchas = delay[2]
                    if delay[1]:
                        entries+=1
                    update()
                    d = check_delay(delay[0])
                    if d[0]:
                        sleep(d[1])
                        log('10s till next entry...')
                        sleep(10)
                    else:
                        sleep(d[1])

            entries+=1
            update()
            break
        else:
            sleep(2)


def area51():
    global raffleInfo
    global entries
    global config
    while True:
        print_info()
        url = input('Enter raffle url: ')
        try:
            url = url.split('?')[0]
        except:
            pass
        print()
        if 'https://area51store.co.nz/products/' not in url:
            print('Invalid raffle link')
            sleep(2)
            clear()
        else:
            handle = url.split('products/')[1]
            break
    while True:
        print_info()
        print('Enter raffle url: '+url)
        print()
        raffleID = input('Enter raffle id: ')
        if raffleID.isdigit():
            break
        else:
            print('Invalid raffle id')

        input()
        clear()
        
    print()

    while True:
        try:
            sizes = []
            log('Getting raffle info...')
            headers = {
                'authority': 'area51store.co.nz',
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'origin': 'https://area51store.co.nz',
                'pragma': 'no-cache',
                'referer': url,
                'sec-ch-ua': chromeVersion,
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': userAgent,
                'x-shopify-storefront-access-token': '7293cfd3cea1b2b4cd81166209b64c89',
            }
            data = {
                'operationName': 'productByHandle',
                'variables': {
                    'handle': handle,
                },
                'query': 'query productByHandle($handle: String!) {\n  shop {\n    productByHandle(handle: $handle) {\n      id\n      vendor\n      title\n      descriptionHtml\n      tags\n      images(first: 250) {\n        edges {\n          image: node {\n            id\n            originalSrc\n            altText\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      options {\n        id\n        name\n        values\n        __typename\n      }\n      variants(first: 250) {\n        edges {\n          variant: node {\n            ...variantFields\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      recommend: collections(first: 1) {\n        edges {\n          collection: node {\n            products(first: 4) {\n              edges {\n                product: node {\n                  ...productForListing\n                  __typename\n                }\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      collections(first: 30) {\n        edges {\n          collection: node {\n            handle\n            title\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment variantFields on ProductVariant {\n  id\n  title\n  selectedOptions {\n    name\n    value\n    __typename\n  }\n  price\n  compareAtPrice\n  sku\n  availableForSale\n  __typename\n}\n\nfragment productForListing on Product {\n  id\n  handle\n  title\n  publishedAt\n  vendor\n  tags\n  images(first: 2) {\n    edges {\n      image: node {\n        id\n        originalSrc\n        altText\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  variants(first: 1) {\n    edges {\n      variant: node {\n        price\n        compareAtPrice\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n',
            }
            try:
                r = requests.post('https://area51store.co.nz/api/2021-07/graphql.json', headers=headers, timeout=config['timeoutDelay'], json=data)
            except Exception as e:
                log('Failed to connect to Area 51')
                sleep(config['errorDelay'])
                continue

            if r.status_code == 200:
                try:
                    array = r.json()['data']['shop']['productByHandle']
                    try:
                        title = array['title']
                    except:
                        title = 'Area 51 Raffle'
                    try:
                        image = array['images']['edges'][0]['image']['originalSrc']
                    except:
                        image = 'https://cdn.discordapp.com/attachments/694012581555470396/779083760943366174/swine.jpg'
                    
                    allSizes = array['variants']['edges']
                    for i in allSizes:
                        try:
                            size = i['variant']['title'].split('(')[0]
                        except:
                            size = i['variant']['title']
                        sizes.append({'size':size, 'variant':str(base64.b64decode(i['variant']['id']).decode("utf-8")).split('ProductVariant/')[1]})

                    log('Successfully got raffle info')

                    sizesDisplay = []
                    for i in sizes:
                        sizesDisplay.append(i['size'])

                    break
                except:
                    log('Failed to load raffle info')
            else:
                log('Failed to get raffle info. [Status Code: {}]'.format(str(r.status_code)))

            sleep(config['errorDelay'])
        except Exception as e:
            log('Failed to get raffle info. [Error: {}]'.format(str(e)))
            input()

    raffleInfo = {
        "store":store,
        "url":url,
        "id":raffleID,
        "title":title,
        "image":image,
        "sizes":sizes
    }

    clear()
    print_info()
    print('Raffle: '+title)
    print('Sizes: '+', '.join(sizesDisplay))

    while True:
        print()
        cont = input('Do you want to start? (y/n): ')
        print()
        if cont.lower()=='y':
            send_tasks(raffleInfo, discordName, profileLength, config['licence'], hardware_id, VERSION, proxies)
            for x in range(len(profiles)):
                config = load_config_tasks()
                if inUse:
                    print('Licence is in use on another device. Please reset the key or click enter to retry authentication')
                    input()
                    checkLoggedInTemp(config['licence'], hardware_id['id'])
                    if inUse:
                        continue

                delay = Area51(x, profiles[x], proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion).enter()
                
                if delay != None:
                    if delay[1]:
                        entries+=1
                    update()
                    d = check_delay(delay[0])
                    if d[0]:
                        sleep(d[1])
                        log('10s till next entry...')
                        sleep(10)
                    else:
                        sleep(d[1])

            entries+=1
            update()
            break
        else:
            sleep(2)
            

def empireskate():
    global raffleInfo
    global entries
    global config
    while True:
        print_info()
        url = input('Enter raffle url: ')
        try:
            url = url.split('?')[0]
        except:
            pass
        print()
        if 'https://www.empireskate.co.nz/products/' not in url:
            print('Invalid raffle link')
            sleep(2)
            clear()
        else:
            break

    while True:
        try:
            log('Getting raffle info...')
            sizes = []
            headers = {
                'authority': 'www.empireskate.co.nz',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'sec-ch-ua': chromeVersion,
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': userAgent
            }

            try:
                r = requests.get(url, headers=headers, timeout=config['timeoutDelay'])
            except Exception as e:
                log('Failed to connect to Empire Skate')
                sleep(config['errorDelay'])
                continue

            if r.status_code == 200:
                page = soup(r.text, 'html.parser')
                try:
                    title = str(page.find('h1').text.strip())
                except:
                    title = 'Empire Skate Raffle'
                try:
                    image = page.find('div',{'class':'image__container'}).find('img')['data-src']
                except:
                    image = 'https://cdn.discordapp.com/attachments/694012581555470396/779083760943366174/swine.jpg'
                list_id = str(page.find('input', {'class':'klaviyo_list_id'})['value'])
                allSizes = page.find('select', {'id':'klaviyo_form_size'}).findAll('option')
                for i in allSizes:
                    size = str(i.text).strip()
                    try:
                        size = size.split('(')[0]
                    except:
                        pass
                    sizes.append(size)
                log('Successfully got raffle info')
                break
            else:
                log('Failed to get raffle info. [Status Code: {}]'.format(str(r.status_code)))
            sleep(config['errorDelay'])
        except Exception as e:
            log('Failed to get raffle info. [Error: {}]'.format(str(e)))
            input()

    raffleInfo = {
        "store":store,
        "url":url,
        "list_id":list_id,
        "title":title,
        "image":image,
        "sizes":sizes
    }

    clear()
    print_info()
    print('Raffle: '+title)
    print('Sizes: '+', '.join(sizes))

    while True:
        print()
        cont = input('Do you want to start? (y/n): ')
        print()
        if cont.lower()=='y':
            send_tasks(raffleInfo, discordName, profileLength, config['licence'], hardware_id, VERSION, proxies)
            for x in range(len(profiles)):
                config = load_config_tasks()
                if inUse:
                    print('Licence is in use on another device. Please reset the key or click enter to retry authentication')
                    input()
                    checkLoggedInTemp(config['licence'], hardware_id['id'])
                    if inUse:
                        continue

                delay = EmpireSkate(x, profiles[x], proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion).enter()
                
                if delay != None:
                    if delay[1]:
                        entries+=1
                    update()
                    d = check_delay(delay[0])
                    if d[0]:
                        sleep(d[1])
                        log('10s left until next entry...')
                        sleep(10)
                    else:
                        sleep(d[1])

            entries+=1
            update()
            break
        else:
            sleep(2)



def knowear():
    global raffleInfo
    global entries
    global config
    while True:
        print_info()
        url = input('Enter raffle url: ')
        try:
            url = url.split('?')[0]
        except:
            pass
        print()
        if 'https://www.knowear.co/' not in url:
            print('Invalid raffle link')
            sleep(2)
            clear()
        else:
            break
    
    while True:
        try:
            sizes = []
            log('Getting raffle info...')
            headers = {
                'authority': 'www.knowear.co',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'referer': 'https://www.knowear.co/collections/upcoming-launches',
                'sec-ch-ua': chromeVersion,
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': userAgent,
            }
            try:
                r = requests.get(url, headers=headers, timeout=config['timeoutDelay'])
            except Exception as e:
                log('Failed to connect to Knowear')
                sleep(config['errorDelay'])
                continue

            if r.status_code == 200:
                page = soup(r.text,'html.parser')
                try:
                    resp = json.loads(r.text.split('var meta = ')[1].split(';')[0].strip())['product']
                    try:
                        try:
                            title = page.find('meta', {'property':'og:title'})['content']
                        except Exception as e:
                            title = 'Knowear Raffle'
                        try:
                            image = page.find('meta', {'property':'og:image'})['content']
                        except:
                            image = 'https://cdn.discordapp.com/attachments/694012581555470396/779083760943366174/swine.jpg'

                        captchaKey = r.text.split('"g-recaptcha" data-sitekey="')[1].split('"')[0]

                        for i in resp['variants']:
                            sizes.append(i['name'].split('-')[-1].strip())

                        raffleID = r.text.split('action="https://submit-form.com/')[1].split('"')[0]

                        log('Successfully got raffle info')
                        break
                    except Exception as e:
                        log('Failed to get raffle info')    
                except Exception as e:
                    log('Failed to load raffle info')
            else:
                log('Failed to get raffle info. [Status Code: {}]'.format(str(r.status_code)))

            sleep(config['errorDelay'])
        except Exception as e:
            log('Failed to get raffle info. [Error: {}]'.format(str(e)))
            input()
    
    raffleInfo = {
        "store":store,
        "url":url,
        "title":title,
        "image":image,
        "sizes":sizes,
        "id":raffleID,
        "captcha":captchaKey
    }

    clear()
    print_info()
    print('Raffle: '+title)
    print('Sizes: '+', '.join(sizes))

    if len(config['captchaKey']) == 0 or len(config['captchaProvider']) == 0:
        print()
        print('Starting captcha harvester...')
        logging.getLogger('harvester').setLevel(logging.CRITICAL)
        try: 
            harvester = Harvester('localhost', 8881)
            harvester.intercept_recaptcha_v2(
                domain='wwww.knowear.co',
                sitekey=captchaKey
            )
            server_thread = threading.Thread(target=harvester.serve, daemon=True)
            server_thread.start()
            harvester.launch_browser()
            print('Successfully started captcha harvester')
            print()
        except:
            print('Failed to open captcha harvester. Please add a Captcha solving services (2Captcha or CapMonster) API key to the config file')
            input()
            return
    else:
        if config['captchaProvider'].lower() != '2captcha' and config['captchaProvider'].lower() != 'capmonster':
            print()
            print('Captcha provider is not supported. Please change it to 2Captcha or CapMonster')
            input()
            sys.exit()


    usedCaptchas = []
    while True:
        print()
        cont = input('Do you want to start? (y/n): ')
        print()
        if cont.lower()=='y':
            send_tasks(raffleInfo, discordName, profileLength, config['licence'], hardware_id, VERSION, proxies)
            for x in range(len(profiles)):
                config = load_config_tasks()
                if inUse:
                    print('Licence is in use on another device. Please reset the key or click enter to retry authentication')
                    input()
                    checkLoggedInTemp(config['licence'], hardware_id['id'])
                    if inUse:
                        continue

                delay = Knowear(x, profiles[x], proxies, config, raffleInfo, profileLength, VERSION, userAgent, userInfo, chromeVersion, usedCaptchas).enter()

                if delay != None:
                    usedCaptchas = delay[2]
                    if delay[1]:
                        entries+=1
                    update()
                    d = check_delay(delay[0])
                    if d[0]:
                        sleep(d[1])
                        log('10s till next entry...')
                        sleep(10)
                    else:
                        sleep(d[1])

            entries+=1
            update()
            break
        else:
            sleep(2)




def print_info():
    clear()
    print('Store: '+store)
    print('Profiles: '+profileFormat)
    print('Proxies: '+proxyFormat)
    print()
    print()


def authenticate(licence_key):
    global discordName
    clear()
    print('Authenticating licence...')
    check = check_licence(licence_key, hardware_id['id'])
    if check != None:
        clear()
        discordName = check[1]
        update()
        clear()
        send_login(discordName, config['licence'], hardware_id, VERSION)
        return True

    else:
        clear()
        print('Licence is invalid or in use on another device. Please reset the key and check it is correct')

    sleep(1)
    return False


def reset(licence_key):
    clear()
    print('Resetting licence...')
    reset = reset_licence(licence_key)
    clear()
    if reset != None:
        print('Successfully reset licence')
        send_reset(discordName, config['licence'], hardware_id, VERSION)
    else:
        print('Failed to reset licence')
        sleep(1)



def checkLoggedIn(licence, hardware_id):
    global inUse
    inUse = False
    while True:
        sleep(180)
        check = check_licence_interim(licence, hardware_id)
        if check == None:
            inUse = True


def checkLoggedInTemp(licence, hardware_id):
    global inUse
    inUse = False
    check = check_licence_interim(licence, hardware_id)
    if check == None:
        inUse = True
    
        
        

def main():
    global config
    while True:
        clear()
        print('[1] : Authenticate licence key')
        print('[2] : Reset licence key')
        print('[3] : Exit')
        answers = ['1', '2', '3']
            
        print()
        answer = input('Please enter your option: ').strip()
        config = load_config_tasks()
        if answer not in answers:
            print()
            print('Invalid input')
            input()
            continue
        elif answer == '1':
            if len(config['licence']) != 0:
                cont = authenticate(config['licence'])
                if cont:
                    return
                else:
                    input()
            else:
                print()
                print('Please enter a licence in the config file')
                input()
                continue
        elif answer == '2':
            if len(config['licence']) != 0:
                clear()
                reset(config['licence'])
                continue
            else:
                print()
                print('Please enter a licence in the config file')
                input()
                continue
        else:
            print('Exiting...')
            sleep(3)
            sys.exit()

def choose_mode():
    while True:
        clear()
        print('Welcome back {}!'.format(discordName))
        print()
        print('Modes:')
        print('-------')
        modeList = ["Enter raffles", "Confirm entries"]
        for i in range(len(modeList)):
            print('[{}] {}'.format(str(i+1), modeList[i]))

        print('[{}] Go Back'.format(str(len(modeList)+1)))
        print()
        modeSelected = input('Choose your mode: ')
        try:
            if int(modeSelected) < 1:
                print('Invalid input')
                input()
                continue
            else:
                if int(modeSelected) == len(modeList)+1:
                    return 'back'
                mode = modeList[int(modeSelected)-1]
        except:
            print('Invalid input')
            input()
            continue

        return mode


def choose_store():
    while True:
        clear()
        print('Welcome back {}!'.format(discordName))
        print()
        print('Stores:')
        print('-------')
        storeList = ["JD Sports NZ", "Area 51","Loaded", "Empire Skate", "Knowear"]
        for i in range(len(storeList)):
            print('[{}] {}'.format(str(i+1), storeList[i]))

        print('[{}] Go Back'.format(str(len(storeList)+1)))
        print()
        storeSelected = input('Choose your store: ')
        try:
            if int(storeSelected) < 1:
                print('Invalid input')
                input()
                continue
            else:
                if int(storeSelected) == len(storeList)+1:
                    return 'back'
                store = storeList[int(storeSelected)-1]
        except:
            print('Invalid input')
            input()
            continue

        return store





def choose_profiles():
    while True:
        clear()
        print('Store: '+store)
        print()
        if len(listdir('Profiles')) != 0:
            print('Profiles:')
            print('---------')
            try:
                for i in range(len(listdir('Profiles'))):
                    print('[{}] {}'.format(str(i+1), listdir('Profiles')[i]))
                print('['+str(len(listdir('Profiles'))+1)+'] Go Back')
            except Exception as e:
                print('Failed to load profile files')
                input()
                return False
            print()
            profileNo = input('Please choose your profile file: ').strip()
            try:
                profileNo = int(profileNo)
            except:
                print()
                print('Invalid input. Please try again')
                sleep(1)
                clear()
            if profileNo == len(listdir('Profiles')) + 1:
                return 'Back'
            print()
            try:
                profileFile = listdir('Profiles')[profileNo-1]
            except:
                print()
                print('Invalid input. Please try again')
                sleep(1)
                clear()
                continue
            clear()
            p = load_profiles('Profiles/'+profileFile)
            clear()
            return p[0], p[1], profileFile, p[2]
        else:
            print('Profiles folder is empty. Please add a profile file')
            input()
            return False


def save_profiles(profiles, profileFile):
    try:
        f = open('Profiles/'+profileFile, 'w', newline='')
        writer = csv.writer(f)
        header = ['id', 'email', 'fname', 'lname', 'phone', 'street', 'suburb', 'city', 'province', 'postcode', 'size', 'instagram', 'answer']
        writer.writerow(header)
        f.close()

        t = open('Profiles/'+profileFile, 'a', newline='')
        writer = csv.writer(t)
        for i in profiles:
            row = [i['id'], i['email'], i['fname'], i['lname'], i['phone'], i['street'], i['suburb'], i['city'], i['province'], i['postcode'], i['size'], i['instagram'], i['answer']]
            writer.writerow(row)
        t.close()
    except Exception as e:
        input()
        print()
        print('Failed to save genned profile values')
        input()
        sleep(1)
    return


def choose_proxies():
    while True:
        clear()
        print('Store: '+store)
        print('Profiles: '+profileFormat)
        print()
        
        if len(listdir('Proxies')) != 0:
            print('Proxies:')
            print('--------')
            try:
                print('[1] Local Host')
                for i in range(len(listdir('Proxies'))):
                    print('[{}] {}'.format(str(i+2), listdir('Proxies')[i]))
                print('['+str(len(listdir('Proxies'))+2)+'] Go Back')
            except Exception as e:
                print('Failed to load proxy files')
                input()
                return False
            print()
            proxyNo = input('Please choose your proxy file: ').strip()
            try:
                proxyNo = int(proxyNo)
            except:
                print()
                print('Invalid input. Please try again')
                sleep(1)
                clear()
                continue
            if proxyNo == len(listdir('Proxies')) + 2:
                return 'Back'
            print()
            if proxyNo == 1:
                clear()
                return False
            else:
                clear()
                try:
                    proxyFile = listdir('Proxies')[proxyNo-2]
                except:
                    print()
                    print('Invalid input. Please try again')
                    sleep(1)
                    clear()
                    continue
                p = load_proxies('Proxies/'+proxyFile)
            if p == False:
                return False
            clear()
            return p[0], p[1], proxyFile
        else:
            print('Proxies folder is empty. Running local host')
            sleep(2)
            return False


def choose_confirmer_proxies():
    while True:
        clear()
        print()
        
        if len(listdir('Proxies')) != 0:
            print('Proxies:')
            print('--------')
            try:
                print('[1] Local Host')
                for i in range(len(listdir('Proxies'))):
                    print('[{}] {}'.format(str(i+2), listdir('Proxies')[i]))
                print('['+str(len(listdir('Proxies'))+2)+'] Go Back')
            except Exception as e:
                print('Failed to load proxies')
                input()
                return False
            print()
            proxyNo = input('Please choose your proxy file: ').strip()
            try:
                proxyNo = int(proxyNo)
            except:
                print()
                print('Invalid input. Please try again')
                sleep(1)
                clear()
                continue
            if proxyNo == len(listdir('Proxies')) + 2:
                return 'Back'
            print()
            if proxyNo == 1:
                clear()
                return False
            else:
                clear()
                try:
                    proxyFile = listdir('Proxies')[proxyNo-2]
                except:
                    print()
                    print('Invalid input. Please try again')
                    sleep(1)
                    clear()
                    continue
                p = load_proxies('Proxies/'+proxyFile)
            if p == False:
                return False
            clear()
            return p[0], p[1], proxyFile
        else:
            print('Proxies folder is empty. Running local host')
            sleep(2)
            return False
            
update()

clear()

config = load_config()

clear()

links = load_links()


while True:
    clear()
    updateConfig = False
    if len(config['licence']) == 0:
        config['licence'] = str(input('Please enter your licence key: ').strip())
        if len(config['licence']) != 19:
            print()
            print('Invalid input. Please try again')
            config['licence'] = ''
            sleep(1)
            clear()
            continue
        else:
            updateConfig = True

    if len(config['webhook']) == 0:
        config['webhook'] = str(input('Please enter your discord webhook: ').strip())
        if 'https://discord.com' not in config['webhook'] and 'https://discordapp.com' not in config['webhook'] and 'webhooks.aycd.io' not in config['webhook']:
            print()
            config['webhook'] = ''
            print('Invalid input. Please try again')
            sleep(1)
            clear()
            continue
        else:
            updateConfig = True
    

    if updateConfig:
        try:    
            config_data = {
                "config": {
                    "licence":config['licence'],
                    "entryRetries":config['entryRetries'],
                    "entryDelay":config['entryDelay'],
                    "confirmDelay":config['confirmDelay'],
                    "timeoutDelay":config['timeoutDelay'],
                    "errorDelay":config['errorDelay'],
                    "webhook":config['webhook'],
                    "captchaProvider":config['captchaProvider'],
                    "captchaKey":config['captchaKey'],
                    "captchaRetries":config['captchaRetries']
                }
            }
            with open ('config.json', 'w+') as l:
                json.dump(config_data, l)
                clear()
                print('Successfully updated config')
                sleep(1)
                
        except Exception as e:
            print('Failed to update config. [Error: {}]'.format(str(e)))
            input()
            continue
    break



clear()
if len(config['licence']) == 0:
    print('Please enter a licence key in the config file')
    input()
    sys.exit()

if len(config['webhook']) == 0:
    print('Please enter a webhook in the config file')
    input()
    sys.exit()
    



while True:
    proxyFormat = '' #check this doesnt fuck shit up
    profileFormat = ''
    entries = 0
    update()
    while True:
        back = False
        main()
        while True:
            back = False
            mode = choose_mode()
            if mode == 'back':
                back = True
                break
            while True:
                back = False
                if mode == 'Enter raffles':
                    store = choose_store()
                    raffles = True
                
                    if store == 'back':
                        raffles = False
                        back = True
                        break

                    while True:
                        back = False
                        p = choose_profiles()

                        if p == False:
                            input()
                            sys.exit()
                        
                        
                        
                        try:
                            if p == 'Back':
                                back = True
                                break
                        except:
                            pass

                        profiles, profileLength, profileFile = p[0], p[1], p[2]
                        profileFormat = profileFile + " ("+str(len(profiles))+")"
                        if p[3]:
                            save_profiles(profiles, profileFile)
                        update()
                        clear()

                        while True:
                            back = False
                            prox = choose_proxies()

                            try:
                                if prox == 'Back':
                                    back = True
                                    break
                            except:
                                pass

                            if prox == False:
                                proxies = 'Local Host'
                                usingProxies = False
                                proxyFile = 'Local Host'
                            else:
                                proxies, usingProxies, proxyFile = prox[0], prox[1], prox[2]

                            if proxyFile != 'Local Host':
                                proxyFormat = proxyFile + " ("+str(len(proxies))+")"
                            else:
                                proxyFormat = proxyFile

                            update()
                            clear()
                            break

                        if back:
                            continue
                        else:
                            break
                    
                    if back:
                        continue
                    else:
                        break

                else:
                    while True:
                        back = False
                        prox = choose_confirmer_proxies()

                        try:
                            if prox == 'Back':
                                back = True
                                break
                        except:
                            pass

                        if prox == False:
                            proxies = 'Local Host'
                            usingProxies = False
                            proxyFile = 'Local Host'
                        else:
                            proxies, usingProxies, proxyFile = prox[0], prox[1], prox[2]

                        if proxyFile != 'Local Host':
                            proxyFormat = proxyFile + " ("+str(len(proxies))+")"
                        else:
                            proxyFormat = proxyFile

                        update()
                        clear()
                        break

                

                if back:
                    continue
                else:
                    break

            if back:
                continue
            else:
                break

        if back:
            continue
        else:
            break


    userInfo = {
        "discord":discordName,
        "licence":config['licence'],
        "hardware_id": hardware_id['id']
    }

    try:
        threading.Thread(target=checkLoggedIn, args=(config['licence'], hardware_id['id']), daemon=True).start()
    except:
        pass

    if raffles:
        if store == 'Loaded':
            loaded()
        elif store == 'JD Sports NZ':
            jdsports()
        #elif store == 'JD Sports NZ (Pre Auth)':
        #    jdsports('pre auth')
        elif store == "Knowear":
            knowear()
        elif store == 'Empire Skate':
            empireskate()
        elif store == 'Area 51':
            area51()
        else:
            print('Im not sure how you got here. Please report the input you used in discord #bugs')
            input()
            continue
        print()
        print()
        print("Finished entering. Press enter to take you to home")
        send_task_finish(raffleInfo, discordName, config['licence'], hardware_id, VERSION, entries)
    else:
        if len(links) != 0:
            while True:
                print()
                cont = input('Do you want to start? (y/n): ')
                print()
                if cont.lower()=='y':
                    for j in range(len(links)):
                        if 'https://manage.kmail-lists.com/subscriptions/subscribed?opt=' in links[j]:
                            EmpireConfirm(j, links, config, userAgent, chromeVersion, proxies, userInfo, len(links)).confirm()
                        #elif 'https://raffles-checkout.jdsports.co.nz/payment_success?' in links[j]:
                        #    jd_confirmer(j, links, config, userAgent, chromeVersion, proxies, userInfo, len(links)).confirm()
                        else:
                            print('Invalid confirm link: '+links[j])
                            print()
                    break
                else:
                    sleep(2)

            print()
            print()
            print("Finished confirming. Press enter to take you to home")
        else:
            print()
            print()
            print("No links loaded to confirm. Press enter to take you to home")
    
    input()
