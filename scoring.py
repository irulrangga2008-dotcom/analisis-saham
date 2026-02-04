import numpy as np
import pandas as pd
from config import (
    PE_GOOD, PBV_GOOD, ROE_GOOD, RSI_OVERSOLD, RSI_OVERBOUGHT,
    VOLUME_CONFIRMATION_THRESHOLD
)

def normalize_score(value, min_val, max_val, ideal_min, ideal_max):
    """Normalize score between 0-100 with ideal range"""
    if pd.isna(value):
        return 50  # Neutral for missing data
    
    # Scale to 0-100
    normalized = np.clip(((value - min_val) / (max_val - min_val)) * 100, 0, 100)
    
    # Apply ideal range bonus/penalty
    if ideal_min <= value <= ideal_max:
        normalized += 20
    elif abs(value - (ideal_min + ideal_max)/2) > (max_val - min_val)/4:
        normalized -= 15
    
    return min(100, max(0, normalized))

def calculate_fundamental_score(fundamentals):
    """Fundamental scoring (40% weight)"""
    score = 0
    
    # Valuation (30%)
    pe = fundamentals.get('pe_ratio')
    pbv = fundamentals.get('pbv')
    if not pd.isna(pe):
        score += normalize_score(pe, 5, 50, 0, PE_GOOD) * 0.3
    if not pd.isna(pbv):
        score += normalize_score(pbv, 0.5, 5, 0, PBV_GOOD) * 0.3
    
    # Profitability (40%)
    roe = fundamentals.get('roe')
    eps = fundamentals.get('eps')
    if not pd.isna(roe):
        score += normalize_score(roe * 100, -20, 50, 0, ROE_GOOD) * 0.4
    if eps and eps > 0:
        score += 20 * 0.4
    
    # Growth & Debt (20%)
    debt_eq = fundamentals.get('debt_to_equity')
    rev_growth = fundamentals.get('revenue_growth')
    if not pd.isna(debt_eq) and debt_eq < 200:
        score += 15 * 0.2
    if not pd.isna(rev_growth) and rev_growth > 0:
        score += 15 * 0.2
    
    # Data completeness penalty
    completeness = fundamentals.get('data_completeness', 100)
    score *= (completeness / 100)
    
    return min(100, max(0, score))

def calculate_technical_score(indicators):
    """Technical scoring (35% weight)"""
    score = 0
    
    # RSI (25%)
    rsi = indicators.get('rsi', 50)
    if RSI_OVERSOLD < rsi < RSI_OVERBOUGHT:
        score += 80 * 0.25
    elif rsi < RSI_OVERSOLD:
        score += 90 * 0.25  # Oversold = buy opportunity
    score += normalize_score(rsi, 20, 80, 30, 70) * 0.25
    
    # MA Trend (30%)
    mas = indicators.get('mas', {})
    if (mas.get('ma20', 0) > mas.get('ma50', 0) and 
        mas.get('ma50', 0) > mas.get('ma200', 0)):
        score += 90 * 0.3
    elif mas.get('ma20', 0) > mas.get('ma200', 0):
        score += 70 * 0.3
    
    # MACD (25%)
    macd_data = indicators.get('macd', {})
    if (macd_data.get('macd', 0) > macd_data.get('signal', 0) and 
        macd_data.get('histogram', 0) > 0):
        score += 80 * 0.25
    
    # Volume confirmation (20%)
    vol_trend = indicators.get('volume_trend', 1)
    if vol_trend > VOLUME_CONFIRMATION_THRESHOLD:
        score += 85 * 0.2
    
    return min(100, max(0, score))

def calculate_risk_score(fundamentals, indicators, stock_data):
    """Risk scoring (25% weight) - higher = lower risk"""
    score = 0
    
    # Volatility (30%) - lower volatility = higher score
    if len(stock_data) > 20:
        vol = stock_data['close'].pct_change().std() * 100 * np.sqrt(252)
        score += normalize_score(vol, 20, 80, 80, 20) * 0.3  # Inverse
    
    # Liquidity (25%)
    volume = fundamentals.get('volume', 0)
    if volume > 1e9:  # 1M shares
        score += 90 * 0.25
    elif volume > 1e8:
        score += 70 * 0.25
    
    # Market cap stability (25%)
    mcap = fundamentals.get('market_cap', 0)
    if mcap > 50:  # >50T IDR
        score += 85 * 0.25
    elif mcap > 5:
        score += 65 * 0.25
    
    # Data completeness & Beta (20%)
    completeness = fundamentals.get('data_completeness', 100)
    beta = fundamentals.get('beta', 1)
    score += completeness * 0.1
    if beta < 1.5:
        score += 15 * 0.1
    
    return min(100, max(0, score))

def calculate_ai_scores(fundamentals, indicators, stock_data):
    """Main AI scoring engine"""
    fund_score = calculate_fundamental_score(fundamentals)
    tech_score = calculate_technical_score(indicators)
    risk_score = calculate_risk_score(fundamentals, indicators, stock_data)
    
    # Weighted final score
    final_score = (0.4 * fund_score + 0.35 * tech_score + 0.25 * risk_score)
    
    # Confidence based on data completeness and score consistency
    completeness = fundamentals.get('data_completeness', 50)
    confidence = min(95, 50 + (abs(fund_score - tech_score) * 0.5) + completeness * 0.3)
    
    return {
        'final_score': final_score,
        'fundamental_score': fund_score,
        'technical_score': tech_score,
        'risk_score': risk_score,
        'confidence': confidence
    }
