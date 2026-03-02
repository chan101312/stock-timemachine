# config.py

# 🇺🇸 미국 주식 한글 이름 매핑 사전 (자유롭게 추가하세요)
US_KOR_NAMES = {
    # 우주 & 원전 & 미래 기술
    'RKLB': '로켓랩', 'LUNR': '인튜이티브 머신스', 'OKLO': '오클로', 'SIDU': '사이더스 스페이스',
    'ASTS': 'AST 스페이스모바일', 'PLTR': '팔란티어', 'SYM': '심보틱', 'PATH': '유아이패스',
    
    # 이커머스 & 소비재
    'CPNG': '쿠팡', 'SE': '쇼피 (Sea)', 'AMZN': '아마존', 'BABA': '알리바바',
    'MELI': '메르카도리브레', 'WMT': '월마트', 'COST': '코스트코', 
    'SBUX': '스타벅스', 'KO': '코카콜라', 'PEP': '펩시코',
    
    # 빅테크 & IT
    'AAPL': '애플', 'MSFT': '마이크로소프트', 'GOOGL': '구글', 'META': '메타 (페이스북)',
    'TSLA': '테슬라', 'NFLX': '넷플릭스', 'MSTR': '마이크로스트레티지', 'COIN': '코인베이스',
    
    # 반도체
    'NVDA': '엔비디아', 'TSM': 'TSMC', 'AMD': 'AMD', 'INTC': '인텔', 
    'ASML': 'ASML', 'QCOM': '퀄컴', 'AVGO': '브로드컴', 'MU': '마이크론', 'ARM': 'ARM',
    
    # 금융 & 헬스케어
    'V': '비자', 'MA': '마스터카드', 'JPM': 'JP모건', 'BRK.B': '버크셔 해서웨이',
    'LLY': '일라이 릴리', 'NVO': '노보 노디스크', 'JNJ': '존슨앤드존슨',
    
    # 인기 ETF (레버리지/인버스 포함)
    'SPY': 'S&P 500 ETF', 'QQQ': '나스닥 100 ETF', 'SCHD': '미국 배당 다우존스',
    'TQQQ': '나스닥 3배 롱', 'SQQQ': '나스닥 3배 숏', 
    'SOXL': '반도체 3배 롱', 'SOXS': '반도체 3배 숏', 'JEPI': 'JP모건 고배당 ETF'
}

# 🪙 암호화폐 티커 매핑
CRYPTO_MAP = {
    "비트코인 (BTC)": "BTC-USD",
    "이더리움 (ETH)": "ETH-USD",
    "솔라나 (SOL)": "SOL-USD",
    "리플 (XRP)": "XRP-USD",
    "도지코인 (DOGE)": "DOGE-USD",
    "에이다 (ADA)": "ADA-USD",
    "바이낸스코인 (BNB)": "BNB-USD",
    "시바이누 (SHIB)": "SHIB-USD",
    "체인링크 (LINK)": "LINK-USD"
}