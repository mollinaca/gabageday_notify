#!/usr/bin/env python3
import sys
import datetime
import pathlib
import configparser
import urllib.request
import json

p = pathlib.Path(__file__).resolve().parent
config = configparser.ConfigParser()
config.read(str(p)+'/setting.ini')
webhook = config['garbage_notify']['webhook']
webhook_dev = config['garbage_notify']['webhook_dev']

"""
ゴミ出し通知くん
 燃やすごみ：月、木
 資源ごみ：土
 金属・陶器・ガラスごみ：第2・第4 金
"""

weekday = datetime.date.today().weekday()
today = datetime.datetime.now().day
#weekday = "test"
if weekday == 6 or weekday == 2:
    garbage_day = "燃やすごみ（毎週 月/木）"
elif weekday == 4:
    garbage_day = "資源ごみの日（毎週 土）"
elif weekday == 3:
    if (8 <= today and today <= 14) or (22 <= today and today <= 28):
        garbage_day = "金属・陶器・ガラスごみ（第2/第4 金）"
elif weekday == "test":
    print ('post test mode')
    garbage_day = "post test mode"
else:
    print ('tommorow is not garbage collected day', file=sys.stderr)
    exit (0)

# Post to slack
message = "明日は " + garbage_day + " の日です 🗑"
url = webhook
#if weekday == "test":
#    url = webhook_dev

data = {
    'text': message
}

headers = {
    'Content-Type': 'application/json',
}

req = urllib.request.Request(url, json.dumps(data).encode(), headers)
with urllib.request.urlopen(req) as res:
    body = res.read().decode('utf-8')

print('ResponseBody:'+str(body), file=sys.stderr)
exit (0)
