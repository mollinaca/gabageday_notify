#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
https://saitama-vaccine.com/
のサイトに表示される「お知らせ」の更新を取得して通知する
"""
import configparser
import json
import os
import pathlib
import requests
import urllib.request
from bs4 import BeautifulSoup


def get_latest_news() -> dict:
    """
    お知らせページの最新ニュースの日付と内容を取得する
    """
    ret = {}
    url = "https://saitama-vaccine.com/"
    res = requests.get(url)
    if res.status_code == requests.codes.ok:
        html = BeautifulSoup(res.content, "html.parser")
        news = html.find_all(class_="news")[0].find_all("dl")
        latest_news = news[0]
        latest_news_date = latest_news.find("dt").text
        latest_news_obj = latest_news.find("dd").text
        ret = {"latest_news_date": latest_news_date, "latest_news_obj": latest_news_obj}

    return ret


def get_last_json() -> dict:
    _LAST_FILE = "saitamashi_cv_news_latest.json"

    if os.path.exists(_LAST_FILE):
        if os.path.getsize(_LAST_FILE) == 0:
            ret = {}
        else:
            json_open = open(_LAST_FILE, "r")
            last = json.load(json_open)
            ret = last
    else:
        ret = {}

    return ret


def update_last_json(latest_news: dict) -> dict:

    _LAST_FILE = "saitamashi_cv_news_latest.json"
    with open(_LAST_FILE, "w") as f:
        json.dump(latest_news, f, ensure_ascii=False, indent=4)

    return 0


def post_message(webhook: str, message: str):
    url = webhook
    data = {"text": message}
    headers = {
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, json.dumps(data).encode(), headers)
    with urllib.request.urlopen(req) as res:
        body = res.read().decode("utf-8")

    return body


def main():
    p = pathlib.Path(__file__).resolve().parent
    CONFIG_FILE = str(p) + "/setting.ini"
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    webhook = config["garbage_notify"]["webhook"]
    # webhook_dev = config["garbage_notify"]["webhook_dev"]

    latest_news = get_latest_news()
    if not latest_news:
        message = "requests.status_code is not ok"
        post_message(webhook, message)
        exit()

    latest_news_date = latest_news["latest_news_date"]
    latest_news_obj = latest_news["latest_news_obj"]

    last_json = get_last_json()
    if (
        last_json and (last_json["latest_news_date"] != latest_news_date)
    ) or not last_json:
        # 通知
        message = (
            "https://saitama-vaccine.com/"
            + " "
            + "最新情報が更新されました"
            + "\n"
            + "更新日 : "
            + latest_news_date
            + "\n"
            + latest_news_obj
        )
        print("notify")
        post_message(webhook, message)

    # last_json を更新する
    last = latest_news
    update_last_json(last)


if __name__ == "__main__":
    main()
