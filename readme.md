| 지표 | 파라미터 | 범위 | 효과 체크 | 실제 효과 |
|------|----------|------|------------|------------|
| **MACD_SIZE** |
|| MACD_FAST_LENGTH | 12 | □ 단기 이동평균 기간으로, 짧을수록 더 민감하게 반응 | x |
|| MACD_SLOW_LENGTH | 17 | □ 장기 이동평균 기간으로, 길수록 더 안정적인 신호 | x |
|| MACD_SIGNAL_LENGTH | 5 ~ 100 (5단위로)| □ MACD 신호선의 평활화 정도를 결정 | O |
|| SIZE_RATIO_THRESHOLD | 0.7 ~ 1.8 (0.1단위) | □ 거래량 비율의 임계값으로 필터링 강도 조절 | □ |
|| DI_LENGTH | 10 ~ 20 (1단위)| □ 방향성 지표의 기간 설정 | □ |
|| DI_SLOPE_LENGTH | 7-15 (1단위) | □ 방향성 지표의 기울기 계산 기간 | □ |
|| MIN_SLOPE_THRESHOLD | 12-18 (1단위) | □ 최소 기울기 요구치로 트렌드 강도 필터링 | □ |
|| REQUIRED_CONSECUTIVE_CANDLES | 1~2(1단위) | □ 연속 캔들 요구 수로 시그널 신뢰도 향상 | □ |
| **MACD_DIVE** |
|| FAST_LENGTH | 10~20 (1) | □ 빠른 반응을 위한 단기 이동평균 기간 | □ |
|| SLOW_LENGTH | 21-31 (1) | □ 트렌드 파악을 위한 장기 이동평균 기간 | □ |
|| SIGNAL_LENGTH | 10 ~ 24 (2) | □ 신호선의 반응 속도 조절 | □ |
|| HISTOGRAM_UPPER_LIMIT | 50-100 (10) | □ 히스토그램 상단 제한으로 과매수 필터링 | □ |
|| HISTOGRAM_LOWER_LIMIT | -50 ~ -100 (10) | □ 히스토그램 하단 제한으로 과매도 필터링 | □ |
|| LOOKBACK_PERIOD | 2 | □ 이전 기간 참조 수로 신호 확인 강화 | X |
|| PRICE_MOVEMENT_THRESHOLD | 0.01-0.05 (0.01)| □ 가격 변동 임계값으로 노이즈 필터링 | □ |
| **SUPERTREND** |
|| ATR_PERIOD | 30 | □ 평균 실제 범위 계산 기간으로 변동성 측정 | X |
|| ATR_MULTIPLIER | 4-8 | □ ATR 승수로 밴드 폭 조절 | □ |
|| ADX_LENGTH | 10-18 | □ 평균 방향성 지수 기간으로 트렌드 강도 측정 | □ |
|| DI_DIFFERENCE_FILTER | 6-10 | □ DI 차이 필터로 트렌드 방향 신뢰도 향상 | □ |
|| DI_DIFFERENCE_LOOKBACK_PERIOD | 4-8 | □ DI 차이 확인 기간으로 추세 지속성 판단 | □ |
| **LINEAR_REG** |
|| LENGTH | 50~150 (25) | □ 선형 회귀 계산 기간으로 트렌드 라인 정확도 조절 | □ |
|| RSI_LENGTH | 14 | □ RSI 계산 기간으로 과매수/과매도 판단 | x |
|| RSI_LOWER_BOUND | 20~35 (5) | □ RSI 하단 경계로 매수 시점 필터링 | □ |
|| RSI_UPPER_BOUND | 65 ~ 80(5) | □ RSI 상단 경계로 매도 시점 필터링 | □ |
|| MIN_BOUNCE_BARS | 2~6 (1) | □ 최소 반등 봉 수로 반등 신뢰도 확보 | □ |
|| UPPER_MULTIPLIER | 3 | □ 상단 밴드 승수로 매도 구간 조절 | x|
|| LOWER_MULTIPLIER | 3 | □ 하단 밴드 승수로 매수 구간 조절 | x |
|| MIN_SLOPE_VALUE | 4-10 | □ 최소 기울기 값으로 트렌드 강도 필터링 | □ |
|| MIN_TREND_DURATION | 30-80(5) | □ 최소 트렌드 지속 기간으로 신뢰도 향상 | □ |


현재 평균 일일 거래 수
MACD_DIVE = 1.8 ~ 1.9 회/일
SUPERTREND = 1.27회/일
MACD_SIZE = 1.7회 / 일


# 트레이딩 지표 테이블

SUPERTREND

| 컬럼 | 값 |
|------|------|
| ATR_PERIOD | 30 |
| ATR_MULTIPLIER | 6 |
| ADX_LENGTH | 11 |
| DI_DIFFERENCE_FILTER | 6 |
| DI_DIFFERENCE_LOOKBACK_PERIOD | 4 |
| trades_per_day | 1.68 |
| win_rate | 57.81 |
| total_trades | 320 |
| wins | 185 |
| losses | 135 |
| final_capital | 10228525.43 |
| profit_percentage | 2.28 |

MACD_DIVE

| 파라미터 | 값 |
|---------|---|
| FAST_LENGTH |10 |
| SLOW_LENGTH | 26|
| SIGNAL_LENGTH | 12|
| HISTOGRAM_UPPER_LIMIT | 50|
| HISTOGRAM_LOWER_LIMIT | -60|
| LOOKBACK_PERIOD |2 |
| PRICE_MOVEMENT_THRESHOLD |0.01 |
| trades_per_day |1.91 |
| win_rate | 61.6|
| total_trades | 362|
| wins | 223|
| losses | 139|
| final_capital |1051763.87 |
| profit_percentage | 5.18|

MACD_SIZE

| 파라미터 | 값 |
|:--|:--|
| MACD_FAST_LENGTH |12 |
| MACD_SLOW_LENGTH | 17|
| MACD_SIGNAL_LENGTH | 10|
| SIZE_RATIO_THRESHOLD |1.1 |
| DI_LENGTH | 18|
| DI_SLOPE_LENGTH | 11|
| MIN_SLOPE_THRESHOLD | 14|
| REQUIRED_CONSECUTIVE_CANDLES |2 |
| trades_per_day |1.89 |
| win_rate | 58.22|
| total_trades |359 |
| wins | 209|
| losses | 150|
| final_capital |1030688.7 |
| profit_percentage | 3.07|