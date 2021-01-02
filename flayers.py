#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
よくいくスーパーのチラシをスクレイピングで取得して更新があればSlackにPOSTする
"""
import pathlib
import requests
import json
import datetime
import git
from bs4 import BeautifulSoup

def prev_flayer () -> dict:
    """
    前回取得したチラシ情報を取得
    """
    json_url = 'https://mollinaca.github.io/hstn-family-scripts/flayer/latest.json'
    res = requests.get(json_url).json()

    return res

def post_to_slack (store:str, urls:list) -> None:
    """
    Slack へ POST する
    """
    print ("post to slack:", store, urls)

    return None

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

def main():
    dt_now = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
    OUTPUT_DIR = pathlib.Path(str(SCRIPT_DIR) + "/docs/flayer/")
    stores = ['yorkmart', 'meetmeet', 'supervalue']
    isNew = False

    ### 前回取得した情報 (latest.json) を再取得
    pf = prev_flayer ()

    ### チラシ取得処理 ###
    for store in stores:
        if store == 'yorkmart':
            y = york ()
            if set(y['flayers']) == set(pf['detail']['yorkmart']['flayers']):
                pass
            else:
                pf['detail']['yorkmart'] = y
                isNew = True
            post_to_slack (store, y['flayers'])
        elif store == 'meetmeet':
            pass
        elif store == 'supervalue':
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
