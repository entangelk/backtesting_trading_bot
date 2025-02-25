import pandas as pd
import ta
import numpy as np

def process_chart_data(df, STG_CONFIG, STRATEGY_ENABLE):
    # 데이터프레임 복사본 생성
    df = df.copy()
    pass
# 함수 및 공통 계산 부분
        # SMA 초기값을 사용하는 EMA 함수
    def ema_with_sma_init(series, period):
        sma = series.rolling(window=period, min_periods=period).mean()
        ema = series.ewm(span=period, adjust=False).mean()
        ema[:period] = sma[:period]  # 초기값을 SMA로 설정
        return ema
    
    def ema_with_sma_init(series, period):
        # NaN 체크 및 제거
        if series.isnull().any():
            print(f"Warning: Input series contains {series.isnull().sum()} NaN values")
        
        # EMA multiplier
        multiplier = 2 / (period + 1)
        
        # SMA 계산 (min_periods를 1로 설정하여 초기값 계산 개선)
        sma = series.rolling(window=period, min_periods=1).mean()
        
        # EMA 계산
        ema = pd.Series(0.0, index=series.index)
        
        # 첫 번째 유효한 값을 찾아 초기값으로 사용
        first_valid_idx = series.first_valid_index()
        if first_valid_idx:
            ema.loc[first_valid_idx] = series.loc[first_valid_idx]
        
        # EMA 계산 (이전 값이 있는 경우에만 계산)
        for i in range(1, len(series)):
            prev_ema = ema.iloc[i-1]
            curr_price = series.iloc[i]
            
            if pd.notna(curr_price) and pd.notna(prev_ema):
                ema.iloc[i] = (curr_price * multiplier) + (prev_ema * (1 - multiplier))
            else:
                ema.iloc[i] = curr_price if pd.notna(curr_price) else prev_ema
        
        return ema
    

    # RMA 함수 정의
    def rma(series, period):
        alpha = 1/period
        return series.ewm(alpha=alpha, adjust=False).mean()

    def wilder_smoothing(series, period):
        if not isinstance(series, pd.Series):
            series = pd.Series(series)
        
        # 모든 값을 미리 float로 변환
        series = series.astype(float)
        
        first_valid_idx = series.first_valid_index()
        if first_valid_idx is None:
            return pd.Series(index=series.index)
        
        first_valid_loc = series.index.get_loc(first_valid_idx)
        if not isinstance(first_valid_loc, (int, np.integer)):
            first_valid_loc = first_valid_loc.start if isinstance(first_valid_loc, slice) else 0
        
        smoothed = np.full(len(series), np.nan)
        smoothed[first_valid_loc] = series.iloc[first_valid_loc]
        
        # 계산 과정
        for i in range(first_valid_loc + 1, len(series)):
            current_value = series.iloc[i]
            prev_value = smoothed[i-1]
            
            if np.isnan(current_value):
                smoothed[i] = prev_value
            elif np.isnan(prev_value):
                smoothed[i] = current_value
            else:
                smoothed[i] = (prev_value * (period - 1) + current_value) / period
        
        return pd.Series(smoothed, index=series.index)
    
    # ATR 계산
    df['TR'] = pd.Series(np.maximum(df['high'] - df['low'], 
                        np.maximum(abs(df['high'] - df['close'].shift(1)), 
                                    abs(df['low'] - df['close'].shift(1)))), dtype=float)

    df['TR'] = df['TR'].fillna(0)


    # Directional Movement (DM+ 및 DM-) 계산
    df['DM+'] = np.where((df['high'] - df['high'].shift(1)) > (df['low'].shift(1) - df['low']),
                        np.maximum(df['high'] - df['high'].shift(1), 0), 0)
    df['DM-'] = np.where((df['low'].shift(1) - df['low']) > (df['high'] - df['high'].shift(1)),
                        np.maximum(df['low'].shift(1) - df['low'], 0), 0)

    # 동시 활성화 방지
    df.loc[df['DM+'] > 0, 'DM-'] = 0
    df.loc[df['DM-'] > 0, 'DM+'] = 0
    df[['DM+', 'DM-']] = df[['DM+', 'DM-']].fillna(0)

    pass


    ''' 여기서부터 계산 부분 '''

    # STG_No1 - MACD_SIZE 전략
    if STRATEGY_ENABLE['MACD_SIZE']:
        df['EMA_fast_stg1'] = ema_with_sma_init(df['close'], STG_CONFIG['MACD_SIZE']['MACD_FAST_LENGTH'])
        df['EMA_slow_stg1'] = ema_with_sma_init(df['close'], STG_CONFIG['MACD_SIZE']['MACD_SLOW_LENGTH'])
        df['macd_stg1'] = df['EMA_fast_stg1'] - df['EMA_slow_stg1']
        df['macd_signal_stg1'] = ema_with_sma_init(df['macd_stg1'], STG_CONFIG['MACD_SIZE']['MACD_SIGNAL_LENGTH'])
        df['hist_stg1'] = df['macd_stg1'] - df['macd_signal_stg1']

            ## MACD Size 계산부분
        df['hist_size'] = abs(df['hist_stg1'])
        df['candle_size'] = abs(df['close'] - df['open'])
        df['candle_size_ma'] = df['candle_size'].rolling(window=STG_CONFIG['MACD_SIZE']['MACD_SLOW_LENGTH']).mean()
        df['normalized_candle_size'] = df['candle_size'] / df['candle_size_ma']
        df['hist_size_ma'] = df['hist_size'].rolling(window=STG_CONFIG['MACD_SIZE']['MACD_SLOW_LENGTH']).mean()
        df['normalized_hist_size'] = df['hist_size'] / df['hist_size_ma']


        df['Smoothed_TR_stg1'] = wilder_smoothing(df['TR'], STG_CONFIG['MACD_SIZE']['DI_LENGTH'])
        df['Smoothed_DM+_stg1'] = wilder_smoothing(df['DM+'], STG_CONFIG['MACD_SIZE']['DI_LENGTH'])
        df['Smoothed_DM-_stg1'] = wilder_smoothing(df['DM-'], STG_CONFIG['MACD_SIZE']['DI_LENGTH'])
        
        df['DI+_stg1'] = 100 * (df['Smoothed_DM+_stg1'] / df['Smoothed_TR_stg1'])
        df['DI-_stg1'] = 100 * (df['Smoothed_DM-_stg1'] / df['Smoothed_TR_stg1'])
        
            # DI Slopes
        df['DIPlus_stg1'] = df['DI+_stg1'] - df['DI+_stg1'].shift(STG_CONFIG['MACD_SIZE']['DI_SLOPE_LENGTH'])
        df['DIMinus_stg1'] = df['DI-_stg1'] - df['DI-_stg1'].shift(STG_CONFIG['MACD_SIZE']['DI_SLOPE_LENGTH'])


    ''' STG_No1 MACD_SIZE 계산 끝'''


    # STG_No2 - MACD_DIVE 전략 (MACD_DIVERGENCE)
    if STRATEGY_ENABLE['MACD_DIVE']:
        df['EMA_fast_stg2'] = ema_with_sma_init(df['close'], STG_CONFIG['MACD_DIVE']['FAST_LENGTH'])
        df['EMA_slow_stg2'] = ema_with_sma_init(df['close'], STG_CONFIG['MACD_DIVE']['SLOW_LENGTH'])
        df['macd_stg2'] = df['EMA_fast_stg2'] - df['EMA_slow_stg2']
        df['macd_signal_stg2'] = ema_with_sma_init(df['macd_stg2'], STG_CONFIG['MACD_DIVE']['SIGNAL_LENGTH'])
        df['hist_stg2'] = df['macd_stg2'] - df['macd_signal_stg2']
        
            # === MACD dive 방향 ===
        df['hist_direction_dive'] = df['hist_stg2'] - df['hist_stg2'].shift(1)

    ''' STG_No2 MACD_DIVE 계산 끝'''



        # STG_No3 - SUPERTREND 전략
    if STRATEGY_ENABLE['SUPERTREND']:
        df['atr_stg3'] = rma(df['TR'], STG_CONFIG['SUPERTREND']['ATR_PERIOD'])
        df['Smoothed_TR_stg3'] = wilder_smoothing(df['TR'], STG_CONFIG['SUPERTREND']['ADX_LENGTH'])
        df['Smoothed_DM+_stg3'] = wilder_smoothing(df['DM+'], STG_CONFIG['SUPERTREND']['ADX_LENGTH'])
        df['Smoothed_DM-_stg3'] = wilder_smoothing(df['DM-'], STG_CONFIG['SUPERTREND']['ADX_LENGTH'])
        df['DI+_stg3'] = 100 * (df['Smoothed_DM+_stg3'] / df['Smoothed_TR_stg3'])
        df['DI-_stg3'] = 100 * (df['Smoothed_DM-_stg3'] / df['Smoothed_TR_stg3'])

    ''' STG_No3 SUPERTREND 계산 끝'''


    # STG_No4 - LINEAR_REG 전략
    if STRATEGY_ENABLE['LINEAR_REG']:

        length = STG_CONFIG['LINEAR_REG']['LENGTH']
        
        # 초기값 설정
        df['slope'] = np.nan
        df['intercept'] = np.nan
        df['average'] = np.nan
        pass
        # 선형 회귀 계산
        for i in range(length-1, len(df)):
            sum_x = 0.0
            sum_y = 0.0
            sum_xy = 0.0
            sum_x2 = 0.0
            
            # 파인스크립트와 동일한 방식으로 계산
            for j in range(length):
                price = df['close'].iloc[i-j]  # 최신 데이터부터 역순으로
                x = length - 1 - j  # x값도 역순으로
                sum_x += x
                sum_y += price
                sum_xy += x * price
                sum_x2 += x * x
            
            n = float(length)
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            average = sum_y / n
            
            df.loc[df.index[i], 'slope'] = slope
            df.loc[df.index[i], 'intercept'] = intercept
            df.loc[df.index[i], 'average'] = average
            print(f"1번째 루프 {i}째 계산중")
        # 중심선 계산
        df['middle_line'] = np.nan
        for i in range(len(df)):
            if not np.isnan(df['intercept'].iloc[i]):
                # 현재 캔들의 중간값 계산
                candle_middle = (df['close'].iloc[i] + df['open'].iloc[i]) / 2
                # 파인스크립트와 동일한 방식으로 계산
                df.loc[df.index[i], 'middle_line'] = df['intercept'].iloc[i] + df['slope'].iloc[i] * candle_middle
            print(f"2번째 루프 {i}째 계산중")
        
        # 표준편차 계산
        df['std_dev'] = np.nan

        for i in range(length-1, len(df)):
            sum_diff_sq = 0.0
            current_slope = df['slope'].iloc[i]
            current_intercept = df['intercept'].iloc[i]
            
            for j in range(length):
                expected_price = current_intercept + current_slope * float(j)
                idx = i - j  # 명시적으로 인덱스 계산
                # 최신 데이터부터 과거 순서로 계산
                diff = df['close'].iat[idx] - expected_price  # iloc 대신 iat 사용
                sum_diff_sq += diff * diff
                
            std_dev = np.sqrt(sum_diff_sq / length)
            df.loc[df.index[i], 'std_dev'] = std_dev
            print(f"3번째 루프 {i}째 계산중")
        
        # 채널 밴드 계산
        up_multiplier = STG_CONFIG['LINEAR_REG']['UPPER_MULTIPLIER']
        lw_multiplier = STG_CONFIG['LINEAR_REG']['LOWER_MULTIPLIER']
        df['upper_band'] = df['middle_line'] + up_multiplier * df['std_dev']
        df['lower_band'] = df['middle_line'] - lw_multiplier * df['std_dev']
        
        # 추세 지속성 계산
        df['trend_duration'] = 0
        current_duration = 0
        
        for i in range(len(df)):
            is_uptrend = df['slope'].iloc[i] >= 0
            is_downtrend = df['slope'].iloc[i] < 0
            
            if i == 0:
                current_duration = 1 if is_uptrend else -1
            else:
                prev_duration = df['trend_duration'].iloc[i-1]
                if is_uptrend:
                    current_duration = (prev_duration + 1) if prev_duration >= 0 else 1
                elif is_downtrend:
                    current_duration = (prev_duration - 1) if prev_duration <= 0 else -1
                else:
                    current_duration = 0
                    
            df.loc[df.index[i], 'trend_duration'] = current_duration
            print(f"4번째 루프 {i}째 계산중")


        rsi_length = STG_CONFIG['LINEAR_REG']['RSI_LENGTH']
        df['rsi_stg4'] = ta.momentum.rsi(df['close'], window=rsi_length).fillna(50)

    ''' STG_No4 LINEAR_REG 계산 끝 '''

    # STG_No5 - MACD_DI_SLOPE 전략
    if STRATEGY_ENABLE['MACD_DI_RSI']:
        df['EMA_fast_stg5'] = ema_with_sma_init(df['close'], STG_CONFIG['MACD_DI_SLOPE']['FAST_LENGTH'])
        df['EMA_slow_stg5'] = ema_with_sma_init(df['close'], STG_CONFIG['MACD_DI_SLOPE']['SLOW_LENGTH'])
        df['macd_stg5'] = df['EMA_fast_stg5'] - df['EMA_slow_stg5']

        # NaN이 아닌 값으로 시그널 라인 계산
        # df['macd_signal_stg5'] = ema_with_sma_init(df['macd_stg5'].fillna(method='ffill'), STG_CONFIG['MACD_DI_SLOPE']['SIGNAL_LENGTH'])
        df['macd_signal_stg5'] = ema_with_sma_init(df['macd_stg5'].ffill(), STG_CONFIG['MACD_DI_SLOPE']['SIGNAL_LENGTH'])
        df['hist_stg5'] = df['macd_stg5'] - df['macd_signal_stg5']
        
        # === MACD dive 방향 ===
        df['hist_direction_stg5'] = df['hist_stg5'] - df['hist_stg5'].shift(1)


        df['Smoothed_TR_stg5'] = wilder_smoothing(df['TR'], STG_CONFIG['MACD_DI_SLOPE']['DI_LENGTH'])
        df['Smoothed_DM+_stg5'] = wilder_smoothing(df['DM+'], STG_CONFIG['MACD_DI_SLOPE']['DI_LENGTH'])
        df['Smoothed_DM-_stg5'] = wilder_smoothing(df['DM-'], STG_CONFIG['MACD_DI_SLOPE']['DI_LENGTH'])

        # DI+ 및 DI- 계산
        df['DI+_stg5'] = 100 * (df['Smoothed_DM+_stg5'] / df['Smoothed_TR_stg5'])
        df['DI-_stg5'] = 100 * (df['Smoothed_DM-_stg5'] / df['Smoothed_TR_stg5'])

        # === 두 번째 전략의 DI Slope (slope_len=3) ===
        df['DIPlus_stg5'] = df['DI+_stg5'] - df['DI+_stg5'].shift(STG_CONFIG['MACD_DI_SLOPE']['SLOPE_LENGTH'])
        df['DIMinus_stg5'] = df['DI-_stg5'] - df['DI-_stg5'].shift(STG_CONFIG['MACD_DI_SLOPE']['SLOPE_LENGTH'])
        df['slope_diff_stg5'] = df['DIPlus_stg5'] - df['DIMinus_stg5']
        
        # RSI (Relative Strength Index)
        rsi_length = STG_CONFIG['MACD_DI_SLOPE']['RSI_LENGTH']
        df['rsi_stg5'] = ta.momentum.rsi(df['close'], window=rsi_length).fillna(50)

    ''' STG_No5 MACD_DI_SLPOE 계산 끝'''




    # STG_No6 - VOLUME_TREND 전략
    if STRATEGY_ENABLE['VOLUME_NORM']:
        vol_length = STG_CONFIG['VOLUME_TREND']['VOLUME_MA_LENGTH']
        trend_length = STG_CONFIG['VOLUME_TREND']['TREND_PERIOD']
        norm_period = STG_CONFIG['VOLUME_TREND']['NORM_PERIOD']
        
        
        # 볼륨 이동평균
        df['vol_ma'] = df['volume'].rolling(vol_length).mean()
        
        # 상승/하락 볼륨 구분 및 이동평균 계산
        df['up_vol'] = np.where(df['close'] >= df['open'], df['volume'], 0)
        df['down_vol'] = np.where(df['close'] < df['open'], df['volume'], 0)

        # 상승/하락 볼륨 이동평균
        df['up_vol_ma'] = df['up_vol'].rolling(vol_length).mean()
        df['down_vol_ma'] = df['down_vol'].rolling(vol_length).mean()
        
        # 볼륨 강도 계산
        df['vol_strength'] = ((df['up_vol_ma'] - df['down_vol_ma']) / df['vol_ma']) * 100
        
        # 볼륨 강도의 추세
        df['vol_trend'] = df['vol_strength'].ewm(span=trend_length, adjust=False).mean()
        
        # 정규화를 위한 최대/최소
        df['vt_highest'] = df['vol_trend'].rolling(norm_period).max()
        df['vt_lowest'] = df['vol_trend'].rolling(norm_period).min()
        
        # 트렌드 정규화
        df['norm_trend'] = ((df['vol_trend'] - df['vt_lowest']) / 
                        (df['vt_highest'] - df['vt_lowest'])) * 2 - 1
        
        # 시그널 라인
        df['signal_line'] = df['norm_trend'].ewm(span=trend_length, adjust=False).mean()
        
        # 차이값 계산
        df['trend_diff'] = abs(df['norm_trend'] - df['signal_line'])




    # 불필요한 중간 계산 컬럼 제거
    try:
        columns_to_drop = ['TR', 'DM+', 'DM-']
        if STRATEGY_ENABLE['MACD_SIZE']:
            columns_to_drop.extend(['Smoothed_TR_stg1', 'Smoothed_DM+_stg1', 'Smoothed_DM-_stg1'])
        if STRATEGY_ENABLE['SUPERTREND']:
            columns_to_drop.extend(['Smoothed_TR_stg3', 'Smoothed_DM+_stg3', 'Smoothed_DM-_stg3'])
        df.drop(columns=columns_to_drop, inplace=True)
    except Exception as e:
        print(f"컬럼 지우기 오류 발생: {e}")
    
    return df