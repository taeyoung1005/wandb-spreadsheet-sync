import math
from datetime import datetime
import schedule
import json
import time

import wandb
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import argparse

''' To-Do list
1. config에서 NAME 제거 -> script 실행 시 user_name 입력하도록

2. Parser option 추가
- scedule time (default=30)
- User name input ('1' 기능 대체)

3. W&B API login 기능 제거 (main script file에서 이미 login 했다고 가정)

4. SEED option 제거 (무의미한 기능이라 판단)

5. UI update : tqdm 기능 추가

6. Rename : GOOGLE_CLOUD_PLATFORM_JSON -> GCP_JSON

'''

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--time', type=int, default=30, help='Set schedule time')
    parser.add_argument('--user_name', type=str, required=True, help='Input user name')
    args = parser.parse_args()

    return args


# 특수 문자 정리 함수
def clean_field_name(field_name):
    return field_name.replace("/", "_")


# 기존 스프레드시트 데이터를 가져와 run_id 리스트로 반환
def get_existing_run_ids(sheet):
    sheet_data = sheet.get_all_records()
    return [row["run_id"] for row in sheet_data], sheet_data


# NaN 값 처리를 포함한 데이터를 문자열로 변환하는 함수
def convert_row_to_str(row):
    return [
        str(value) if not (isinstance(value, float) and math.isnan(value)) else ""
        for value in row.values()
    ]


# 동적 헤더 추출 함수
def get_dynamic_headers(runs):
    dynamic_headers = set()
    for run in runs[:1]:
        dynamic_headers.update(run.config.keys())
        dynamic_headers.update(run.summary.keys())
    return list(dynamic_headers)

### 구분선 ###

def main(args) :
    ###


if __name__ == '__main__':
    args = parse_args()
    main(args)