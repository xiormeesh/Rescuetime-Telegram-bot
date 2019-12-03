import os
import json
import requests
import pandas as pd

import telegram

from datetime import date

API_URL = "https://www.rescuetime.com/anapi/data"

LOCAL = True

# for testing only, move to firebase
tasks = [
    {
        "name": "Entertainment",
        "type": "limit",
        "minutes": 1,
        "reached_today": False
    },
    {
        "name": "Software Development",
        "type": "goal",
        "minutes": 1,
        "reached_today": False
    },
    {
        "type": "productivity",
        "minutes": 1,
        "reached_today": False
    }
]

def extract_from_cell(df, what, where, where_value):
    try:
        cell = df.loc[df[where] == where_value, [what]].iat[0,0]
    except IndexError:
        cell = None

    return cell

def send_request(**additional_params):

    params = {
        'key': os.environ["RESCUE_TIME_API_TOKEN"],
        'format': 'json'
    }

    params.update(additional_params)

    r = requests.get(API_URL, params=params)
    data = r.json()
    #print(json.dumps(data, indent=2))

    df = pd.DataFrame(data['rows'], columns=data['row_headers'])
    df.rename(columns={'Time Spent (seconds)': 'Time'}, inplace=True)
    df['Time'] = df['Time'].apply(lambda x: int(x/60))
    print(df)

    return df

def process_productivity(task, bot):

    target = task['minutes']
    
    today = send_request(perspective="interval", resolution_time="day", restrict_kind="efficiency")
    productivity_score = today.at[0, "Efficiency (percent)"]

    today_date = str(date.today())
    today = send_request(perspective="interval", resolution_time="day", restrict_kind="productivity", restrict_begin=today_date)

    # could update to > 0
    very_productive_min = extract_from_cell(today, 'Time', 'Productivity', 2) or 0
    print("very", very_productive_min)
    productive_min = extract_from_cell(today, 'Time', 'Productivity', 1) or 0
    print("productive", productive_min)

    time_spent = very_productive_min + productive_min

    if time_spent and time_spent >= target:

        message = "Goal reached, you have logged {} productive minutes out of {} minutes goal.".format(time_spent, target)

        if LOCAL:
            print(message)
        else:
            chat_id = os.environ["TELEGRAM_CHAT_ID"]
            bot.sendMessage(chat_id=chat_id, text=message)

def process_category(task, bot):

    target = task['minutes']
    
    today = send_request(perspective="rank", restrict_kind="overview")
    time_spent = extract_from_cell(today, 'Time', 'Category', task['name'])

    if time_spent and time_spent >= target:

        message = "{} reached, you've spent {}/{} minutes on {}".format(task['type'].capitalize(), time_spent, target, task['name'])

        if LOCAL:
            print(message)
        else:
            chat_id = os.environ["TELEGRAM_CHAT_ID"]
            bot.sendMessage(chat_id=chat_id, text=message)


def check_goals(request):

    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])

    if LOCAL == True or request.method == "GET":

        for task in tasks:
            if task["type"] in ["goal", "limit"]:
                process_category(task, bot)

            elif task['type'] == 'productivity':
                process_productivity(task, bot)

    return "ok"

check_goals("test")