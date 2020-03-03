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
webhook = config['slack']['webhook']

"""
ゴミ出し通知くん
 燃やすごみ：月、木
 資源ごみ：土
 金属・陶器・ガラスごみ：第2・第4 金
"""

weekday = datetime.date.today().weekday()
today = datetime.datetime.now().day
#print (weekday)
#print (today)
if weekday == 7 or weekday == 2:
    garbage_day = "燃やすごみ（毎週 月/木）"
elif weekday == 5:
    garbage_day = "資源ごみの日（毎週 土）"
elif weekday == 4:
    if (today <= 8 and today <= 14) or (today <= 22 and today <= 28):
        garbage_day = "金属・陶器・ガラスごみ（第2/第4 金）"
else:
    print ('tommorow is not garbage collected day', file=sys.stderr)
    exit (0)

# Post to slack
message = "明日は " + garbage_day + " の日です 🗑"
url=webhook
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