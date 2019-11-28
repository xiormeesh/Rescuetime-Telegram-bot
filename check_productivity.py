import os
import requests

import telegram

API_URL = "https://www.rescuetime.com/anapi/data"

def check_productivity(request):

    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])

    if request.method == "GET":

        api_token = os.environ["RESCUE_TIME_API_TOKEN"]

        params = {
            'key': api_token,
            'format': 'json',
            'perspective': 'interval',
            'restrict_kind': 'efficiency',
            'resolution_time': 'day',
            # looks like there is a new bug on RT side, returning data for 2-3 days back
            'restrict_begin':'2019-11-28'
        }

        r = requests.get(API_URL, params=params)
        data = r.json()

        # productivity is the last element of the first row
        productivity = data['rows'][0][-1]
        
        print(productivity)

        chat_id = os.environ["TELEGRAM_CHAT_ID"]
        bot.sendMessage(chat_id=chat_id, text="Today's productivity pulse is {}%".format(productivity))
        
    return "ok"