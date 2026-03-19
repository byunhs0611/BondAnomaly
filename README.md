# 📈 Nasdaq-Kospi Correlation Analysis

미국 나스닥 지수의 강세가 다음 날 한국 코스피 지수에 미치는 영향을 분석하는 파이썬 프로젝트입니다.

## 🛠️ 분석 환경
- **Language**: Python 3.13
- **Libraries**: Pandas, NumPy, Requests
- **Data Source**: Yahoo Finance API (JSON)

## 📊 분석 방법론
- 최근 5년치 데이터를 기반으로 수익률의 **$Z$-Score**를 산출합니다.
- $$Z = \frac{x - \mu}{\sigma}$$
- 어제 나스닥의 강세($Z > 0.5$)가 오늘 코스피의 강세로 이어지는지 조건부 확률을 계산합니다.

## 🚀 분석 결과
- **나스닥 강세 시 익일 코스피 동반 상승 확률: 12.00%**
- 통계적 기대값(약 31%)보다 낮은 수치를 기록하며, 한-미 증시 간의 **디커플링(Decoupling)** 현상을 데이터로 확인했습니다.