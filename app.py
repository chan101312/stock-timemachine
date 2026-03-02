import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import FinanceDataReader as fdr

# config.py에서 설정 불러오기
from config import US_KOR_NAMES, CRYPTO_MAP

# 1. 웹 페이지 설정 (모바일에 맞게 'centered'로 변경)
st.set_page_config(page_title="타임머신 Pro", page_icon="🚀", layout="centered")

# 🎨 [NEW] 모바일 최적화 CSS 디자인 입히기
st.markdown("""
    <style>
    /* 전체 배경색을 약간 회색빛으로 해서 앱 느낌 살리기 */
    .stApp { background-color: #f4f6f9; font-family: 'Pretendard', sans-serif; }
    
    /* 윗부분 여백 줄이기 */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* 메트릭(결과 숫자)을 예쁜 카드 형태로 만들기 */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #f0f2f6;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        text-align: center;
    }
    
    /* 라디오 버튼 가로 정렬 시 간격 조정 */
    div.row-widget.stRadio > div { flex-direction: row; align-items: stretch; }
    
    /* 결과 확인 버튼을 크고 눈에 띄게 (토스 스타일) */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 55px;
        font-size: 18px;
        font-weight: bold;
        background-color: #ff4b4b;
        color: white;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover { background-color: #ff3333; transform: scale(1.02); }
    
    /* 입력창 모서리 둥글게 */
    .stTextInput>div>div>input, .stNumberInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 및 환율 로딩 (기존과 동일)
@st.cache_data
def get_stock_list():
    us_fallback = pd.DataFrame([{'Symbol': k, 'Name': v} for k, v in list(US_KOR_NAMES.items())[:10]])
    kr_fallback = pd.DataFrame([{'Code': '005930', 'Name': '삼성전자'}, {'Code': '000660', 'Name': 'SK하이닉스'}])
    try: 
        us_stocks = fdr.StockListing('NASDAQ')
        us_stocks['Name'] = us_stocks.apply(lambda x: f"{x['Name']} / {US_KOR_NAMES.get(x['Symbol'], '')}".strip(' / '), axis=1)
    except: us_stocks = us_fallback
    try: kr_stocks = fdr.StockListing('KRX')
    except: kr_stocks = kr_fallback
    return us_stocks, kr_stocks

@st.cache_data(ttl=3600) 
def get_exchange_rate():
    try: return yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[-1]
    except: return 1350.0 

us_list, kr_list = get_stock_list()
ex_rate = get_exchange_rate()

# 3. 메인 화면 헤더
st.title("🚀 타임머신 Pro")
st.caption("과거의 선택이 내 통장을 어떻게 바꿨을까?")

# 4. 모바일 친화적인 설정 영역 (사이드바 제거, 메인에 배치)
with st.container():
    # 터치하기 쉽게 수평(horizontal) 라디오 버튼 적용
    market_type = st.radio("🌍 투자 시장", ["🇺🇸 미국", "🇰🇷 한국", "🪙 코인"], horizontal=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        # 시장별 종목 검색 로직
        if market_type == "🪙 코인":
            selected_stock = st.selectbox("종목 선택", options=list(CRYPTO_MAP.keys()))
            ticker = CRYPTO_MAP[selected_stock]
            currency = "USDT"
            default_invest = 1000
        elif market_type == "🇺🇸 미국":
            stock_options = us_list.apply(lambda x: f"{x['Name']} ({x['Symbol']})", axis=1).tolist()
            selected_stock = st.selectbox("종목 검색 (한글/영어)", options=stock_options)
            ticker = selected_stock.split('(')[-1].strip(')')
            currency = "$"
            default_invest = 1000
        else: # 한국
            stock_options = kr_list.apply(lambda x: f"{x['Name']} ({x['Code']})", axis=1).tolist()
            selected_stock = st.selectbox("종목 검색", options=stock_options)
            ticker = selected_stock.split('(')[-1].strip(')')
            if not ticker.endswith((".KS", ".KQ")): ticker = ticker + ".KS"
            currency = "원"
            default_invest = 1000000

    with col2:
        # 모바일에선 토글 버튼으로 수동 입력 지원
        input_method = st.toggle("직접입력")
        if input_method:
            ticker = st.text_input("티커", value=ticker).upper()

    # 투자 방식 및 금액 설정
    invest_type = st.radio("💼 투자 방식", ["한 번에 몰빵 (거치식)", "매월 꾸준히 (적립식)"], horizontal=True)
    
    col3, col4 = st.columns(2)
    with col3:
        amount_label = f"투자금 ({currency})"
        investment = st.number_input(amount_label, min_value=1, value=default_invest)
    with col4:
        past_date = st.date_input("투자 시작일", value=datetime(2023, 1, 1))

    if currency != "원": 
        st.caption(f"ℹ️ 적용된 환율: 1{currency} = {ex_rate:,.0f}원")

    st.write("") # 버튼 위 여백
    submit_button = st.button("결과 확인하기 ✨")

# 5. 수익률 멘트 (떡볶이 유니버스)
def get_commentary(rate, krw_profit):
    tteok_price = 15000 
    tteok_count = int(krw_profit / tteok_price)
    if rate > 500: return f"🏆 **전설의 트레이더!** 순수익으로 떡볶이 **{tteok_count:,}세트** 쏩니다! 건물주가 코앞이네요! 🚀"
    elif rate > 100: return f"🔥 **대박 사건!** 수익금이 엄청납니다. 이 정도면 떡볶이 트럭 하나 뽑고도 남습니다! 🥘"
    elif rate > 0: return f"🌱 **소소한 수익!** 은행 이자보단 낫네요. 번 돈으로 떡볶이 **{tteok_count:,}세트** 공짜로 드시죠! 🥟"
    elif rate > -20: return f"😅 **휴우~** 손실이 났네요. 떡볶이 국물로 쓰린 속을 달래보시죠."
    else: return f"😇 **신의 한 수!** 투자 안 하길 천만다행입니다. 잃을 뻔한 돈으로 떡볶이나 배터지게 드세요!"

# 6. 결과 출력 영역
if submit_button:
    try:
        with st.status("🚀 시공간 데이터를 분석 중입니다...", expanded=True) as status:
            stock = yf.Ticker(ticker)
            df = stock.history(start=past_date)
            spy_df = yf.Ticker("SPY").history(start=past_date)
            
            if df.empty:
                status.update(label="데이터 탐색 실패!", state="error", expanded=True)
                st.warning(f"'{ticker}' 데이터를 찾을 수 없습니다.")
            else:
                # 거치식/적립식 계산 (기존 로직 동일)
                if "거치식" in invest_type:
                    total_invested = investment
                    current_value = (total_invested / df['Close'].iloc[0]) * df['Close'].iloc[-1]
                    days_passed = (datetime.now().date() - past_date).days
                    bank_value = total_invested * ((1 + 0.035 / 365) ** days_passed)
                    if not spy_df.empty: spy_value = (total_invested / spy_df['Close'].iloc[0]) * spy_df['Close'].iloc[-1]
                    else: spy_value = total_invested
                else: 
                    monthly_data = df['Close'].resample('ME').last().dropna()
                    total_invested = investment * len(monthly_data)
                    current_value = (investment / monthly_data).sum() * df['Close'].iloc[-1]
                    monthly_rate = 0.035 / 12
                    months = len(monthly_data)
                    bank_value = investment * (((1 + monthly_rate) ** months) - 1) / monthly_rate if months > 0 else total_invested
                    if not spy_df.empty:
                        spy_monthly = spy_df['Close'].resample('ME').last().dropna()
                        min_len = min(len(monthly_data), len(spy_monthly))
                        spy_value = (investment / spy_monthly.iloc[:min_len]).sum() * spy_df['Close'].iloc[-1]
                    else: spy_value = total_invested

                return_rate = ((current_value - total_invested) / total_invested) * 100
                total_profit = current_value - total_invested
                krw_total_profit = total_profit * ex_rate if currency != "원" else total_profit

                status.update(label="분석 완료!", state="complete", expanded=False)
                
                # [NEW] 모바일 친화적 결과 출력 (세로로 길게, 카드처럼)
                st.subheader(f"🎯 나의 투자 성적표")
                
                # 모바일에서는 3열이 찌그러지므로 1열 강조 후 2열로 배치
                m_main, m_sub1, m_sub2 = st.columns(3) # CSS로 둥근 박스 처리됨
                m_main.metric("최종 자산", f"{current_value:,.0f} {currency}", f"{return_rate:.2f}%")
                m_sub1.metric("총 원금", f"{total_invested:,.0f} {currency}")
                m_sub2.metric("순수익", f"{total_profit:,.0f} {currency}")
                
                st.success(get_commentary(return_rate, krw_total_profit))
                
                # 팩트 폭행 비교 (막대 차트)
                st.subheader("📊 시장 평균 vs 예금 vs 내 선택")
                compare_data = pd.DataFrame({
                    '자산 가치': [current_value, spy_value, bank_value]
                }, index=[f'내 선택', 'S&P 500', '은행(3.5%)'])
                st.bar_chart(compare_data, height=350) # 모바일에 맞게 높이 조절
                
                spy_rate = ((spy_value - total_invested) / total_invested) * 100
                if return_rate > spy_rate:
                    st.info(f"🎉 훌륭합니다! 맘 편한 S&P 500({spy_rate:.1f}%)을 이겼습니다!")
                else:
                    st.warning(f"🤔 맘 편하게 S&P 500({spy_rate:.1f}%)이나 살걸 그랬네요!")

                st.subheader(f"📈 주가 흐름")
                st.line_chart(df['Close'])
                
    except Exception as e:
        st.error(f"오류: {e}")

    # ... (기존 코드의 st.line_chart(df['Close']) 밑에 추가) ...

# ... (기존 메인 화면 차트 코드 끝난 후, 맨 아래에 추가) ...

# 7. 후원하기 뱃지 (화면 맨 아래)
st.divider()

# app.py 맨 하단에 추가
st.divider()
st.markdown("<h4 style='text-align: center;'>🥘 개발자에게 떡볶이 후원하기</h4>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # 👇 여기에 복사한 링크(https://qr.kakaopay.com/...)를 붙여넣으세요!
    kakaopay_url = "https://qr.kakaopay.com/FLBnVLTrZ9c409700"
    st.link_button("💛 카카오페이로 떡볶이 쏘기", url=kakaopay_url, use_container_width=True)

st.markdown("<br><br><br>", unsafe_allow_html=True) # 스마트폰에서 맨 아래 여백을 넉넉하게