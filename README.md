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

----------------------------------------------------------------------------------------------------------------------------------------------------

This project investigates the lead-lag relationship between the US Nasdaq Index and the Korean KOSPI Index using Python-based quantitative analysis.

## 🛠️ Tech Stack & Environment
- **Language**: Python 3.13
- **Data Source**: Yahoo Finance API (JSON Endpoint)
- **Libraries**: Pandas, NumPy, Requests, Urllib3

## 📊 Methodology
The analysis focuses on whether a "surge" in the US market leads to a subsequent "surge" in the Korean market the following day.

### 1. Z-Score Normalization
To compare two different markets on equal ground, we calculate the rolling Z-Score of daily returns:
$$Z = \frac{x - \mu_{100d}}{\sigma_{100d}}$$
* **$x$**: Daily return
* **$\mu$**: 100-day rolling mean
* **$\sigma$**: 100-day rolling standard deviation

### 2. Time-Lag Adjustment
Since the US market ($t-1$) closes before the Korean market ($t$) opens, we shift the Nasdaq data by 1 day to analyze the predictive power of the US market as a leading indicator.

## 🚀 Key Findings (5-Year Data)
- **Nasdaq Surge Threshold**: $Z > 0.5$
- **Probability of Co-movement**: **12.00%**
- **Insight**: Contrary to the popular belief that "KOSPI follows Nasdaq," the data reveals a significant **Decoupling** effect, with only a 12% probability of a synchronized surge over the last 5 years.
