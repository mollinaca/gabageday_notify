#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
1日1回起動し、15日でなかったらスルー。15日だったら呟く。
"""
import sys
import datetime
import pathlib
import configparser
import urllib.request
import json

p = pathlib.Path(__file__).resolve().parent
config = configparser.ConfigParser()
config.read(str(p)+'/setting.ini')
webhook = config['yurichan_okodukai_remainder']['webhook']
webhook_dev = config['yurichan_okodukai_remainder']['webhook_dev']
okodukai = config['yurichan_okodukai_remainder']['okodukai']

today = datetime.datetime.now().day
print (today,type(today))
today = 15
if today != 15:
    print ("今日は15日ではないのです。")
    exit (0)


# Post to slack
message = "15日です。ゆりちゃんにお小遣いを振り込みましょう。今月のお小遣いは " + okodukai + " 円です。\nただし、2020年4月~6月分は支給済みです。"
url = webhook
#url = webhook_dev

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
