import json
import requests
import yaml


def update_spreadsheet(elements:list)->str:
    
    with open('api_settings.yaml', 'r', encoding='utf-8') as f:
        api_settings = yaml.safe_load(f)
    # headers = {"Content-Type": "application/json",
    #         "Authorization": f"Bearer {api_settings['token']}"}
    headers = {"Content-Type": "application/json"}

    json_data = json.dumps({"elements": elements, 
                            "password": api_settings['secret']})
    res = requests.post(api_settings['api_url'], json_data, headers=headers)
    return res.status_code

if __name__=="__main__":
    pass