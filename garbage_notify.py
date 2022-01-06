#!/usr/bin/env python3
import sys
import datetime
import pathlib
import configparser
import urllib.request
import json

p = pathlib.Path(__file__).resolve().parent
config = configparser.ConfigParser()
config.read(str(p) + "/setting.ini")
webhook = config["garbage_notify"]["webhook"]
webhook_dev = config["garbage_notify"]["webhook_dev"]

"""
ゴミ出し通知くん
 燃えるゴミ   ： 火、金
 燃えないゴミ ： 木
 資源物１類   ： 水
 資源物２類   ： 木
 有害危険ゴミ ： 木
"""
gomi_data = {
    1: "燃えるゴミ",
    2: "資源物1類(びん、かん、ペットボトル、食品包装プラ等)",
    3: "燃えないごみ、資源２類(古紙、繊維)、有害ゴミ",
    4: "燃えるゴミ",
}

weekday = datetime.date.today().weekday()
today = datetime.datetime.now().day
now = datetime.datetime.now()

if int(now.strftime("%H")) < 11:
    # 当日予定
    if weekday == 1 or 2 or 3 or 4:
        message = "今日は " + gomi_data[weekday] + " の日です"
    else:
        print("tommorow is not garbage collected day", file=sys.stderr)
        exit(0)

else:
    # 翌日予定
    weekday += 1
    if weekday == 7:
        weekday = 0
    if weekday == 1 or 2 or 3 or 4:
        message = "明日は " + gomi_data[weekday] + " の日です"
    else:
        print("tommorow is not garbage collected day", file=sys.stderr)
        exit(0)

# Post to slack
url = webhook
data = {"text": message}
headers = {
    "Content-Type": "application/json",
}
req = urllib.request.Request(url, json.dumps(data).encode(), headers)
with urllib.request.urlopen(req) as res:
    body = res.read().decode("utf-8")

print("ResponseBody:" + str(body), file=sys.stderr)
exit(0)
