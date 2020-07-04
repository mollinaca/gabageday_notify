#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
raspberryPi から 健康状態をSlackへPOSTする
"""
import sys
import pathlib
import configparser
import urllib.request
import json
import subprocess

p = pathlib.Path(__file__).resolve().parent
config = configparser.ConfigParser()
config.read(str(p)+'/setting.ini')
webhook = config['raspberry']['webhook']

hostname = subprocess.run(['hostname'], encoding='utf-8', stdout=subprocess.PIPE)
uptime = subprocess.run(['uptime'], encoding='utf-8', stdout=subprocess.PIPE)
message = hostname.stdout + uptime.stdout
url = webhook

# Post to slack
data = {
    'text': message
}

headers = {
    'Content-Type': 'application/json',
}

req = urllib.request.Request(url, json.dumps(data).encode(), headers)
with urllib.request.urlopen(req) as res:
    body = res.read().decode('utf-8')
