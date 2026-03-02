import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import FinanceDataReader as fdr

# config.py에서 설정 불러오기
from config import US_KOR_NAMES, CRYPTO_MAP

# 1. 웹 페이지 설정
st.set_page_config(page_title="주식 & 코인 타임머신 Pro", page_icon="💰", layout="wide")

# 2. 데이터 및 환율 로딩
@st.cache_data
def get_stock_list():
    us_fallback = pd.DataFrame([{'Symbol': k, 'Name': v} for k, v in list(US_KOR_NAMES.items())[:10]])
    kr_fallback = pd.DataFrame([{'Code': '005930', 'Name': '삼성전자'}, {'Code': '000660', 'Name': 'SK하이닉스'}])
    
    try: 
        us_stocks = fdr.StockListing('NASDAQ')
        us_stocks['Name'] = us_stocks.apply(
            lambda x: f"{x['Name']} / {US_KOR_NAMES.get(x['Symbol'], '')}".strip(' / '), axis=1
        )
    except: us_stocks = us_fallback

    try: kr_stocks = fdr.StockListing('KRX')
    except: kr_stocks = kr_fallback
        
    return us_stocks, kr_stocks

@st.cache_data(ttl=3600) # 환율은 1시간(3600초)마다 한 번씩만 새로고침 (서버 부하 방지)
def get_exchange_rate():
    try:
        return yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[-1]
    except:
        return 1350.0 # 에러 발생 시 임시 고정 환율

us_list, kr_list = get_stock_list()
ex_rate = get_exchange_rate() # 현재 환율 가져오기

# 3. 사이드바 구성
with st.sidebar:
    st.header("🕰️ 타임머신 세팅")
    market_type = st.radio("시장 선택", ["미국 (NASDAQ)", "한국 (KRX)", "암호화폐 (Crypto)"])
    
    input_method = st.toggle("티커 직접 입력", value=False)
    invest_type = st.radio("투자 방식", ["💰 한 번에 몰빵 (거치식)", "🗓️ 매월 꾸준히 (적립식)"])
    
    # 시장별 설정
    if market_type == "암호화폐 (Crypto)":
        if input_method:
            ticker = st.text_input("코인 티커 입력 (예: BTC-USD)", value="BTC-USD").upper()
            if not ticker.endswith("-USD"): ticker += "-USD"
            selected_stock = ticker
        else:
            selected_stock = st.selectbox("코인 검색", options=list(CRYPTO_MAP.keys()))
            ticker = CRYPTO_MAP[selected_stock]
        currency = "USDT"
        default_invest = 1000

    elif market_type == "미국 (NASDAQ)":
        if input_method:
            ticker = st.text_input("미국 티커 입력 (예: AAPL)", value="AAPL").upper()
            selected_stock = ticker
        else:
            stock_options = us_list.apply(lambda x: f"{x['Name']} ({x['Symbol']})", axis=1).tolist()
            selected_stock = st.selectbox("종목 검색", options=stock_options)
            ticker = selected_stock.split('(')[-1].strip(')')
        currency = "$"
        default_invest = 1000

    else: # 한국 시장
        if input_method:
            code = st.text_input("한국 종목번호 입력 (예: 005930)", value="005930")
            ticker = code + ".KS"
            selected_stock = code
        else:
            stock_options = kr_list.apply(lambda x: f"{x['Name']} ({x['Code']})", axis=1).tolist()
            selected_stock = st.selectbox("종목 검색", options=stock_options)
            ticker = selected_stock.split('(')[-1].strip(')')
            if not ticker.endswith((".KS", ".KQ")): ticker = ticker + ".KS"
        currency = "원"
        default_invest = 1000000

    amount_label = f"매월 투자 금액 ({currency})" if "적립식" in invest_type else f"초기 투자 금액 ({currency})"
    investment = st.number_input(amount_label, min_value=1, value=default_invest)
    past_date = st.date_input("투자 시작일", value=datetime(2023, 1, 1))
    
    submit_button = st.button("결과 확인하기 ✨", use_container_width=True)
    
    if currency != "원":
        st.caption(f"ℹ️ 적용된 실시간 환율: 1{currency} = {ex_rate:,.2f}원")

