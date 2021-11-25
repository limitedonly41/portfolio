import requests
import json
import pandas as pd
from datetime import date
import glob
import os.path
import os
import pathlib
import time
import threading


headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.binance.com/en/futuresng-activity/leaderboard',
    'lang': 'en',
    'x-ui-request-trace': 'a31e230d-a7cc-4ef0-aa01-f04486ee902d',
    'x-trace-id': 'a31e230d-a7cc-4ef0-aa01-f04486ee902d',
    'bnc-uuid': 'd48c7780-693a-4487-ab6d-7bdcd984f0dd',
    'content-type': 'application/json',
    'device-info': 'eyJzY3JlZW5fcmVzb2x1dGlvbiI6Ijg2NCwxNTM2IiwiYXZhaWxhYmxlX3NjcmVlbl9yZXNvbHV0aW9uIjoiNzkyLDE1MzYiLCJzeXN0ZW1fdmVyc2lvbiI6IlVidW50dSB1bmRlZmluZWQiLCJicmFuZF9tb2RlbCI6InVua25vd24iLCJzeXN0ZW1fbGFuZyI6ImVuLVVTIiwidGltZXpvbmUiOiJHTVQrMyIsInRpbWV6b25lT2Zmc2V0IjotMTgwLCJ1c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFgxMTsgVWJ1bnR1OyBMaW51eCB4ODZfNjQ7IHJ2Ojg1LjApIEdlY2tvLzIwMTAwMTAxIEZpcmVmb3gvODUuMCIsImxpc3RfcGx1Z2luIjoiIiwiY2FudmFzX2NvZGUiOiI5ODcxODY3YSIsIndlYmdsX3ZlbmRvciI6IlguT3JnIiwid2ViZ2xfcmVuZGVyZXIiOiJBTUQgUkFWRU4yIChEUk0gMy4zOC4wLCA1LjguMC00My1nZW5lcmljLCBMTFZNIDExLjAuMCkiLCJhdWRpbyI6IjM1LjczODMzNDAyMjQ2MjM3IiwicGxhdGZvcm0iOiJMaW51eCB4ODZfNjQiLCJ3ZWJfdGltZXpvbmUiOiJFdXJvcGUvTW9zY293IiwiZGV2aWNlX25hbWUiOiJGaXJlZm94IFY4NS4wIChVYnVudHUpIiwiZmluZ2VycHJpbnQiOiIyNzFhNmJiNGViM2E5OGJmNTNhNGVhMGMwMjUxZjAyZCIsImRldmljZV9pZCI6IiIsInJlbGF0ZWRfZGV2aWNlX2lkcyI6IiJ9',
    'clienttype': 'web',
    'fvideo-id': '3163ababb858a6e4b454321ad6a0603ffa474b9a',
    'csrftoken': 'd41d8cd98f00b204e9800998ecf8427e',
    'Origin': 'https://www.binance.com',
    'Connection': 'keep-alive',
    'TE': 'Trailers',
}

data_usd_roi = '{"isShared":false,"periodType":"DAILY","statisticsType":"ROI","tradeType":"PERPETUAL"}'

data_usd_pnl = '{"isShared":false,"periodType":"DAILY","statisticsType":"PNL","tradeType":"PERPETUAL"}'

data_coin_roi = '{"isShared":false,"periodType":"DAILY","statisticsType":"ROI","tradeType":"DELIVERY"}'

data_coin_pnl = '{"isShared":false,"periodType":"DAILY","statisticsType":"PNL","tradeType":"DELIVERY"}'


datas = {
    'usd_roi': data_usd_roi,
    'usd_pnl': data_usd_pnl,
    'coin_roi': data_coin_roi,
    'coin_pnl': data_coin_pnl
}

def write_to_csv(data, type_of_data):
    n = 0

    files_name = []

    today = date.today()

    directory_name = 'data'

    folder_name = str(type_of_data)

    full_dir_path = f"{directory_name}/{folder_name}"

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        os.makedirs(full_dir_path)
    
    if not os.path.exists(full_dir_path):
        os.makedirs(full_dir_path)

    path = pathlib.Path(__file__).parent.absolute()
    csv_files = glob.glob(os.path.join(path, directory_name, folder_name, '*.zip'))

    if len(csv_files) > 0:
        for f in csv_files:
            name = f.split("/")[-1]
            name = name.split(".")[0]
            name = name.split("-")[-1]

            files_name.append(name)

        n = str(int(max(files_name)) + 1)
    # Month abbreviation, day and year	
    file_name_date = str(today.strftime("%Y-%m-%d"))
    file_name_full = file_name_date + f"-{n}"

    df = pd.DataFrame(data)
    df = df[['rank', 'nickName', 'value', 'positionShared']]
    print(str(type_of_data))
    if str(type_of_data) == 'usd_roi' or 'coin_roi':
        print("!!!!!")
        df['value'] = df['value'].apply(lambda x: x*100_000)
    compression_opts = dict(method='zip',
                        archive_name=f'{file_name_full}.csv')  

    df.to_csv(f'{full_dir_path}/{file_name_full}.zip', index=False,
          compression=compression_opts)  



def get_data(timing, data, name):


    response = requests.post('https://www.binance.com/gateway-api/v1/public/future/leaderboard/getLeaderboardRank', headers=headers, data=data)

    text = response.text
    text = json.loads(text)

    write_to_csv(text['data'], name)


def run():
    for k in datas.keys():
        get_data(1, datas[k], k)



def start():
    threading.Timer(1800, start).start()
    run()

start()



