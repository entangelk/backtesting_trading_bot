def supertrend(df, STG_CONFIG):
    # 데이터프레임 복사본 생성
    df = df.copy()
    
    # 소스 hl2 유지
    src = (df['high'] + df['low']) / 2
    atr = df['atr_stg3']  
    multiplier = STG_CONFIG['SUPERTREND']['ATR_MULTIPLIER']
    
    # Basic Bands 계산
    df.loc[:, 'basic_upper'] = src - (multiplier * atr)
    df.loc[:, 'basic_lower'] = src + (multiplier * atr)
    
    # Final Bands 계산을 위한 초기화
    df.loc[:, 'up'] = df['basic_upper']
    df.loc[:, 'down'] = df['basic_lower']
    
    # Final Bands 계산
    for i in range(1, len(df)):
        if df['close'].iloc[i-1] > df['up'].iloc[i-1]:
            df.loc[df.index[i], 'up'] = max(df['basic_upper'].iloc[i], df['up'].iloc[i-1])
        else:
            df.loc[df.index[i], 'up'] = df['basic_upper'].iloc[i]
            
        if df['close'].iloc[i-1] < df['down'].iloc[i-1]:
            df.loc[df.index[i], 'down'] = min(df['basic_lower'].iloc[i], df['down'].iloc[i-1])
        else:
            df.loc[df.index[i], 'down'] = df['basic_lower'].iloc[i]
    
    # Trend 초기화
    df.loc[:, 'st_trend'] = 1

    # 첫 번째 트렌드 설정
    if df['close'].iloc[0] > df['down'].iloc[0]:
        df.loc[df.index[0], 'st_trend'] = 1
    else:
        df.loc[df.index[0], 'st_trend'] = -1

    # Trend 계산 수정
    for i in range(1, len(df)):
        prev_trend = df['st_trend'].iloc[i-1]
        
        if prev_trend == -1 and df['close'].iloc[i] > df['down'].iloc[i-1]:
            curr_trend = 1
        elif prev_trend == 1 and df['close'].iloc[i] < df['up'].iloc[i-1]:
            curr_trend = -1
        else:
            curr_trend = prev_trend
            
        df.loc[df.index[i], 'st_trend'] = curr_trend
    
    # Position 시그널 계산
    df.loc[:, 'st_position'] = None
    trend_change = df['st_trend'] != df['st_trend'].shift(1)
    
    df.loc[(trend_change) & (df['st_trend'] == 1), 'st_position'] = 'Long'
    df.loc[(trend_change) & (df['st_trend'] == -1), 'st_position'] = 'Short'
    
    return df