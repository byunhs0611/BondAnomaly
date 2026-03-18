import asyncio
import yfinance as yf
import pandas as pd
import os

# 직접 토큰을 적지 말고, 환경 변수에서 가져오게 합니다.
TOKEN = os.getenv('BOND_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
from telegram import Bot

# [분석 엔진] 형섭님이 작성하신 로직
def detect_bond_anomaly(threshold=0.001):
    tickers = ["^TNX", "^TYX"]
    # progress=False를 추가하면 터미널이 깨끗해집니다.
    data = yf.download(tickers, period="100d", progress=False)['Close']
    
    returns = data.pct_change().dropna()
    avg_return = returns.mean()
    std_return = returns.std()
    
    today_val = returns.iloc[-1]
    findings = []
    
    for ticker in tickers:
        z_score = (today_val[ticker] - avg_return[ticker]) / std_return[ticker]
        
        if abs(z_score) > threshold:
            name = "미 국채 10년물" if ticker == "^TNX" else "미 국채 30년물"
            move_type = "🚀 급등" if z_score > 0 else "📉 급락"
            
            msg = (f"🔔 [이상 변동 감지]\n"
                   f"종목: {name} ({ticker})\n"
                   f"상태: {move_type}\n"
                   f"변화율: {today_val[ticker]*100:.2f}%\n"
                   f"위험도(Z-Score): {z_score:.2f}")
            findings.append(msg)
            
    return findings

# [전송 핸들러] 분석 결과를 텔레그램으로 전송
# [전송 핸들러] 분석 결과를 텔레그램으로 전송
async def send_to_telegram():
    # --- 여기에 본인의 정보 입력 ---
    TOKEN = os.getenv('BOND_BOT_TOKEN')
    CHAT_ID = os.getenv('CHAT_ID')
    # ----------------------------
    
    # 이 줄(47행)의 시작 부분이 윗줄(TOKEN = ...)과 정확히 수직으로 맞아야 합니다.
    bot = Bot(token=TOKEN)
    
    print("시장 데이터 분석 중...")
    results = detect_bond_anomaly(threshold=2.0)
    
    if not results:
        print("평온한 시장입니다. 전송할 내용이 없습니다.")
    else:
        print(f"{len(results)}개의 이상치 발견! 전송을 시작합니다.")
        for alert in results:
            await bot.send_message(chat_id=CHAT_ID, text=alert)
            # 텔레그램 API 도배 방지를 위해 1초 대기
            await asyncio.sleep(1)
if __name__ == "__main__":
    # 비동기 함수 실행
    asyncio.run(send_to_telegram())
