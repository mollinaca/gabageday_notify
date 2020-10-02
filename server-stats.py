#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
for ubuntu server
Post to Slack about my ubuntu server status
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
uptime = subprocess.run(['uptime'], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
sensors_j = json.loads(subprocess.run(['sensors', '-j'], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout)
coretemp_core0 = str(sensors_j['coretemp-isa-0000']['Core 0']['temp2_input'])
coretemp_core1 = str(sensors_j['coretemp-isa-0000']['Core 1']['temp3_input'])
ip_addr1 = subprocess.Popen(['ip', 'addr', 'show'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ip_addr2 = subprocess.Popen(['grep', '-w', 'inet'], stdin=ip_addr1.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ip_addr3 = subprocess.Popen(['grep', 'global'], stdin=ip_addr2.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ip_addr4 = subprocess.Popen(['awk', '{print $2}'], stdin=ip_addr3.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
ip_addr = ip_addr4.communicate()[0].decode('utf-8')

message = '```[' + hostname + ']' + uptime \
    + 'core0_temp: ' + coretemp_core0 + '\'C \n' \
    + 'core1_temp: ' + coretemp_core1 + '\'C \n' \
    + 'local_ip: ' + ip_addr \
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
