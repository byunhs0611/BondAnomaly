import asyncio
import yfinance as yf
import pandas as pd
import os
from telegram import Bot

# [분석 엔진] 형섭님의 로직 + 방어 코드 추가
def detect_bond_anomaly(threshold=2.0):
    tickers = ["^TNX", "^TYX"]
    # 1. 데이터 다운로드
    data = yf.download(tickers, period="100d", progress=False)
    
    # 데이터가 아예 없는 경우 체크
    if data.empty or 'Close' not in data:
        print("⚠️ 야후 파이낸스에서 데이터를 가져오지 못했습니다.")
        return []

    close_data = data['Close']
    
    # 2. 변화율 계산 및 결측치 제거
    returns = close_data.pct_change().dropna()
    
    # 계산 후 데이터가 비어있는지 다시 체크 (IndexError 방지)
    if returns.empty:
        print("⚠️ 계산 가능한 수익률 데이터가 충분하지 않습니다.")
        return []
    
    avg_return = returns.mean()
    std_return = returns.std()
    
    # 여기서 에러가 났던 부분을 안전하게 처리
    today_val = returns.iloc[-1]
    findings = []
    
    for ticker in tickers:
        # 데이터에 해당 티커가 있는지 확인
        if ticker not in today_val: continue
        
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

# [전송 핸들러]
async def send_to_telegram():
    TOKEN = os.getenv('BOND_BOT_TOKEN')
    CHAT_ID = os.getenv('CHAT_ID')
    
    if not TOKEN or not CHAT_ID:
        print("⚠️ Secrets 설정(TOKEN 또는 CHAT_ID)을 확인해주세요.")
        return

    bot = Bot(token=TOKEN)
    
    print("🚀 시장 데이터 분석 시작...")
    results = detect_bond_anomaly(threshold=0.001) # 테스트를 위해 낮게 설정
    
    if not results:
        print("✅ 분석 완료: 전송할 이상 변동이 없습니다.")
    else:
        print(f"📧 {len(results)}개의 알림 전송 시작!")
        for alert in results:
            await bot.send_message(chat_id=CHAT_ID, text=alert)
            await asyncio.sleep(1) 

if __name__ == "__main__":
    asyncio.run(send_to_telegram())
