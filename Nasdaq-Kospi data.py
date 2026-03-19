import pandas as pd
import numpy as np
import requests
import urllib3
from datetime import datetime

# 1. SSL 경고 무시 설정 (콘솔을 깨끗하게 유지)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_market_data_json(ticker):
    # 야후 파이낸스 실시간 차트 API (CSV보다 훨씬 잘 뚫립니다)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5y"
    
    # 실제 브라우저처럼 보이게 만드는 헤더 (매우 중요)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # SSL 검증 무시 (verify=False)
    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code == 200:
        json_data = response.json()
        result = json_data['chart']['result'][0]
        timestamps = result['timestamp']
        adj_close = result['indicators']['adjclose'][0]['adjclose']
        
        # 데이터프레임 생성 및 날짜 변환
        df = pd.DataFrame({
            'Date': pd.to_datetime(timestamps, unit='s'),
            'Adj Close': adj_close
        })
        df.set_index('Date', inplace=True)
        return df['Adj Close']
    else:
        print(f"❌ 데이터 수집 실패: {ticker} (Status Code: {response.status_code})")
        return None

# 2. 데이터 수집 시작
nasdaq = get_market_data_json("^IXIC")
kospi = get_market_data_json("^KS11")

if nasdaq is not None and kospi is not None:
    # --- [데이터 정규화 및 중복 제거] ---
    # 1. 시간대 제거 및 날짜 표준화
    nasdaq.index = nasdaq.index.tz_localize(None).normalize()
    kospi.index = kospi.index.tz_localize(None).normalize()
    
    # 2. 중복된 날짜 제거 (핵심!)
    # keep='first'는 중복된 날짜 중 첫 번째 데이터만 남기겠다는 뜻입니다.
    nasdaq = nasdaq[~nasdaq.index.duplicated(keep='first')]
    kospi = kospi[~kospi.index.duplicated(keep='first')]
    
    # 3. 컬럼명 지정
    nasdaq.name = 'NASDAQ'
    kospi.name = 'KOSPI'
    
    # 4. 이제 안전하게 병합 (axis=1은 열 방향 합치기)
    returns_df = pd.concat([nasdaq, kospi], axis=1).dropna()
    print(f"DEBUG: 병합 후 남은 일수: {len(returns_df)}")
    # ------------------------------------

    if len(returns_df) > 100:
        # 이후 수익률 및 Z-Score 계산 로직은 이전과 동일합니다.
        returns_df = returns_df.pct_change().dropna()
        # ...
    print(f"DEBUG: 병합 후 남은 일수: {len(returns_df)}")
    # -----------------------

    if len(returns_df) > 100: # 최소 100일은 있어야 이동평균 계산 가능
        # 3. 수익률 및 Z-Score 계산 (기존과 동일)
        returns_df = returns_df.pct_change().dropna()

        def calculate_zscore(series, window=100):
            return (series - series.rolling(window).mean()) / series.rolling(window).std()

        returns_df['Z_NASDAQ'] = calculate_zscore(returns_df['NASDAQ'])
        returns_df['Z_KOSPI'] = calculate_zscore(returns_df['KOSPI'])

    # 4. 시차 조정 (어제 밤 나스닥 -> 오늘 국장)
    returns_df['Z_NASDAQ_LAG'] = returns_df['Z_NASDAQ'].shift(1)
    returns_df = returns_df.dropna()

    # 5. 확률 계산
    threshold = 0.5  # 분석 기준값
    nasdaq_surge = returns_df[returns_df['Z_NASDAQ_LAG'] > threshold]
    both_surge = nasdaq_surge[nasdaq_surge['Z_KOSPI'] > threshold]

    # 6. 결과 출력
    print("\n" + "="*45)
    print(f"📊 나스닥-코스피 동조화 분석 (최근 5년 데이터)")
    print(f"🗓️ 총 분석 대상 일수: {len(returns_df)}일")
    
    if len(nasdaq_surge) > 0:
        prob = (len(both_surge) / len(nasdaq_surge)) * 100
        # f-string을 활용해 threshold 값을 자동으로 반영하게 수정했습니다.
        print(f"✅ 나스닥이 강세였던 날(Z > {threshold}): {len(nasdaq_surge)}회")
        print(f"✅ 그 다음날 국장도 강세였던 날: {len(both_surge)}회")
        print(f"🚀 [확률] 미장 강세 시 익일 국장 강세 확률: {prob:.2f}%")
    else:
        print(f"❌ 분석 기간 내 나스닥 강세(Z > {threshold}) 사건이 없습니다.")
    print("="*45)


# 2. 데이터 수집 확인
print(f"DEBUG: 나스닥 원본 데이터 수: {len(nasdaq)}")
print(f"DEBUG: 코스피 원본 데이터 수: {len(kospi)}")

# 3. 병합 후 확인
returns_df = pd.concat([nasdaq, kospi], axis=1).dropna()
print(f"DEBUG: 병합 후 남은 일수: {len(returns_df)}")

# 4. Z-Score 계산 후 확인
returns_df['Z_NASDAQ'] = calculate_zscore(returns_df['NASDAQ'])
returns_df['Z_KOSPI'] = calculate_zscore(returns_df['KOSPI'])
print(f"DEBUG: Z-Score 계산 직후 (NaN 포함): {len(returns_df)}")

# 여기서 dropna()를 하기 전, 실제 데이터가 있는지 샘플 확인
print("--- Z-Score 샘플 (최초 110행 이후) ---")
print(returns_df[['Z_NASDAQ', 'Z_KOSPI']].iloc[100:110])

returns_df = returns_df.dropna()
print(f"DEBUG: 최종 분석 가능 일수: {len(returns_df)}")
