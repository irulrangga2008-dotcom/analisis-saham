import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time

from data_source import get_stock_data, get_fundamental_data
from indicators import calculate_technical_indicators
from scoring import calculate_ai_scores
from ai_analysis import generate_ai_analysis
from ui_components import (
    render_kpi_cards, render_fundamental_table, render_technical_analysis,
    render_ai_decision_panel, render_ai_explanation, render_price_chart,
    render_volume_chart
)
from config import REFRESH_INTERVAL, CACHE_TTL

st.set_page_config(
    page_title="Analisis Saham IDX - AI Stock Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for fintech look
st.markdown("""
    <style>
    .main {padding: 2rem;}
    .stMetric {font-size: 1.2rem;}
    .metric-container {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .stApp {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);}
    </style>
""", unsafe_allow_html=True)

# Title & Header
st.title("🤖 AI Saham Analyzer IDX")
st.markdown("**Analisis Fundamental + Teknikal + AI Scoring untuk Investor Indonesia**")

# Sidebar
st.sidebar.header("⚙️ Kontrol")
ticker = st.sidebar.text_input("Masukkan kode saham (4 huruf)", "BBRI", help="Contoh: BUMI, BBRI, TLKM")
refresh_interval = st.sidebar.slider("Refresh otomatis (detik)", 30, 300, REFRESH_INTERVAL)

if st.sidebar.button("🔄 Refresh Manual", type="primary"):
    st.cache_data.clear()
    st.rerun()

# Auto-refresh logic
placeholder = st.empty()
if ticker:
    with placeholder.container():
        # Data fetching with caching
        @st.cache_data(ttl=CACHE_TTL)
        def load_all_data(ticker_full):
            stock_data = get_stock_data(ticker_full)
            fundamental_data = get_fundamental_data(ticker_full)
            if not stock_data.empty:
                tech_indicators = calculate_technical_indicators(stock_data)
                scores = calculate_ai_scores(fundamental_data, tech_indicators, stock_data)
                analysis = generate_ai_analysis(fundamental_data, tech_indicators, scores)
                return stock_data, fundamental_data, tech_indicators, scores, analysis
            return None, None, None, None, None
        
        ticker_full = ticker.upper() + ".JK"
        stock_data, fundamental_data, tech_indicators, scores, analysis = load_all_data(ticker_full)
        
        if stock_data is not None:
            # KPI Cards Row 1
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                render_kpi_cards("Harga Saat Ini", f"Rp {fundamental_data.get('price', 0):,.0f}", 
                               fundamental_data.get('price_change_pct', 0))
            with col2:
                render_kpi_cards("AI Score", f"{scores['final_score']:.1f}/100", 
                               scores['final_score'], is_score=True)
            with col3:
                render_kpi_cards("Volume", f"{fundamental_data.get('volume', 0):,}", 
                               fundamental_data.get('volume_change_pct', 0))
            with col4:
                render_kpi_cards("Market Cap", f"Rp {fundamental_data.get('market_cap', 0):,.0f}T", 
                               fundamental_data.get('market_cap_growth', 0))

            # Row 2: Charts & Fundamental
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 Chart Harga & Volume")
                render_price_chart(stock_data, tech_indicators)
                render_volume_chart(stock_data)
            
            with col2:
                st.subheader("📋 Data Fundamental")
                render_fundamental_table(fundamental_data)
            
            # Row 3: Technical & AI Decision
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("⚙️ Analisis Teknikal")
                render_technical_analysis(tech_indicators)
            
            with col2:
                st.subheader("🤖 Keputusan AI")
                render_ai_decision_panel(scores, analysis['recommendation'])
            
            # Row 4: AI Explanation & Conclusion
            st.subheader("📝 Analisis Lengkap AI")
            render_ai_explanation(analysis)
            
            st.markdown("---")
            st.caption(f"Terakhir diupdate: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Auto-refresh: {refresh_interval}s")
            
            # Auto-refresh
            time.sleep(refresh_interval)
            st.rerun()
        else:
            st.error(f"❌ Data tidak ditemukan untuk {ticker_full}. Coba ticker lain seperti BBRI, TLKM, BUMI")
else:
    st.info("👈 Masukkan kode saham di sidebar untuk memulai analisis")
