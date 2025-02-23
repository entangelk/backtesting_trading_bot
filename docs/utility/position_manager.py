class Position:
    def __init__(self):
        self.current_position = None
        self.entry_price = None
        self.tp_price = None
        self.sl_price = None
        self.entry_time = None
        self.tag = None

def process_position(df, current_pos, new_position, new_tag, TAG_TPSL):
    """
    포지션 처리 및 TPSL 계산 함수
    """
    results = []
    
    for i in range(1, len(df)):  # 1부터 시작하여 이전 봉의 시그널을 현재 봉의 진입에 사용
        current_row = df.iloc[i]
        prev_row = df.iloc[i-1]
        
        # TPSL 체크 (현재 포지션이 있는 경우)
        if current_pos.current_position:
            hit_tp = False
            hit_sl = False
            
            if current_pos.current_position == 'Long':
                # TP/SL 동시 도달 시 봉의 방향으로 판단
                if current_row['high'] >= current_pos.tp_price and current_row['low'] <= current_pos.sl_price:
                    if current_row['close'] > current_row['open']:
                        hit_tp = True
                    else:
                        hit_sl = True
                else:
                    hit_tp = current_row['high'] >= current_pos.tp_price
                    hit_sl = current_row['low'] <= current_pos.sl_price
                
            else:  # Short position
                if current_row['high'] >= current_pos.sl_price and current_row['low'] <= current_pos.tp_price:
                    if current_row['close'] > current_row['open']:
                        hit_sl = True
                    else:
                        hit_tp = True
                else:
                    hit_tp = current_row['low'] <= current_pos.tp_price
                    hit_sl = current_row['high'] >= current_pos.sl_price
            
            # TPSL 히트 처리
            if hit_tp or hit_sl:
                result = {
                    'exit_time': current_row.name,
                    'entry_time': current_pos.entry_time,
                    'position': current_pos.current_position,
                    'entry_price': current_pos.entry_price,
                    'exit_price': current_pos.tp_price if hit_tp else current_pos.sl_price,
                    'result': 'TP' if hit_tp else 'SL',
                    'tag': current_pos.tag
                }
                results.append(result)
                current_pos.current_position = None
        
        # 새로운 포지션 진입 검토
        if prev_row.name == new_position[0]:  # 시그널이 발생한 봉
            # 반대 포지션이거나 포지션이 없을 때 진입
            if (current_pos.current_position is None or 
                current_pos.current_position != new_position[1]):
                
                current_pos.current_position = new_position[1]
                current_pos.entry_price = current_row['open']
                current_pos.entry_time = current_row.name
                current_pos.tag = new_tag
                
                # TPSL 설정
                tp_value = TAG_TPSL[new_tag]['tp']
                sl_value = TAG_TPSL[new_tag]['sl']
                
                if new_position[1] == 'Long':
                    current_pos.tp_price = current_pos.entry_price + tp_value
                    current_pos.sl_price = current_pos.entry_price - sl_value
                else:  # Short
                    current_pos.tp_price = current_pos.entry_price - tp_value
                    current_pos.sl_price = current_pos.entry_price + sl_value
    
    return current_pos, results