# 4. 수익률 멘트 (원화 기준으로 통일해서 떡볶이 계산)
def get_commentary(rate, krw_profit):
    tteok_price = 15000
    tteok_count = int(krw_profit / tteok_price)
    
    if rate > 500:
        return f"🏆 **전설의 트레이더!** 순수익으로 떡볶이 **{tteok_count:,}세트** 쏩니다! 건물주가 코앞이네요! 🚀"
    elif rate > 100:
        return f"🔥 **대박 사건!** 수익금이 엄청납니다. 이 정도면 떡볶이 트럭 하나 뽑고도 남습니다! 🥘"
    elif rate > 0:
        return f"🌱 **소소한 수익!** 은행 이자보단 낫네요. 번 돈으로 떡볶이 **{tteok_count:,}세트** 공짜로 드시죠! 🥟"
    elif rate > -20:
        return f"😅 **휴우~** 손절 라인을 살짝 넘겼습니다. 떡볶이 국물로 쓰린 속을 달래보시죠."
    else:
        return f"😇 **신의 한 수!** 투자 안 하길 천만다행입니다. 잃을 뻔한 돈으로 떡볶이나 배터지게 드세요!"

# 5. 메인 화면
st.title("🚀 주식 & 코인 타임머신 Pro")
st.write(f"현재 선택된 자산: **{selected_stock}** ({ticker}) | 모드: **{invest_type.split(' ')[1]}**")

if submit_button:
    try:
        with st.status("🚀 타임머신 가동! 시공간 데이터를 불러오는 중...", expanded=True) as status:
            st.write("📡 글로벌 금융 데이터베이스 연결 중...")
            stock = yf.Ticker(ticker)
            
            st.write(f"📅 {past_date} 기준 과거 데이터 탐색 중...")
            df = stock.history(start=past_date)
            
            if df.empty:
                status.update(label="데이터 탐색 실패!", state="error", expanded=True)
                st.warning(f"'{ticker}' 데이터를 찾을 수 없습니다.")
            else:
                st.write("🧮 자산 가치 변화 및 수익률 계산 중...")
                
                # 계산 로직
                if "거치식" in invest_type:
                    total_invested = investment
                    past_price = df['Close'].iloc[0]
                    current_price = df['Close'].iloc[-1]
                    shares_bought = total_invested / past_price
                    current_value = shares_bought * current_price
                else: # 적립식
                    monthly_data = df['Close'].resample('ME').last().dropna()
                    total_invested = investment * len(monthly_data)
                    shares_bought = (investment / monthly_data).sum()
                    current_price = df['Close'].iloc[-1]
                    current_value = shares_bought * current_price
                    st.write(f"💡 총 {len(monthly_data)}개월 동안 꾸준히 매수했습니다.")

                return_rate = ((current_value - total_invested) / total_invested) * 100
                total_profit = current_value - total_invested
                
                # 원화(KRW) 환산 로직
                if currency != "원":
                    krw_current_value = current_value * ex_rate
                    krw_total_invested = total_invested * ex_rate
                    krw_total_profit = total_profit * ex_rate
                else:
                    krw_current_value = current_value
                    krw_total_invested = total_invested
                    krw_total_profit = total_profit

                status.update(label="분석 완료! 결과를 확인하세요.", state="complete", expanded=False)
                
                # 결과 지표 출력
                st.divider()
                m1, m2, m3 = st.columns(3)
                
                m1.metric("최종 자산 (평가금액)", f"{current_value:,.2f} {currency}", f"{return_rate:.2f}%")
                if currency != "원": m1.caption(f"🇰🇷 약 **{krw_current_value:,.0f}** 원")
                
                m2.metric("총 투자 원금", f"{total_invested:,.2f} {currency}")
                if currency != "원": m2.caption(f"🇰🇷 약 **{krw_total_invested:,.0f}** 원")
                
                m3.metric("순수익", f"{total_profit:,.2f} {currency}")
                if currency != "원": m3.caption(f"🇰🇷 약 **{krw_total_profit:,.0f}** 원")

                st.success(get_commentary(return_rate, krw_total_profit))
                st.line_chart(df['Close'])
                
    except Exception as e:
        st.error(f"오류: {e}")