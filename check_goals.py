import os
import requests
import pandas as pd

import telegram

from datetime import date

from google.cloud import firestore

API_URL = "https://www.rescuetime.com/anapi/data"


def extract_from_cell(df, what, where, where_value):
    try:
        cell = df.loc[df[where] == where_value, [what]].iat[0, 0]
    except IndexError:
        cell = 0

    return cell


def send_request(**additional_params):

    params = {
        'key': os.environ["RESCUE_TIME_API_TOKEN"],
        'format': 'json'
    }

    params.update(additional_params)

    r = requests.get(API_URL, params=params)
    data = r.json()

    # converting to pandas dataframe to search easier for specific values
    df = pd.DataFrame(data['rows'], columns=data['row_headers'])
    df.rename(columns={'Time Spent (seconds)': 'Time'}, inplace=True)
    # converting seconds to minutes
    df['Time'] = df['Time'].apply(lambda x: int(x/60))

    return df


def process_task(task, bot):
    '''
    Sends a message if goal/limit has been reached

    Parameters:
    task: instance of DocumentSnapshot (https://googleapis.dev/python/firestore/latest/document.html)
    bot: instance of Telegram.Bot (https://python-telegram-bot.readthedocs.io/en/stable/telegram.bot.html)

    Returns:
    None
    '''

    target = task.get('minutes')

    if task.get('type') == "productivity":

        today_date = str(date.today())
        today = send_request(perspective="interval", resolution_time="day", restrict_kind="productivity", restrict_begin=today_date)

        very_productive_min = extract_from_cell(today, 'Time', 'Productivity', 2)
        productive_min = extract_from_cell(today, 'Time', 'Productivity', 1)

        time_spent = very_productive_min + productive_min

        message = "Goal reached, you have logged {} productive minutes out of {} minutes goal.".format(time_spent, target)

    elif task.get('type') in ["limit", "goal"]:

        today = send_request(perspective="rank", restrict_kind="overview")
        time_spent = extract_from_cell(today, 'Time', 'Category', task.get('name'))

        message = "{} reached, you've spent {}/{} minutes on {}".format(task.get('type').capitalize(), time_spent, target, task.get('name'))

    else:
        print("Unknown task type")

    print(message)

    if time_spent and time_spent >= target:

        chat_id = os.environ["TELEGRAM_CHAT_ID"]
        bot.sendMessage(chat_id=chat_id, text=message)

        task.reference.update({"reached_today": True})


def check_goals(request):
    '''
    Gets tasks from firestore and checks if notifications need to be sent
    '''

    # initializing the bot
    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])

    if request.method == "GET":

        db = firestore.Client()

        # processing only unmet goals
        tasks = db.collection('tasks').where("reached_today", "==", False).stream()

        for task in tasks:

            print("{} => {}".format(task.id, task.to_dict()))

            process_task(task, bot)

    return "ok"
