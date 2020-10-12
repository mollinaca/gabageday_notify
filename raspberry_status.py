#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
raspberryPi から 健康状態をSlackへPOSTする
"""
import pathlib
import configparser
import urllib.request
import json
import socket
import subprocess

p = pathlib.Path(__file__).resolve().parent
config = configparser.ConfigParser()
config.read(str(p)+'/setting.ini')
webhook = config['raspberry']['webhook']

hostname = socket.gethostname()
uptime = subprocess.run(['uptime'], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
temp1 = subprocess.Popen(['vcgencmd', 'measure_temp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
temp = temp1.communicate()[0].decode('utf-8')
ip_addr1 = subprocess.Popen(['ip', 'addr', 'show', 'bond0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ip_addr2 = subprocess.Popen(['grep', '-w', 'inet'], stdin=ip_addr1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ip_addr3 = subprocess.Popen(['awk', '{print $2}'], stdin=ip_addr2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ip_addr = ip_addr3.communicate()[0].decode('utf-8')

message = '```[' + hostname + ']' + uptime.stdout \
    + temp \
    + 'wlan0: ' + ip_addr \
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

print (body)
