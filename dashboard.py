import streamlit as st
import pandas as pd
from clickhouse_driver import Client
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime
import warnings

warnings.filterwarnings("ignore") # 경고창 박멸
st.set_page_config(page_title="WhalePulse Enterprise", layout="wide", page_icon="🐳")

st.markdown("""
    <style>
    .stAlert { display: none; } 
    [data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 700; }
    .main { background-color: #05070a; }
    </style>
    """, unsafe_allow_html=True)

# 데이터베이스 연결
@st.cache_resource
def get_client():
    return Client(host='localhost', port=9000, password='1234')

def get_data():
    client = get_client()
    # 최근 200건으로 분석 범위 확대
    query = "SELECT event_time, amount_usd, price, side FROM whale_trades ORDER BY event_time DESC LIMIT 200"
    data = client.execute(query)
    df = pd.DataFrame(data, columns=['시간', '금액(USD)', '가격', '구분'])
    df['시간'] = pd.to_datetime(df['시간'])
    return df

# 비즈니스 로직
def analyze_market(df):
    buy_vol = df[df['구분'] == 'BUY']['금액(USD)'].sum()
    sell_vol = df[df['구분'] == 'SELL']['금액(USD)'].sum()
    
    # 고래 심리 지수 (WSI)
    sentiment = (buy_vol / (buy_vol + sell_vol)) * 100 if (buy_vol + sell_vol) > 0 else 50
    
    # 누적 델타 (CVD) - 매수세와 매도세
    df = df.sort_values('시간')
    df['delta'] = df.apply(lambda x: x['금액(USD)'] if x['구분'] == 'BUY' else -x['금액(USD)'], axis=1)
    df['CVD'] = df['delta'].cumsum()
    
    return sentiment, buy_vol, sell_vol, df

# --- UI 레이아웃 ---
st.title("🐳 WhalePulse Enterprise")
st.caption(f"이남호(leenamho2000)님의 실시간 시장 감시 시스템 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
    raw_df = get_data()
    if not raw_df.empty:
        sentiment, b_vol, s_vol, processed_df = analyze_market(raw_df)

        # 상단 섹션: 의사결정 핵심 지표
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("고래 매수 심리", f"{sentiment:.1f}%", delta=f"{sentiment-50:.1f}%", delta_color="normal")
        with m2:
            st.metric("최근 200건 매수총액", f"${b_vol/1e6:.1f}M")
        with m3:
            st.metric("최근 200건 매도총액", f"${s_vol/1e6:.1f}M")
        with m4:
            status = "강력 매수" if sentiment > 60 else "강력 매도" if sentiment < 40 else "관망(Neutral)"
            st.metric("AI 시장 진단", status)

        st.write("---")

        # 중앙 섹션: 시각화 분석
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("📈 실시간 고래 활동 및 누적 거래흐름(CVD)")
            # 이중 축 차트 구성 (가격/금액 + 누적 흐름)
            fig = px.scatter(processed_df, x='시간', y='금액(USD)', color='구분', 
                             size='금액(USD)', hover_data=['가격'],
                             color_discrete_map={'BUY': '#00FF7F', 'SELL': '#FF4B4B'},
                             template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        with col_right:
            st.subheader("📊 매수 vs 매도 비중")
            fig_pie = px.pie(values=[b_vol, s_vol], names=['BUY', 'SELL'], 
                             color=['BUY', 'SELL'],
                             color_discrete_map={'BUY': '#00FF7F', 'SELL': '#FF4B4B'},
                             hole=0.6, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)

        # 하단 섹션: 트랜잭션 로그
        st.subheader("📜 상세 분석 로그")
        st.dataframe(processed_df.sort_values('시간', ascending=False).head(20).style.format({
            '금액(USD)': '${:,.0f}',
            '가격': '${:,.2f}',
            'CVD': '${:,.0f}'
        }), use_container_width=True)

    time.sleep(2)
    st.rerun()

except Exception as e:
    st.error(f"데이터 수신 대기 중... {e}")
    time.sleep(5)
    st.rerun()