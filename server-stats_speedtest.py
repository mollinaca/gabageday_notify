#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
for ubuntu server
Post to Slack about my network speedtest
"""
import os
import configparser
import urllib.request
import json
import socket
import subprocess

cfg = configparser.ConfigParser ()
cfg_file = os.path.dirname(__file__) + '/setting.ini'
cfg.read (cfg_file)
webhook = cfg['server-stats']['webhook']

hostname = socket.gethostname()
result = subprocess.Popen(['speedtest'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
result = result.communicate()[0].decode('utf-8')

message = '```[' + hostname + ']' \
    + result + '```'

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

print (body)
