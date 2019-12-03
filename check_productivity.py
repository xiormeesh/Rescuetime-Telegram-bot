import os
import requests

import telegram

from datetime import date

API_URL = "https://www.rescuetime.com/anapi/data"

def check_productivity(request):

    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])

    if request.method == "GET":

        api_token = os.environ["RESCUE_TIME_API_TOKEN"]

        today = str(date.today())

        params = {
            'key': api_token,
            'format': 'json',
            'perspective': 'interval',
            'restrict_kind': 'efficiency',
            'resolution_time': 'day',
            'restrict_begin': today
        }

        r = requests.get(API_URL, params=params)
        data = r.json()

        # productivity is the last element of the first row
        productivity = data['rows'][0][-1]
        
        print(productivity)

        chat_id = os.environ["TELEGRAM_CHAT_ID"]
        bot.sendMessage(chat_id=chat_id, text="Today's productivity pulse is {}%".format(productivity))
        
    return "ok"