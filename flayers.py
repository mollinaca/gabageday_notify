#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
よくいくスーパーのチラシをスクレイピングで取得して更新があればSlackにPOSTする
"""
import sys, os
import pathlib
import requests
import urllib.request
import configparser
import json
import datetime, time
import git
from bs4 import BeautifulSoup

def files_upload (token:str, channel:str, f:str, comment:str):
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

# functions
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
    flayer_uri = leaflet[0].findAll('img')[0]['src']
    flayer_a = york_url + flayer_uri
    flayer_b = york_url + flayer_uri.replace('A','B')
    yorkmart_flayers = [flayer_a,flayer_b]

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
    res = requests.get(meatmeet_url)
    html = BeautifulSoup(res.content, "html.parser")
    leaflet_page_url = tokubai_url + html.find(class_='image_element').get('href')

    # チラシページのチラシページリンクURL（複数）を取得
    res = requests.get(leaflet_page_url)
    html = BeautifulSoup(res.content, "html.parser")

    leaflet_page_link = html.find_all(class_="other_leaflet_link")
    leaflet_page_links = []
    for l in leaflet_page_link:
        leaflet_page_links.append(tokubai_url + l.get('href'))

    # 各チラシページリンクURLを開いて、チラシの画像ファイルURLを取得
    leaflet_links = []
    for page in leaflet_page_links:
        res = requests.get(page)
        html = BeautifulSoup(res.content, "html.parser")
        leaflet_links.append(html.find(class_='leaflet').get('src').split("?")[0])

    ret = {'updated_at':dt_now, 'flayers':leaflet_links}
    return ret

def main():
    dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    p = pathlib.Path(__file__).resolve().parent
    config = configparser.ConfigParser()
    config.read(str(p)+'/setting.ini')
    token = config['flayers']['token']
    channel = config['flayers']['channel']

    SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
    OUTPUT_DIR = pathlib.Path(str(SCRIPT_DIR) + "/docs/flayer/")
    stores = ['yorkmart', 'meatmeet', 'supervalue', 'gyomusuper']
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
            else:
                print (" -> got new flayers!")
                pf['detail']['yorkmart'] = y
                isNew = True

                # img ファイルを取得
                for flayer_url in y['flayers']:
                    filename = flayer_url.split("/")[-1]
                    comment = flayer_url
                    dl (flayer_url, filename)

                    # Slack へPOSTする
                    res = files_upload (token, channel, filename, comment)
                    if not res.status_code == 200:
                        time.sleep (61) # 61秒 sleep してリトライ
                        ret = files_upload (token, channel, filename, comment)
                        if not res.status_code == 200:
                            print ("[error] requests response not 200 OK ->", ret.headers['status'], filename, file=sys.stderr)
                    else:
                        pass

                    # ファイルをローカルから削除
                    os.remove (filename)

        elif store == 'meatmeet': # ミートミート
            print (store)
            m = meatmeet ()
            if ('meatmeet' in pf['detail']) and set(m['flayers']) == set(pf['detail']['meatmeet']['flayers']):
                print (" -> flayers not renewed")
            else:
                print (" -> got new flayers!")
                pf['detail']['yorkmart'] = y
                isNew = True

                # img ファイルを取得
                for flayer_url in m['flayers']:
                    filename = flayer_url.split("/")[-1]
                    comment = flayer_url
                    dl (flayer_url, filename)

                    # Slack へPOSTする
                    res = files_upload (token, channel, filename, comment)
                    if not res.status_code == 200:
                        time.sleep (61) # 61秒 sleep してリトライ
                        ret = files_upload (token, channel, filename, comment)
                        if not res.status_code == 200:
                            print ("[error] requests response not 200 OK ->", ret.headers['status'], filename, file=sys.stderr)
                    else:
                        pass

                    # ファイルをローカルから削除
                    os.remove (filename)

        elif store == 'supervalue': # スーパーバリュー
            pass
        elif store =="gyomusuper" : # 業務スーパー
            pass
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

if __name__ == "__main__":
    main ()
