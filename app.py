import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import FinanceDataReader as fdr
import streamlit.components.v1 as components # 자바스크립트 실행용

# config.py에서 설정 불러오기
from config import US_KOR_NAMES, CRYPTO_MAP

# 1. 웹 페이지 설정
st.set_page_config(
    page_title="주식 코인 수익률 타임머신 | 수익률 계산기", # 검색에 걸릴 제목
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed",
    # 사이트 설명 (구글 검색 결과 밑에 나오는 문구)
    menu_items={
        'About': "# 주식 & 코인 타임머신\n과거로 돌아가 수익률을 확인해보세요!"
    }
)

GTM_ID = "GTM-WQP3LQ5P" #
gtm_js = f"""
    <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
    new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    }})(window,document,'script','dataLayer','{GTM_ID}');</script>
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
    """
st.markdown(gtm_js, unsafe_allow_html=True) #

# 🎨 모바일 최적화 및 캡처 영역 설정을 위한 CSS
st.markdown("""
    <style>
    .stApp { background-color: #f4f6f9; }
    /* 캡처할 영역 지정 */
    #capture_area {
        padding: 20px;
        background-color: white;
        border-radius: 20px;
    }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #f0f2f6;
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 55px;
        font-size: 18px;
        font-weight: bold;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 로딩 로직
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

# 4. 설정 영역
with st.container():
    market_type = st.radio("🌍 투자 시장", ["🇺🇸 미국", "🇰🇷 한국", "🪙 코인"], horizontal=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if market_type == "🪙 코인":
            selected_stock = st.selectbox("종목 선택", options=list(CRYPTO_MAP.keys()))
            ticker = CRYPTO_MAP[selected_stock]
            currency = "USDT"
            default_invest = 1000
        elif market_type == "🇺🇸 미국":
            stock_options = us_list.apply(lambda x: f"{x['Name']} ({x['Symbol']})", axis=1).tolist()
            selected_stock = st.selectbox("종목 검색", options=stock_options)
            ticker = selected_stock.split('(')[-1].strip(')')
            currency = "$"
            default_invest = 1000
        else:
            stock_options = kr_list.apply(lambda x: f"{x['Name']} ({x['Code']})", axis=1).tolist()
            selected_stock = st.selectbox("종목 검색", options=stock_options)
            ticker = selected_stock.split('(')[-1].strip(')')
            if not ticker.endswith((".KS", ".KQ")): ticker = ticker + ".KS"
            currency = "원"
            default_invest = 1000000

    with col2:
        input_method = st.toggle("직접입력")
        if input_method: ticker = st.text_input("티커", value=ticker).upper()

    invest_type = st.radio("💼 투자 방식", ["한 번에 몰빵 (거치식)", "매월 꾸준히 (적립식)"], horizontal=True)
    
    col3, col4 = st.columns(2)
    with col3:
        investment = st.number_input(f"투자금 ({currency})", min_value=1, value=default_invest)
    with col4:
        past_date = st.date_input("투자 시작일", value=datetime(2023, 1, 1))

    submit_button = st.button("결과 확인하기 ✨")

# 5. 결과 및 이미지 저장 로직
if submit_button:
    try:
        with st.status("🚀 시공간 데이터를 분석 중입니다...", expanded=False):
            stock = yf.Ticker(ticker)
            df = stock.history(start=past_date)
            spy_df = yf.Ticker("SPY").history(start=past_date)
            
            if df.empty:
                st.warning(f"'{ticker}' 데이터를 찾을 수 없습니다.")
            else:
                if "거치식" in invest_type:
                    total_invested = investment
                    current_value = (total_invested / df['Close'].iloc[0]) * df['Close'].iloc[-1]
                    spy_value = (total_invested / spy_df['Close'].iloc[0]) * spy_df['Close'].iloc[-1]
                else: 
                    monthly_data = df['Close'].resample('ME').last().dropna()
                    total_invested = investment * len(monthly_data)
                    current_value = (investment / monthly_data).sum() * df['Close'].iloc[-1]
                    spy_monthly = spy_df['Close'].resample('ME').last().dropna()
                    spy_value = (investment / spy_monthly.iloc[:min(len(monthly_data), len(spy_monthly))]).sum() * spy_df['Close'].iloc[-1]

                return_rate = ((current_value - total_invested) / total_invested) * 100
                total_profit = current_value - total_invested
                
                # 🔥 원화 수익금 계산 로직
                krw_profit = total_profit * ex_rate if currency != "원" else total_profit

                # 📸 [IMAGE CAPTURE START] 캡처할 영역 시작
                st.markdown('<div id="capture_area" style="background-color: white; border-radius: 20px; padding: 20px;">', unsafe_allow_html=True)
                
                st.subheader(f"🎯 나의 투자 성적표")
                st.caption(f"자산: {selected_stock} | 모드: {invest_type}")
                
                m1, m2, m3 = st.columns(3)
                m1.metric("최종 자산", f"{current_value:,.0f}{currency}", f"{return_rate:.2f}%")
                m2.metric("총 원금", f"{total_invested:,.0f}{currency}")
                m3.metric("순수익", f"{total_profit:,.0f}{currency}")
                
                # 🔥 [NEW] 원화 수익금 강조 섹션 (이미지 포함용)
                if currency != "원":
                    st.markdown(f"""
                    <div style="background-color: #e8f4ff; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 20px; border: 1px solid #cce5ff;">
                        <span style="color: #555; font-size: 14px;">🇰🇷 실시간 환율 적용 한화 순수익</span><br>
                        <span style="color: #007bff; font-size: 24px; font-weight: bold;">약 {krw_profit:,.0f} 원</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 팩트체크 차트
                compare_data = pd.DataFrame({'자산 가치': [current_value, spy_value]}, index=['내 선택', 'S&P 500'])
                st.bar_chart(compare_data, height=300)
                
                st.markdown(f"**💡 {selected_stock} 떡볶이 지수:** 순수익으로 떡볶이 **{int(krw_profit/15000):,}세트** 가능!")
                st.markdown('</div>', unsafe_allow_html=True)
                # 📸 [IMAGE CAPTURE END]

                # 📥 이미지 저장 버튼
                components.html(
                    f"""
                    <script src="https://html2canvas.hertzen.com/dist/html2canvas.min.js"></script>
                    <button id="save_btn" style="
                        width: 100%; height: 50px; background-color: #4CAF50; color: white; 
                        border: none; border-radius: 15px; cursor: pointer; font-size: 16px; font-weight: bold; margin-top: 10px;
                    ">📸 결과 화면 이미지로 저장하기</button>
                    <script>
                    const btn = document.getElementById('save_btn');
                    btn.addEventListener('click', () => {{
                        const area = window.parent.document.getElementById('capture_area');
                        html2canvas(area).then(canvas => {{
                            const link = document.createElement('a');
                            link.download = 'timemachine_result_{datetime.now().strftime("%Y%m%d")}.png';
                            link.href = canvas.toDataURL();
                            link.click();
                        }});
                    }});
                    </script>
                    """, height=70,
                )

                st.divider()
                st.markdown("<p style='text-align: center; color: #666;'>개발자 떡볶이 사주기 🥘</p>", unsafe_allow_html=True)
                st.link_button("💛 카카오페이 후원", url="https://qr.kakaopay.com/FLBnVLTrZ9c409700", use_container_width=True)

    except Exception as e:
        st.error(f"오류: {e}")