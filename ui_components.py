import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def render_kpi_cards(title, value, change_pct=None, is_score=False):
    """Fintech-style KPI cards"""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.metric(title, value)
    
    if change_pct is not None:
        color = "normal" if change_pct >= 0 else "inverse"
        delta = f"{abs(change_pct):.1f}%"
        with col2:
            st.metric("", delta, delta, delta_color=color)

def render_fundamental_table(fundamentals):
    """Clean fundamental data table"""
    st.markdown("**Key Metrics**")
    
    data = {
        "Metric": ["Price", "Market Cap", "Volume", "P/E", "PBV", "EPS", 
                  "ROE", "D/E", "Rev Growth", "Profit Margin"],
        "Value": [
            f"Rp {fundamentals.get('price', 0):,.0f}",
            f"Rp {fundamentals.get('market_cap', 0):,.1f}T",
            f"{fundamentals.get('volume', 0):,}",
            f"{fundamentals.get('pe_ratio', '-'):.1f}",
            f"{fundamentals.get('pbv', '-'):.1f}",
            f"{fundamentals.get('eps', '-'):.0f}",
            f"{fundamentals.get('roe', '-'):.1%}",
            f"{fundamentals.get('debt_to_equity', '-'):.1f}",
            f"{fundamentals.get('revenue_growth', '-'):.1%}",
            f"{fundamentals.get('net_profit_margin', '-'):.1%}"
        ]
    }
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

def render_technical_analysis(indicators):
    """Technical indicators display"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("RSI (14)", f"{indicators.get('rsi', 0):.0f}")
    
    with col2:
        trend = indicators.get('trend_direction', 'Sideways')
        color = "🟢" if trend == "Up" else "🟡" if trend == "Sideways" else "🔴"
        st.metric("Trend", f"{color} {trend}")
    
    with col3:
        macd = indicators.get('macd', {})
        hist = macd.get('histogram', 0)
        st.metric("MACD", f"{hist:.3f}", delta=f"Signal: {macd.get('signal', 0):.3f}")
    
    with col4:
        vol_trend = indicators.get('volume_trend', 1)
        st.metric("Volume", f"{vol_trend:.2f}x")

def render_ai_decision_panel(scores, recommendation):
    """AI decision panel"""
    st.markdown("### 🎯 Rekomendasi AI")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Final Score", f"{scores['final_score']:.0f}/100", 
                 delta=f"Conf: {scores['confidence']:.0f}%")
    
    with col2:
        st.metric("Risk Level", scores['risk_score'])
    
    with col3:
        st.error(recommendation) if "AVOID" in recommendation else \
        st.success(recommendation) if "STRONG" in recommendation else \
        st.warning(recommendation)
    
    # Progress bars
    col1, col2, col3 = st.columns(3)
    with col1:
        st.progress(scores['fundamental_score'] / 100)
        st.caption("Fundamental (40%)")
    with col2:
        st.progress(scores['technical_score'] / 100)
        st.caption("Teknikal (35%)")
    with col3:
        st.progress(scores['risk_score'] / 100)
        st.caption("Risiko (25%)")

def render_price_chart(stock_data, indicators):
    """Price chart with MAs"""
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=stock_data.index, open=stock_data['open'], high=stock_data['high'],
        low=stock_data['low'], close=stock_data['close'], name="Price"
    ))
    
    # Moving averages
    mas = indicators.get('mas', {})
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['close'].rolling(20).mean(),
                           name="MA20", line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['close'].rolling(50).mean(),
                           name="MA50", line=dict(color='blue')))
    
    fig.update_layout(height=400, title="Price Chart", xaxis_title="Date")
    st.plotly_chart(fig, use_container_width=True)

def render_volume_chart(stock_data):
    """Volume chart"""
    fig = go.Figure()
    fig.add_trace(go.Bar(x=stock_data.index, y=stock_data['volume'], 
                        name="Volume", marker_color='rgba(158,202,225,0.8)'))
    fig.update_layout(height=200, title="Volume", yaxis_title="Volume")
    st.plotly_chart(fig, use_container_width=True)

def render_ai_explanation(analysis):
    """AI explanation panel"""
    st.markdown(analysis['nl_conclusion'])
    
    st.markdown("**Faktor Penentu Score**:")
    for point in analysis['explanation'][:6]:
        st.markdown(point)
