import math
from datetime import datetime
import schedule
import json
import time

import wandb
import gspread
from oauth2client.service_account import ServiceAccountCredentials

config_json = json.load(open("config.json", "r"))
# 이름과 wandb ID 매핑 -> 누가 wandb에 올렸는지 확인하기 위함
NAME = config_json["NAME"]

# spreadsheet에 먼저 추가할 헤더 설정
FIXED_HEADERS = config_json["FIXED_HEADERS"]

API_KEY = config_json["API_KEY"]
GOOGLE_CLOUD_PLATFORM_JSON = config_json["GOOGLE_CLOUD_PLATFORM_JSON"]
SPREADSHEET_NAME = config_json["SPREADSHEET_NAME"]
TEAM_NAME = config_json["TEAM_NAME"]
PROJECT_NAME = config_json["PROJECT_NAME"]


# Config 설정 함수
def config():
    # W&B API Key 설정
    wandb.login(key=API_KEY)

    # Google Spreadsheet 인증 설정
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        GOOGLE_CLOUD_PLATFORM_JSON, scope
    )
    client = gspread.authorize(creds)

    # 스프레드시트 열기
    spreadsheet = client.open(SPREADSHEET_NAME)
    sheet = spreadsheet.sheet1  # 첫 번째 시트를 사용

    # W&B 프로젝트와 연결
    api = wandb.Api()
    runs = api.runs(f"{TEAM_NAME}/{PROJECT_NAME}")

    return sheet, runs


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


# WandB 데이터 처리 함수
def process_wandb_data(runs, run_id_list, final_headers):
    rows_to_add = []
    for run in runs:
        if run.state == "finished" and run.id not in run_id_list:
            row_data = [
                run.id,  # run_id
                (
                    datetime.fromtimestamp(run.summary["_timestamp"]).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if "_timestamp" in run.summary
                    else ""
                ),  # _timestamp
                NAME.get(run.user.name, run.user.name),  # name
            ]
            # 고정된 열들에 대한 데이터 추가
            for key in final_headers[
                3:
            ]:  # 이미 run_id, _timestamp, name 추가되었으므로 3번째 인덱스부터
                key = clean_field_name(key)
                if key in run.config:
                    row_data.append(str(run.config[key]))
                elif key in run.summary:
                    row_data.append(str(run.summary[key]))
                else:
                    row_data.append("")  # 해당 키에 데이터가 없으면 빈 값 추가
            rows_to_add.append(row_data)
    return rows_to_add


def main():
    sheet, runs = config()

    # 기존 스프레드시트에서 run_id 가져오기
    run_id_list, sheet_data = get_existing_run_ids(sheet)

    # 기존 데이터를 문자열로 변환하여 temp 리스트에 저장
    temp = [convert_row_to_str(row) for row in sheet_data]

    # 동적 헤더 추출
    dynamic_headers = get_dynamic_headers(runs)

    # 고정된 헤더와 동적 헤더를 합쳐 최종 헤더 구성
    final_headers = FIXED_HEADERS + [
        key for key in dynamic_headers if key not in FIXED_HEADERS
    ]

    # 스프레드시트에 헤더 추가
    sheet.clear()  # 기존 데이터 삭제
    sheet.append_row(final_headers)  # 헤더 추가

    # WandB 데이터 처리 후 추가할 데이터 생성
    new_rows = process_wandb_data(runs, run_id_list, final_headers)

    # 새로운 데이터와 기존 데이터 결합 후 날짜순으로 정렬
    merged_data = new_rows + temp
    merged_data.sort(key=lambda x: x[1], reverse=True)

    # 스프레드시트에 추가
    sheet.append_rows(merged_data)

    print("W&B 데이터를 내림차순으로 헤더와 함께 Google 스프레드시트에 추가했습니다.")


if __name__ == "__main__":
    schedule.every(30).minutes.do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
