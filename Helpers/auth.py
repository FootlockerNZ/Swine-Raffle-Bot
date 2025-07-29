import requests
import os
from time import sleep
from dotenv import load_dotenv


load_dotenv(dotenv_path='..\\..\\.env')
API_KEY = os.getenv('API_KEY')


def check_licence(licence_key, hardware_id):
    licence_data = update_licence(licence_key, hardware_id)
    if licence_data is not None:
        discordName = licence_data.get('discord').get('username')
        return True, discordName
        
    return None


def check_licence_interim(licence_key, hardware_id):
    licence_data = update_licence(licence_key, hardware_id)
    if licence_data is not None:
        return True

    return None


def update_licence(licence_key, hardware_id):
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}'
        }
        data = {
            'metadata': 
                {'hwid': hardware_id}
        }

        try:
            response = requests.post(f'https://api.whop.com/api/v2/memberships/{licence_key}/validate_license', headers=headers, json=data, timeout=10)
        except:
            print('Failed to connect to dashboard')
            sleep(1)

        if response.status_code == 201:
            return response.json()
    except:
        pass

    return None


def reset_licence(licence_key):
    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}'
        }
        data = {
            'metadata': {}
        }
        try:
            response = requests.post(f'https://api.whop.com/api/v2/memberships/{licence_key}', headers=headers, json=data, timeout=10)
        except:
            print('Failed to connect to dashboard')
            sleep(1)
            
        if response.status_code == 201:
            return True 
    except:
        pass

    return None