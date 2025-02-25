from docs.get_chart import chart_update, chart_update_one
from docs.cal_chart import process_chart_data
from docs.cal_position import cal_position
from docs.utility.cal_close import isclowstime
from docs.utility.load_data import load_all_data,backtest_iterator
from docs.utility.position_manager import Position, process_position
from datetime import datetime, timezone, timedelta
import time


from docs.backtest.run_backtest import run_backtest, create_parameter_grid, run_grid_search


# 프로젝트 루트 디렉토리 추가
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # 전략 활성화 설정
STRATEGY_ENABLE = {
        'SUPERTREND': False,      # 슈퍼트렌드 전략 (체크 완료)
        'LINEAR_REG': False,  # 선형회귀 전략 (체크 완료)
        'VOLUME_NORM': False,      # 볼륨 정규화 전략 (사용 안함)
        'MACD_DI_RSI': False,     # MACD-DI-RSI Slop 전략 (사용 안함)
        'MACD_SIZE': True,       # MACD 크기 전략 (체크 완료)
        'MACD_DIVE': False,  # MACD 다이버전스 전략 (체크 완료)
    }



STG_CONFIG = {
    'MACD_SIZE': {
        'STG_No' : 1,
        'MACD_FAST_LENGTH': 12,
        'MACD_SLOW_LENGTH': 17,
        'MACD_SIGNAL_LENGTH': 20,
        'SIZE_RATIO_THRESHOLD': 1.4,
        'DI_LENGTH': 18,
        'DI_SLOPE_LENGTH': 9,
        'MIN_SLOPE_THRESHOLD': 13,
        'REQUIRED_CONSECUTIVE_CANDLES': 2
    },
    'MACD_DIVE': {
        'STG_No' : 2,
        'FAST_LENGTH': 11,
        'SLOW_LENGTH': 27,
        'SIGNAL_LENGTH': 12,
        'HISTOGRAM_UPPER_LIMIT': 60,
        'HISTOGRAM_LOWER_LIMIT': -60,
        'LOOKBACK_PERIOD': 2,
        'PRICE_MOVEMENT_THRESHOLD': 0.01
    },
    'SUPERTREND': {
        'STG_No' : 3,
        'ATR_PERIOD': 30,
        'ATR_MULTIPLIER': 6,
        'ADX_LENGTH': 14,
        'DI_DIFFERENCE_FILTER': 8,
        'DI_DIFFERENCE_LOOKBACK_PERIOD': 6
    },
    'LINEAR_REG': {
        'STG_No' : 4,
        'LENGTH': 100,
        'RSI_LENGTH': 14,
        'RSI_LOWER_BOUND': 40,
        'RSI_UPPER_BOUND': 60,
        'MIN_BOUNCE_BARS': 4,
        'UPPER_MULTIPLIER': 3,
        'LOWER_MULTIPLIER': 3,
        'MIN_SLOPE_VALUE': 6,
        'MIN_TREND_DURATION': 50
    },
    'MACD_DI_SLOPE': {
        'STG_No' : 5,
        'FAST_LENGTH': 12,
        'SLOW_LENGTH': 26,
        'SIGNAL_LENGTH': 8,
        'DI_LENGTH': 14,
        'SLOPE_LENGTH': 3,
        'RSI_LENGTH': 14,
        'RSI_UPPER_BOUND': 60,
        'RSI_LOWER_BOUND': 40,
        'MIN_SLOPE_THRESHOLD': 6,
        'REQUIRED_CONSECUTIVE_SIGNALS': 5
    },
    'VOLUME_TREND': {
        'STG_No' : 6,
        'VOLUME_MA_LENGTH': 9,
        'TREND_PERIOD': 11,
        'SIGNAL_THRESHOLD': 0.2,
        'NORM_PERIOD' : 100
    }
}



# 설정값
TRADING_CONFIG = {
    'symbol': 'BTCUSDT',
    'leverage': 5,
    'usdt_amount': 0.3,
    'set_timevalue': '5m',
    'take_profit': 400,
    'stop_loss': 400
}

TIME_VALUES = {
    '1m': 1,
    '3m': 3,
    '5m': 5,
    '15m': 15
}

TAG_TPSL = {
    'st' : {'tp' : 700, 'sl' : 700}
    ,'vn' : {'tp' : 800, 'sl' : 800}
    ,'lr' : {'tp' : 800, 'sl' : 800}
    ,'sl' : {'tp' : 400, 'sl' : 400}
    ,'sz' : {'tp' : 800, 'sl' : 800}
    ,'dv' : {'tp' : 800, 'sl' : 800}
}

test_stragy = 'st'
isUpdate = False

