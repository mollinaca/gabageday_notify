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
webhook = config['furikomi_remainder']['webhook']
yurichan_okodukai = config['furikomi_remainder']['yurichan_okodukai']
kaechan_okodukai = config['furikomi_remainder']['kaechan_okodukai']

today = datetime.datetime.now().day
if today != 15:
    print ("今日は15日ではないのです。")
    exit (0)


# Post to slack
message = "15日です。お金を振り込みましょう。金額は ゆりちゃん: " + yurichan_okodukai + "かえちゃん: " + kaechan_okodukai + " です"
url = webhook

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
