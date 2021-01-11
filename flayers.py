#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
よくいくスーパーのチラシをスクレイピングで取得して更新があればSlackにPOSTする
"""
import sys, os
import traceback
import pathlib
import requests
import urllib.request
import configparser
import json
import datetime, time
import git
from bs4 import BeautifulSoup

def files_upload (token:str, channel:str, f:str, comment:str):
    """
    Slackチャンネルへファイルをアップロードする
    """
    url = "https://slack.com/api/files.upload"
    files = {'file': open(f, 'rb')}
    data = {
        'token': token,
        'channels': channel,
        'filename': f,
        'initial_comment': comment,
        'filetype': "jpg"
    }
    res = requests.post(url, data=data, files=files)
    return res

def iw (webhook:str, message:str):
    """
    SlackチャンネルへIncomingWebhookを使ってメッセージをポストする
    """
    data = json.dumps({
    "text" : message
    })
    res = requests.post(webhook, data)
    return res

def prev_flayer () -> dict:
    """
    前回取得したチラシ情報を取得
    """
    json_url = 'https://mollinaca.github.io/hstn-family-scripts/flayer/latest.json'
    res = requests.get(json_url).json()

    return res

def dl (url:str, title:str) -> str:
    urllib.request.urlretrieve(url,"{0}".format(title))
    return title

def york () -> dict:
    """
    ヨークマートのチラシ情報
    """
    dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # 最新のチラシのファイル名を取得
    york_url = "https://www.york-inc.com"
    load_url = york_url + "/store/%e5%a4%a7%e5%ae%ae%e5%8d%97%e4%b8%ad%e9%87%8e%e5%ba%97.html"
    res = requests.get(load_url)
    html = BeautifulSoup(res.content, "html.parser")
    leaflet = html.find_all(class_='leaflet pc')
    yorkmart_flayers = []
    for l in leaflet:
        for l2 in list(l.findAll('img')[0].get('data-set').split(',')):
            if "ul-files" in l2:
                yorkmart_flayers.append(york_url + l2)

    ret = {'updated_at':dt_now, 'flayers':yorkmart_flayers}
    return ret

def meatmeet () -> dict:
    """
    ミートミート木崎のチラシ情報
    """
    dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # 最新のチラシのファイル名を取得

    # チラシページURLを取得
    tokubai_url = "https://tokubai.co.jp"
    meatmeet_url = tokubai_url + "/MEATMeet%E9%A3%9F%E8%82%89%E5%8D%B8%E5%A3%B2%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC/174289"
    req = urllib.request.Request(meatmeet_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    html = BeautifulSoup(body, "html.parser")
    leaflet_page_url = tokubai_url + html.findAll(class_="leaflet_component")[0].find(class_="image_element").get('href')
    req = urllib.request.Request(leaflet_page_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    html = BeautifulSoup(body, "html.parser")
    leaflet_page_link = html.find_all(class_="other_leaflet_link")

    # チラシページリンクのチラシページリンクURL（複数）を取得
    leaflet_page_links = []
    for l in leaflet_page_link:
        leaflet_page_links.append(tokubai_url + l.get('href').split('?')[0])

    # 各チラシページリンクURLを開いて、チラシの画像ファイルURLを取得
    leaflet_links = []
    for url in leaflet_page_links:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as res:
            body = res.read()

        html = BeautifulSoup(body, "html.parser")
        leaflet_links.append(html.find(class_='leaflet').get('src').split("?")[0])

    ret = {'updated_at':dt_now, 'flayers':leaflet_links}
    return ret

def gyomusuper () -> dict:
    """
    業務スーパー 浦和花月（関東）のチラシ
    """
    dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # 最新のチラシのファイル名を取得

    # チラシページURLを取得
    tokubai_url = "https://tokubai.co.jp"
    gs_url = tokubai_url + "/%E6%A5%AD%E5%8B%99%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC/169887"
    req = urllib.request.Request(gs_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    html = BeautifulSoup(body, "html.parser")
    leaflet_page_url = tokubai_url + html.findAll(class_="leaflet_component")[0].find(class_="image_element").get('href')
    req = urllib.request.Request(leaflet_page_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    html = BeautifulSoup(body, "html.parser")
    leaflet_page_link = html.find_all(class_="other_leaflet_link")

    # チラシページリンクのチラシページリンクURL（複数）を取得
    leaflet_page_links = []
    for l in leaflet_page_link:
        leaflet_page_links.append(tokubai_url + l.get('href').split('?')[0])

    # 各チラシページリンクURLを開いて、チラシの画像ファイルURLを取得
    leaflet_links = []
    for url in leaflet_page_links:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as res:
            body = res.read()

        html = BeautifulSoup(body, "html.parser")
        leaflet_links.append(html.find(class_='leaflet').get('src').split("?")[0])

    ret = {'updated_at':dt_now, 'flayers':leaflet_links}
    return ret


def main():
    dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    p = pathlib.Path(__file__).resolve().parent
    config = configparser.ConfigParser()
    config.read(str(p)+'/setting.ini')
    token = config['flayers']['token']
    webhook = config['flayers']['webhook']
    webhook_dev = config['flayers']['webhook_dev']
    channel = config['flayers']['channel']
    channel_dev = config['flayers']['channel_dev']

    try:
        # 動作確認用
        m = "[動作確認用] flayers.py を実行しました dt: " + dt_now
        iw (webhook_dev, m)
        # 動作確認用ここまで

        SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
        OUTPUT_DIR = pathlib.Path(str(SCRIPT_DIR) + "/docs/flayer/")
        stores = ['yorkmart', 'meatmeet', 'gyomusuper',  'supervalue']
        isNew = False

        ### 前回取得した情報 (latest.json) を再取得
        pf = prev_flayer ()

        ### 店ごとの処理 ###
        for store in stores:
            if store == 'yorkmart': # ヨークマート
                print (store)
                y = york ()
                if set(y['flayers']) == set(pf['detail']['yorkmart']['flayers']):
                    print (" -> flayers not renewed")
                    text = "[動作確認用] " + store + " のチラシは更新されていませんでいした"
                    iw (webhook_dev, text)
                else:
                    print (" -> got new flayers!")
                    text = "ヨークマート の新しいチラシを取得しました！"
                    iw (webhook, text)
                    iw (webhook_dev, text)
                    pf['detail']['yorkmart'] = y
                    isNew = True

                    # img ファイルを取得
                    for flayer_url in y['flayers']:
                        filename = flayer_url.split("/")[-1]
                        comment = flayer_url
                        dl (flayer_url, filename)

                        # Slack へPOSTする
                        ret = files_upload (token, channel, filename, comment)
                        #ret = files_upload (token, channel_dev, filename, comment)
                        if not ret.status_code == 200:
                            time.sleep (61) # 61秒 sleep してリトライ
                            ret = files_upload (token, channel, filename, comment)
                            #ret = files_upload (token, channel_dev, filename, comment)
                            if not ret.status_code == 200:
                                print ("[error] requests response not <200 OK> ->", ret.headers['status'], filename, file=sys.stderr)
                        else:
                            pass

                        # ファイルをローカルから削除
                        os.remove (filename)

            elif store == 'meatmeet': # ミートミート
                print (store)
                m = meatmeet ()
                if ('meatmeet' in pf['detail']) and set(m['flayers']) == set(pf['detail']['meatmeet']['flayers']):
                    print (" -> flayers not renewed")
                    text = "[動作確認用] " + store + " のチラシは更新されていませんでいした"
                    iw (webhook_dev, text)
                else:
                    print (" -> got new flayers!")
                    text = "ミートミート木崎 の新しいチラシを取得しました！"
                    iw (webhook, text)
                    iw (webhook_dev, text)
                    pf['detail']['meatmeet'] = m
                    isNew = True

                    # img ファイルを取得
                    for flayer_url in m['flayers']:
                        filename = flayer_url.split("/")[-1]
                        comment = flayer_url
                        dl (flayer_url, filename)

                        # Slack へPOSTする
                        ret = files_upload (token, channel, filename, comment)
                        #ret = files_upload (token, channel_dev, filename, comment)
                        if not ret.status_code == 200:
                            time.sleep (61) # 61秒 sleep してリトライ
                            ret = files_upload (token, channel, filename, comment)
                            #ret = files_upload (token, channel_dev, filename, comment)
                            if not ret.status_code == 200:
                                print ("[error] requests response not <200 OK> ->", ret.headers['status'], filename, file=sys.stderr)
                        else:
                            pass

                        # ファイルをローカルから削除
                        os.remove (filename)

            elif store == 'supervalue': # スーパーバリュー
                pass

            elif store == "gyomusuper" : # 業務スーパー
                print (store)
                gs = gyomusuper ()
                if ('gyomusuper' in pf['detail']) and set(gs['flayers']) == set(pf['detail']['gyomusuper']['flayers']):
                    print (" -> flayers not renewed")
                    text = "[動作確認用] " + store + " のチラシは更新されていませんでいした"
                    iw (webhook_dev, text)
                else:
                    print (" -> got new flayers!")
                    text = "業務スーパー の新しいチラシを取得しました！"
                    iw (webhook, text)
                    iw (webhook_dev, text)
                    pf['detail']['gyomusuper'] = gs
                    isNew = True

                    # img ファイルを取得
                    for flayer_url in gs['flayers']:
                        filename = flayer_url.split("/")[-1]
                        comment = flayer_url
                        dl (flayer_url, filename)

                        # Slack へPOSTする
                        ret = files_upload (token, channel, filename, comment)
                        #ret = files_upload (token, channel_dev, filename, comment)
                        if not ret.status_code == 200:
                            time.sleep (61) # 61秒 sleep してリトライ
                            ret = files_upload (token, channel, filename, comment)
                            #ret = files_upload (token, channel_dev, filename, comment)
                            if not ret.status_code == 200:
                                print ("[error] requests response not <200 OK> ->", ret.headers['status'], filename, file=sys.stderr)
                        else:
                            pass

                        # ファイルをローカルから削除
                        os.remove (filename)

            else:
                pass

        if isNew:
            # ファイルを更新
            pf['updated_at'] = dt_now
            OUTPUT_FILE_NAME = "latest.json"
            OUTPUT_FILE = pathlib.Path(str(OUTPUT_DIR) + "/" + OUTPUT_FILE_NAME)

            with open(OUTPUT_FILE, mode='w') as f:
                f.write(json.dumps(pf, indent=4))

            # git 
            git_repo= git.Repo(SCRIPT_DIR)
            git_repo.index.add(str(OUTPUT_FILE))
            commit_message = "[auto] update " + str(OUTPUT_FILE_NAME)
            git_repo.index.commit(commit_message)
            git_repo.remotes.origin.push('HEAD')

    except Exception as e:
        err_msg = "```" + "[Exception]\n" + str(e) + "\n" + "[StackTrace]" + "\n" + traceback.format_exc() + "```"
        iw (webhook_dev, err_msg)

if __name__ == "__main__":
    main ()
