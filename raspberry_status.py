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

hostname = subprocess.run(['hostname'], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
uptime = subprocess.run(['uptime'], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
temp = subprocess.run(['vcgencmd', 'measure_temp'], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
volt = subprocess.run(['vcgencmd', 'measure_volts'], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)

message = '```[' + hostname.stdout.rstrip() + ']' + uptime.stdout \
    + temp.stdout \
    + volt.stdout \
    + '```'

# Post to slack
data = {
    'text': message
}

headers = {
    'Content-Type': 'application/json',
}

req = urllib.request.Request(webhook, json.dumps(data).encode(), headers)
with urllib.request.urlopen(req) as res:
    body = res.read().decode('utf-8')

