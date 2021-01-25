#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
よくいくスーパーのチラシをスクレイピングで取得して更新があればSlackにPOSTするスクリプト
"""
import sys, os
import datetime, time
import traceback
import json
import pathlib
import configparser
import requests
import urllib.request
import git
from bs4 import BeautifulSoup

def files_upload (token:str, channel:str, f:str, comment:str):
    """
    Slackチャンネルへファイルをアップロードする
    """
    url = 'https://slack.com/api/files.upload'
    files = {'file': open(f, 'rb')}
    data = {
        'token': token,
        'channels': channel,
        'filename': f,
        'initial_comment': comment,
        'filetype': 'jpg',
        'file': files
    }
    res = requests.post(url, data=data, files=files)
    return res

def iw (webhook_url:str, message:str):
    """
    SlackチャンネルへIncomingWebhookを使ってメッセージをポストする
    """
    data = json.dumps({
    'text' : message
    })
    res = requests.post(webhook_url, data=data)
    return res

def dl (url:str, title:str) -> str:
    """
    ファイルをダウンロードしローカルに保存する
    """
    urllib.request.urlretrieve(url,'{0}'.format(title))
    return title

def prev_flayer () -> dict:
    """
    前回取得したチラシ情報を取得する
    """
    json_url = 'https://mollinaca.github.io/hstn-family-scripts/flayer/latest.json'
#   json_url = 'https://mollinaca.github.io/hstn-family-scripts/flayer/latest_test.json'
    req = urllib.request.Request(json_url)
    with urllib.request.urlopen(req) as res:
        body = json.load(res)

    return body

def get_flayers (s:str) -> dict:
    """
    引数 s に指定された店舗のチラシデータを取得して dict に加工して返す
    対象の s を増やしたい場合はここの中に増やす
    現在 s として指定できるものは
     - yorkmart
     - meatmeet
     - gyomusuper
    の3種
    チラシ情報の取得はそれぞれ別の関数に外だししている
    """
    flayers = {}

    if s == "yorkmart":
        flayers = get_flayers_york()
    elif s == "meatmeet":
        flayers = get_flayers_meatmeet()
    elif s == "gyomusuper":
        flayers = get_flayers_gyomusuper()
    else:
        return flayers

    return flayers

def get_flayers_york () -> dict:
    """
    ヨークマートのチラシ情報
    """
    dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # 最新のチラシのファイル名を取得
    york_url = 'https://www.york-inc.com'
    load_url = york_url + '/store/%e5%a4%a7%e5%ae%ae%e5%8d%97%e4%b8%ad%e9%87%8e%e5%ba%97.html'
    res = requests.get(load_url)
    html = BeautifulSoup(res.content, 'html.parser')
    leaflet = html.find_all(class_='leaflet pc')
    yorkmart_flayers = []
    for l in leaflet:
        for l2 in list(l.findAll('img')[0].get('data-set').split(',')):
            if 'ul-files' in l2:
                yorkmart_flayers.append(york_url + l2)

    ret = {'updated_at':dt_now, 'flayers':yorkmart_flayers}
    return ret

def get_flayers_meatmeet () -> dict:
    """
    ミートミートのチラシ情報
    """
    dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # チラシページURLを取得
    tokubai_url = 'https://tokubai.co.jp'
    meatmeet_url = tokubai_url + '/MEATMeet%E9%A3%9F%E8%82%89%E5%8D%B8%E5%A3%B2%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC/174289'
    req = urllib.request.Request(meatmeet_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    html = BeautifulSoup(body, 'html.parser')
    leaflet_page_url = tokubai_url + html.findAll(class_='leaflet_component')[0].find(class_='image_element').get('href')
    req = urllib.request.Request(leaflet_page_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    html = BeautifulSoup(body, 'html.parser')
    leaflet_page_link = html.find_all(class_='other_leaflet_link')

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

        html = BeautifulSoup(body, 'html.parser')
        leaflet_links.append(html.find(class_='leaflet').get('src').split('?')[0])

    ret = {'updated_at':dt_now, 'flayers':leaflet_links}
    return ret

def get_flayers_gyomusuper () -> dict:
    """
    業務スーパー 浦和花月（関東）のチラシ
    """
    dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # チラシページURLを取得
    tokubai_url = 'https://tokubai.co.jp'
    gs_url = tokubai_url + '/%E6%A5%AD%E5%8B%99%E3%82%B9%E3%83%BC%E3%83%91%E3%83%BC/169887'
    req = urllib.request.Request(gs_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    html = BeautifulSoup(body, 'html.parser')
    leaflet_page_url = tokubai_url + html.findAll(class_='leaflet_component')[0].find(class_='image_element').get('href')
    req = urllib.request.Request(leaflet_page_url)
    with urllib.request.urlopen(req) as res:
        body = res.read()
    html = BeautifulSoup(body, 'html.parser')
    leaflet_page_link = html.find_all(class_='other_leaflet_link')

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

        html = BeautifulSoup(body, 'html.parser')
        leaflet_links.append(html.find(class_='leaflet').get('src').split('?')[0])

    ret = {'updated_at':dt_now, 'flayers':leaflet_links}
    return ret


###############
# main
###############
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

    # 取得対象とする店舗一覧
    stores = ['yorkmart', 'meatmeet', 'gyomusuper']

    try:
        # 動作確認用
        m = '[debug] flayers.py を実行しました dt: ' + dt_now
        iw (webhook_dev, m)
        # 動作確認用ここまで

        SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
        OUTPUT_DIR = pathlib.Path(str(SCRIPT_DIR) + '/docs/flayer/')
        isNew = False

        ### 前回取得した情報 (latest.json) を再取得
        pf = prev_flayer ()

        ### 店ごとの処理 ###
        for store in stores:
            print (store)
            flayers = get_flayers(store)
            if set(flayers['flayers']) == set(pf['detail'][store]['flayers']):
                text = '[debug] ' + store + ' has no changed.'
                print (text)
                iw (webhook_dev, text)
            else:
                text = '[debug] ' + store + ' : got flayers info changes'
                print (text)
                iw (webhook_dev, text)
                for flayer_url in flayers['flayers']:
                    if flayer_url not in pf['detail'][store]['flayers']:
                        # img ファイルを取得
                        filename = flayer_url.split('/')[-1]
                        comment = flayer_url
                        dl (flayer_url, filename)

                        # Slack へPOSTする
                        ret = files_upload (token, channel, filename, comment)
#                       ret = files_upload (token, channel_dev, filename, comment)
                        if not ret.status_code == 200:
                            time.sleep (61) # 61秒 sleep してリトライ
                            ret = files_upload (token, channel, filename, comment)
#                           ret = files_upload (token, channel_dev, filename, comment)
                            if not ret.status_code == 200:
                                    print ('[debug] ' + 'requests response not <200 OK> ->', ret.headers['status'], filename, file=sys.stderr)
                        # ファイルをローカルから削除
                        os.remove (filename)
                    else:
                        pass
                    # img ファイルの操作 ここまで

                pf['detail'][store] = flayers
                isNew = True

        if isNew:
            # ファイルを更新
            pf['updated_at'] = dt_now
            OUTPUT_FILE_NAME = 'latest.json'
            OUTPUT_FILE = pathlib.Path(str(OUTPUT_DIR) + '/' + OUTPUT_FILE_NAME)

            with open(OUTPUT_FILE, mode='w') as f:
                f.write(json.dumps(pf, indent=4))

            # git 
            git_repo= git.Repo(SCRIPT_DIR)
            git_repo.index.add(str(OUTPUT_FILE))
            commit_message = '[auto] update ' + str(OUTPUT_FILE_NAME)
            git_repo.index.commit(commit_message)
            git_repo.remotes.origin.push('HEAD')

    except Exception as e:
        err_msg = '```' + '[Exception]\n' + str(e) + '\n' + '[StackTrace]' + '\n' + traceback.format_exc() + '```'
        iw (webhook_dev, err_msg)


if __name__ == '__main__':
    main ()
