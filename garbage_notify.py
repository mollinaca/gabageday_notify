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
 燃えるゴミ   ： 火、金
 燃えないゴミ ： 木
 資源物１類   ： 水
 資源物２類   ： 木
 有害危険ゴミ ： 木
"""

weekday = datetime.date.today().weekday()
today = datetime.datetime.now().day
garbage_day = ''
#weekday = "test"
if weekday == 0 or weekday == 3:
    garbage_day = '燃えるごみ'
elif weekday == 1:
    garbage_day = '資源物1類(びん、かん、ペットボトル、食品包装プラ等)'
elif weekday == 2:
    garbage_day = '燃えないごみ、資源２類(古紙、繊維)、有害ゴミ'
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
