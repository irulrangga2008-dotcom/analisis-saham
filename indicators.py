import pandas as pd
import numpy as np
import streamlit as st
from config import RSI_PERIOD, MACD_FAST, MACD_SLOW, MACD_SIGNAL

def calculate_rsi(data, period=RSI_PERIOD):
    """Calculate RSI with proper handling"""
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(data):
    """Calculate MACD"""
    ema_fast = data['close'].ewm(span=MACD_FAST).mean()
    ema_slow = data['close'].ewm(span=MACD_SLOW).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=MACD_SIGNAL).mean()
    histogram = macd - signal
    return {
        'macd': macd.iloc[-1],
        'signal': signal.iloc[-1],
        'histogram': histogram.iloc[-1]
    }

def calculate_moving_averages(data):
    """Calculate multiple MAs"""
    return {
        'ma20': data['close'].rolling(20).mean().iloc[-1],
        'ma50': data['close'].rolling(50).mean().iloc[-1],
        'ma200': data['close'].rolling(200).mean().iloc[-1]
    }

def calculate_volume_trend(data, periods=20):
    """Volume trend analysis"""
    recent_volume = data['volume'].tail(periods).mean()
    past_volume = data['volume'].tail(periods*2).head(periods).mean()
    volume_ratio = recent_volume / past_volume if past_volume > 0 else 1
    return volume_ratio

def calculate_technical_indicators(stock_data):
    """Main technical indicators calculator"""
    if stock_data.empty:
        return {}
    
    indicators = {
        'rsi': calculate_rsi(stock_data),
        'macd': calculate_macd(stock_data),
        'mas': calculate_moving_averages(stock_data),
        'volume_trend': calculate_volume_trend(stock_data),
        'price': stock_data['close'].iloc[-1],
        'price_change': stock_data['close'].pct_change().tail(5).mean() * 100
    }
    
    # Trend direction
    ma_trend = 1 if indicators['mas']['ma20'] > indicators['mas']['ma50'] > indicators['mas']['ma200'] else 0
    indicators['trend_direction'] = 'Up' if ma_trend == 1 else 'Sideways' if ma_trend == 0.5 else 'Down'
    
    return indicators
