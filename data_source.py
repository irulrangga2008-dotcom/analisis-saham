import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import DATA_PERIOD, CACHE_TTL

@st.cache_data(ttl=CACHE_TTL)
def get_stock_data(ticker):
    """Fetch stock OHLCV data with error handling for IDX stocks"""
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=DATA_PERIOD)
        
        # Fetch historical data
        data = stock.history(start=start_date, end=end_date, interval="1d")
        
        if data.empty:
            return pd.DataFrame()
        
        # Ensure proper column names
        data.columns = [col.lower() for col in data.columns]
        data = data.rename(columns={
            'open': 'open', 'high': 'high', 'low': 'low', 
            'close': 'close', 'volume': 'volume'
        })
        
        return data.tail(200)  # Last 200 days for analysis
        
    except Exception as e:
        st.error(f"Error fetching {ticker}: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def get_fundamental_data(ticker):
    """Fetch fundamental data with IDX-specific handling"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Map yfinance fields to our needs (with IDX fallbacks)
        fundamentals = {
            'price': info.get('regularMarketPrice', info.get('currentPrice', 0)),
            'price_change_pct': info.get('regularMarketChangePercent', 0),
            'market_cap': info.get('marketCap', 0) / 1e12,  # Trillions
            'volume': info.get('regularMarketVolume', 0),
            'volume_change_pct': info.get('volume24Hr', 0),
            'pe_ratio': info.get('trailingPE', info.get('forwardPE', np.nan)),
            'pbv': info.get('priceToBook', np.nan),
            'eps': info.get('trailingEps', np.nan),
            'roe': info.get('returnOnEquity', np.nan),
            'debt_to_equity': info.get('debtToEquity', np.nan),
            'revenue_growth': info.get('revenueGrowth', np.nan),
            'net_profit_margin': info.get('profitMargins', np.nan),
            'beta': info.get('beta', 1.0),
            'sector': info.get('sector', 'Unknown'),
            'industry': info.get('industry', 'Unknown')
        }
        
        # Data quality check
        missing_count = sum(1 for v in fundamentals.values() if pd.isna(v) or v == 0)
        fundamentals['data_completeness'] = max(0, 100 - (missing_count * 10))
        
        return fundamentals
        
    except Exception as e:
        st.error(f"Error fetching fundamentals for {ticker}")
        return {}
