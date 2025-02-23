def run_backtest(df, TAG_TPSL, STRATEGY_ENABLE, SIGNAL_COLUMNS, initial_capital=1000000):
    """
    백테스팅 실행 함수
    Args:
        df: 계산된 데이터프레임
        TAG_TPSL: TP/SL 설정값 딕셔너리
        STRATEGY_ENABLE: 전략 활성화 설정 딕셔너리
        SIGNAL_COLUMNS: 시그널 컬럼명 매핑 딕셔너리
        initial_capital: 초기 자본
    """
    results = {
        'trades': [],
        'capital': initial_capital,
        'wins': 0,
        'losses': 0
    }
    
    # 활성화된 전략 찾기
    active_strategy = next((k for k, v in STRATEGY_ENABLE.items() if v), None)
    if not active_strategy:
        return "활성화된 전략이 없습니다."

    signal_column = SIGNAL_COLUMNS[active_strategy]

    # 각 전략에 맞는 명확한 태그 매핑
    strategy_tag_map = {
        'SUPERTREND': 'st',
        'LINE_REGRESSION': 'lr',
        'VOLUME_NORM': 'vn',
        'MACD_DI_RSI': 'sl',
        'MACD_SIZE': 'sz',
        'MACD_DIVERGENCE': 'dv'
    }

    strategy_tag = strategy_tag_map.get(active_strategy)
    if not strategy_tag:
        return "유효하지 않은 전략입니다."
    in_position = False
    entry_price = 0
    entry_type = None
    
    for i in range(1, len(df)):  # 1부터 시작하여 이전 봉의 시그널 확인
        if in_position:
            current_high = df['high'].iloc[i]
            current_low = df['low'].iloc[i]
            is_bullish = df['close'].iloc[i] >= df['open'].iloc[i]
            
            # TP/SL 체크
            tp_price = entry_price + TAG_TPSL[strategy_tag]['tp'] if entry_type == 'Long' else entry_price - TAG_TPSL[strategy_tag]['tp']
            sl_price = entry_price - TAG_TPSL[strategy_tag]['sl'] if entry_type == 'Long' else entry_price + TAG_TPSL[strategy_tag]['sl']
            
            # TP/SL 동시 도달 체크
            if current_high >= tp_price and current_low <= sl_price:
                if is_bullish:
                    exit_price = tp_price
                    results['wins'] += 1
                else:
                    exit_price = sl_price
                    results['losses'] += 1
            elif current_high >= tp_price:
                exit_price = tp_price
                results['wins'] += 1
            elif current_low <= sl_price:
                exit_price = sl_price
                results['losses'] += 1
            else:
                continue
                
            # 수익 계산 (수수료 포함)
            position_size = results['capital'] * 0.1  # 10% 사용
            entry_fee = position_size * 0.00044
            exit_fee = position_size * 0.00044
            
            if entry_type == 'Long':
                profit = position_size * ((exit_price - entry_price) / entry_price) - entry_fee - exit_fee
            else:
                profit = position_size * ((entry_price - exit_price) / entry_price) - entry_fee - exit_fee
                
            results['capital'] += profit
            results['trades'].append({
                'entry_time': entry_time,
                'exit_time': df.index[i],
                'type': entry_type,
                'entry': entry_price,
                'exit': exit_price,
                'profit': profit
            })
            
            in_position = False
            
        else:
            prev_signal = df[signal_column].iloc[i-1]
            if prev_signal in ['Long', 'Short']:
                entry_price = df['open'].iloc[i]
                entry_type = prev_signal
                entry_time = df.index[i]
                in_position = True
    
    # 결과 계산
    total_days = (df.index[-1] - df.index[0]).days
    trades_per_day = len(results['trades']) / total_days if total_days > 0 else 0
    win_rate = (results['wins'] / (results['wins'] + results['losses'])) * 100 if (results['wins'] + results['losses']) > 0 else 0
    
    return {
        'trades_per_day': trades_per_day,
        'win_rate': win_rate,
        'total_trades': len(results['trades']),
        'wins': results['wins'],
        'losses': results['losses'],
        'final_capital': results['capital'],
        'profit_percentage': ((results['capital'] - initial_capital) / initial_capital) * 100,
        'detailed_trades': results['trades']
    }