def get_time_block(dt, interval):
    """datetime 객체를 interval 분 단위로 표현"""
    return (dt.year, dt.month, dt.day, dt.hour, (dt.minute // interval) * interval)

def get_next_run_time(current_time, interval_minutes):
    """다음 실행 시간 계산"""
    minute_block = (current_time.minute // interval_minutes + 1) * interval_minutes
    next_time = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=minute_block)
    return next_time

def main():
    try:
        config = TRADING_CONFIG

        stg_tag = None
        stg_side = None
        global trigger_first_active, trigger_first_count, position_first_active, position_first_count, position_save

        # 차트 업데이트
        if False:
            # 초기 차트 동기화
            last_time, server_time = chart_update(config['set_timevalue'], config['symbol'])
            last_time = last_time['timestamp']
            server_time = datetime.fromtimestamp(server_time, timezone.utc)
        


            while get_time_block(server_time, TIME_VALUES[config['set_timevalue']]) != get_time_block(last_time, TIME_VALUES[config['set_timevalue']]):
                print(f"{config['set_timevalue']} 차트 업데이트 중...")
                last_time, server_time = chart_update(config['set_timevalue'], config['symbol'])
                last_time = last_time['timestamp'].astimezone(timezone.utc)
                server_time = datetime.fromtimestamp(server_time, timezone.utc)
                time.sleep(60)
                
            print(f"{config['set_timevalue']} 차트 업데이트 완료")

        iscompony = True
        total_df = load_all_data('5m',iscompony)

        # pass

        # df_calculated = process_chart_data(total_df, STG_CONFIG, STRATEGY_ENABLE)
        
        # pass
        # position, df, tag = cal_position(df=df_calculated, STG_CONFIG = STG_CONFIG, STRATEGY_ENABLE = STRATEGY_ENABLE)  # 포지션은 숏,롱,None, hma롱, hma숏

        # 시그널 컬럼 매핑 정의
        SIGNAL_COLUMNS = {
            'SUPERTREND': 'filtered_position',
            'LINEAR_REG': 'line_reg_signal',
            'MACD_SIZE': 'macd_size_signal',
            'MACD_DIVE': 'macd_dive_signal'
        }
        import numpy as np

        parameter_ranges = {
            'MACD_SIZE': {
                'MACD_FAST_LENGTH': range(12, 13, 1),      # 고정값 12
                'MACD_SLOW_LENGTH': range(17, 18, 1),      # 고정값 17
                'MACD_SIGNAL_LENGTH': range(5, 100, 5),    # 5-100 (5단위)
                'SIZE_RATIO_THRESHOLD': [round(x, 1) for x in np.arange(0.7, 1.8, 0.1)],  # 0.7-1.8 (0.1단위)
                'DI_LENGTH': range(10, 21, 1),             # 10-20 (1단위)
                'DI_SLOPE_LENGTH': range(7, 16, 1),        # 7-15 (1단위)
                'MIN_SLOPE_THRESHOLD': range(12, 19, 1),   # 12-18 (1단위)
                'REQUIRED_CONSECUTIVE_CANDLES': range(1, 3, 1)  # 1-2 (1단위)
            },
            'MACD_DIVE': {
                'FAST_LENGTH': range(10, 21, 1),           # 10-20 (1단위)
                'SLOW_LENGTH': range(21, 32, 1),           # 21-31 (1단위)
                'SIGNAL_LENGTH': range(10, 25, 2),         # 10-24 (2단위)
                'HISTOGRAM_UPPER_LIMIT': range(50, 101, 10),  # 50-100 (10단위)
                'HISTOGRAM_LOWER_LIMIT': range(-100, -49, 10),  # -100--50 (10단위)
                'LOOKBACK_PERIOD': range(2, 3, 1),         # 고정값 2
                'PRICE_MOVEMENT_THRESHOLD': [round(x, 2) for x in np.arange(0.01, 0.06, 0.01)]  # 0.01-0.05 (0.01단위)
            },
            'SUPERTREND': {
                'ATR_PERIOD': range(30, 31, 1),            # 고정값 30
                'ATR_MULTIPLIER': range(4, 9, 1),          # 4-8 (1단위)
                'ADX_LENGTH': range(10, 19, 1),            # 10-18 (1단위)
                'DI_DIFFERENCE_FILTER': range(6, 11, 1),   # 6-10 (1단위)
                'DI_DIFFERENCE_LOOKBACK_PERIOD': range(4, 9, 1)  # 4-8 (1단위)
            },
            'LINEAR_REG': {
                'LENGTH': range(50, 151, 25),              # 50-150 (25단위)
                'RSI_LENGTH': range(14, 15, 1),            # 고정값 14
                'RSI_LOWER_BOUND': range(20, 36, 5),       # 20-35 (5단위)
                'RSI_UPPER_BOUND': range(65, 81, 5),       # 65-80 (5단위)
                'MIN_BOUNCE_BARS': range(2, 7, 1),         # 2-6 (1단위)
                'UPPER_MULTIPLIER': range(3, 4, 1),        # 고정값 3
                'LOWER_MULTIPLIER': range(3, 4, 1),        # 고정값 3
                'MIN_SLOPE_VALUE': range(4, 11, 1),        # 4-10 (1단위)
                'MIN_TREND_DURATION': range(30, 81, 5)     # 30-80 (5단위)
            }
        }
        '''각 전략의 모든 파라미터에 대해 적절한 범위를 설정했습니다. 주석으로 각 범위의 실제 값을 표시했습니다.
특히 MACD_SIZE의 SIZE_RATIO_THRESHOLD는 실제 사용 시 10으로 나눠서 사용해야 합니다 (1.2-1.6 사이의 값을 만들기 위해).
MACD_DIVE의 PRICE_MOVEMENT_THRESHOLD도 100으로 나눠서 사용해야 할 것 같습니다 (0.01-0.20 사이의 값을 만들기 위해).'''

        saved_file = run_grid_search(
            df=total_df,
            parameter_ranges=parameter_ranges,
            process_chart_data=process_chart_data,
            cal_position=cal_position,  # cal_position 함수 추가
            STG_CONFIG=STG_CONFIG,
            STRATEGY_ENABLE=STRATEGY_ENABLE,
            TAG_TPSL=TAG_TPSL,
            SIGNAL_COLUMNS=SIGNAL_COLUMNS
        )
        print(f"백테스트 결과가 저장된 파일: {saved_file}")

    except Exception as e:
        import traceback
        print("Traceback:")
        traceback.print_exc()
        print(f"오류 발생: {e}")
        return False


    
if __name__ == "__main__":
    main()