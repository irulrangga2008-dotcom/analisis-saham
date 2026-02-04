from config import SCORE_THRESHOLDS

def get_recommendation(final_score, confidence):
    """Map score to recommendation"""
    if final_score >= SCORE_THRESHOLDS['strong_buy'] and confidence > 75:
        return "STRONG BUY"
    elif final_score >= SCORE_THRESHOLDS['buy']:
        return "BUY (Speculative)"
    elif final_score >= SCORE_THRESHOLDS['hold']:
        return "HOLD"
    else:
        return "AVOID"

def get_risk_level(final_score, risk_score):
    """Determine risk level"""
    if risk_score >= 80:
        return "Low"
    elif risk_score >= 60:
        return "Medium"
    else:
        return "High"

def generate_ai_analysis(fundamentals, indicators, scores):
    """Generate comprehensive AI analysis"""
    final_score = scores['final_score']
    recommendation = get_recommendation(final_score, scores['confidence'])
    risk_level = get_risk_level(final_score, scores['risk_score'])
    
    # Build explanation
    explanation = []
    
    # Fundamental factors
    pe = fundamentals.get('pe_ratio')
    if pe and pe < 15:
        explanation.append("✅ PE ratio rendah menunjukkan valuasi menarik")
    elif pe and pe > 25:
        explanation.append("⚠️ PE ratio tinggi - waspada overvaluation")
    
    roe = fundamentals.get('roe')
    if roe and roe > 0.15:
        explanation.append("✅ ROE kuat menunjukkan profitabilitas baik")
    
    # Technical factors
    rsi = indicators.get('rsi')
    if 30 < rsi < 70:
        explanation.append("✅ RSI di zona netral - momentum stabil")
    
    trend = indicators.get('trend_direction', '')
    if trend == 'Up':
        explanation.append("📈 Trend MA bullish (MA20 > MA50 > MA200)")
    
    # Risk factors
    mcap = fundamentals.get('market_cap', 0)
    if mcap < 1:
        explanation.append("⚠️ Market cap kecil - risiko likuiditas")
    
    analysis = {
        'recommendation': recommendation,
        'risk_level': risk_level,
        'confidence': scores['confidence'],
        'explanation': explanation,
        'strengths': ["Data lengkap", "Analisis multidimensi"][:2],
        'weaknesses': ["Volatilitas pasar", "Faktor makroekonomi"][:1]
    }
    
    # Natural language conclusion
    analysis['nl_conclusion'] = f"""
    **Kesimpulan Analis**: {recommendation} dengan {risk_level.lower()} risk dan {scores['confidence']:.0f}% confidence.
    
    Saham ini menunjukkan {trend.lower()} trend dengan fundamental {'kuat' if scores['fundamental_score'] > 70 else 'sedang'}.
    Investor cocok: { 'Short-term trader' if final_score > 80 else 'Long-term investor' if final_score > 60 else 'Observer' }.
    
    **Outlook**:
    - Short-term: { 'Positif' if indicators.get('rsi', 50) < 70 else 'Hati-hati' }
    - Long-term: { 'Baik' if scores['fundamental_score'] > 70 else 'Waspada' }
    """
    
    return analysis