import itertools
import pandas as pd
from datetime import datetime

def create_parameter_grid(parameter_ranges,STRATEGY_ENABLE):
    """
    파라미터 범위로부터 그리드 생성
    예시 parameter_ranges:
    {
        'LINEAR_REG': {
            'LENGTH': range(80, 121, 10),
            'RSI_LENGTH': range(10, 21, 2),
            'MIN_SLOPE_VALUE': range(4, 9, 1)
        }
    }
    """
    active_strategy = next((k for k, v in STRATEGY_ENABLE.items() if v), None)
    if not active_strategy:
        return []
        
    params = parameter_ranges[active_strategy]
    keys = list(params.keys())
    values = list(params.values())
    
    combinations = list(itertools.product(*values))
    return [dict(zip(keys, combo)) for combo in combinations]

def run_grid_search(df, parameter_ranges, process_chart_data, cal_position, STG_CONFIG, STRATEGY_ENABLE, 
                   TAG_TPSL, SIGNAL_COLUMNS, save_path='backtest_results'):
    """
    Args:
        df_original: 원본 데이터프레임 (계산 전)
        parameter_ranges: 테스트할 파라미터 범위
        process_chart_data: 지표 계산 함수
        STG_CONFIG: 전략 설정
        STRATEGY_ENABLE: 전략 활성화 설정
        TAG_TPSL: TP/SL 설정값
        SIGNAL_COLUMNS: 시그널 컬럼명 매핑
        save_path: 결과 저장 경로
    """
    results = []
    active_strategy = next((k for k, v in STRATEGY_ENABLE.items() if v), None)
    

    import os 
    # 결과 저장 디렉토리 생성
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    # 파일명에 사용할 타임스탬프
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 모든 파라미터 조합에 대해 테스트 실행
    parameter_grid = create_parameter_grid(
    parameter_ranges=parameter_ranges,
    STRATEGY_ENABLE=STRATEGY_ENABLE
)
    total_combinations = len(parameter_grid)
    
    for i, params in enumerate(parameter_grid, 1):
        print(f"\n테스트 진행중: {i}/{total_combinations}")
        print(f"파라미터: {params}")
        
        # STG_CONFIG 업데이트
        test_config = STG_CONFIG.copy()
        test_config[active_strategy].update(params)
        
        # 데이터 재계산
        df_calculated = process_chart_data(df, test_config, STRATEGY_ENABLE)
        _, df_with_signals, _ = cal_position(df=df_calculated, STG_CONFIG=test_config, STRATEGY_ENABLE=STRATEGY_ENABLE)
        
        # 백테스트 실행
        backtest_results = run_backtest(
            df=df_with_signals,
            TAG_TPSL=TAG_TPSL,
            STRATEGY_ENABLE=STRATEGY_ENABLE,
            SIGNAL_COLUMNS=SIGNAL_COLUMNS
        )
        
        # 결과 저장
        result = {
            'parameters': params,
            'trades_per_day': backtest_results['trades_per_day'],
            'win_rate': backtest_results['win_rate'],
            'total_trades': backtest_results['total_trades'],
            'wins': backtest_results['wins'],
            'losses': backtest_results['losses'],
            'final_capital': backtest_results['final_capital'],
            'profit_percentage': backtest_results['profit_percentage']
        }
        results.append(result)
        
    # 결과를 DataFrame으로 변환
    results_df = pd.DataFrame(results)
    
    # 파라미터 컬럼 분리
    param_df = pd.DataFrame(list(results_df['parameters']))
    results_df = pd.concat([param_df, results_df.drop('parameters', axis=1)], axis=1)
    
    # 결과 저장
    filename = f"{active_strategy}_results_{timestamp}.csv"
    filepath = os.path.join(save_path, filename)
    results_df.to_csv(filepath, index=False)
    
    # 상위 결과 출력
    print("\n=== 상위 5개 결과 ===")
    top_results = results_df.nlargest(5, 'profit_percentage')
    print(top_results)
    
    return filepath

