from pymongo import MongoClient
import pandas as pd

import sys
import os
# 현재 스크립트 파일의 디렉토리 경로 가져오기
current_dir = os.path.dirname(os.path.abspath(__file__))
# CSV 파일 경로 설정
file_path = os.path.join(current_dir, "bitcoin_chart_5m_new.csv")

def load_all_data(set_timevalue,iscompony):
    if iscompony:
        df = pd.read_csv(file_path)
    else:
        # MongoDB에 접속
        mongoClient = MongoClient("mongodb://localhost:27017")
        database = mongoClient["bitcoin"]

        # set_timevalue 값에 따라 적절한 차트 컬렉션 선택
        collection_map = {
            '1m': 'chart_1m',
            '3m': 'chart_3m',
            '5m': 'chart_5m_new',
            '15m': 'chart_15m',
            '1h': 'chart_1h',
            '30d': 'chart_30d'
        }
        
        if set_timevalue not in collection_map:
            raise ValueError(f"Invalid time value: {set_timevalue}")
            
        chart_collection = database[collection_map[set_timevalue]]
        
        # 시간순으로 전체 데이터 가져오기
        data_cursor = chart_collection.find().sort("timestamp", 1)
        data_list = list(data_cursor)

        # MongoDB 데이터를 DataFrame으로 변환
        df = pd.DataFrame(data_list)

    # 타임스탬프를 datetime 형식으로 변환
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # 불필요한 ObjectId 필드 제거
    if '_id' in df.columns:
        df.drop('_id', axis=1, inplace=True)

    # 인덱스를 타임스탬프로 설정
    df.set_index('timestamp', inplace=True)

    # 마지막 행을 제외한 전체 데이터 반환
    return df.iloc[:-1]

def backtest_iterator(df, window_size=300):
    """
    데이터프레임을 window_size 크기의 윈도우로 순차적으로 분할하여 반환하는 제너레이터
    """
    total_rows = len(df)
    for start_idx in range(0, total_rows - window_size + 1):
        yield df.iloc[start_idx:start_idx + window_size]
