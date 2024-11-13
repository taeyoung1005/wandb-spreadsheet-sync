import math
from datetime import datetime
import schedule
import json
import time

import wandb
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import argparse
from argparse import ArgumentParser

''' To-Do list
1. config에서 NAME 제거 -> script 실행 시 user_name 입력하도록

2. Parser option 추가
- scedule time (default=30)
- User name input ('1' 기능 대체)
- Spread Sheet name

3. W&B API login 기능 제거 (main script file에서 이미 login 했다고 가정)

4. SEED option 제거 (무의미한 기능이라 판단)

5. UI update : tqdm 기능 추가

6. Rename : GOOGLE_CLOUD_PLATFORM_JSON -> GCP_JSON

7. 만약 Sheet가 존재한다면(비어있지 않다면), 새로운 sheet를 생성하고 거기에 기록하도록 설정
'''

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--time', type=int, default=30, help='Set schedule time')
    parser.add_argument('--user_name', type=str, required=True, help='Input user name')
    args = parser.parse_args()

    return args

config_json = json.load(open("config.json", "r"))

# spreadsheet에 먼저 추가할 헤더 설정
FIXED_HEADERS = config_json["FIXED_HEADERS"]
API_KEY = config_json["API_KEY"]
GCP_JSON = config_json["GCP_JSON"]
SPREADSHEET_NAME = config_json["SPREADSHEET_NAME"]
TEAM_NAME = config_json["TEAM_NAME"]
PROJECT_NAME = config_json["PROJECT_NAME"]

##### 구분선 #####





##### 구분선 #####




##### 구분선 #####


def main(args) :



if __name__ == '__main__':
    args = parse_args()
    main(args)