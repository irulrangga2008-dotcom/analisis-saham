# Data configuration
DATA_PERIOD = 365 * 2  # 2 years
CACHE_TTL = 300  # 5 minutes
REFRESH_INTERVAL = 60  # seconds

# Technical indicators
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
VOLUME_CONFIRMATION_THRESHOLD = 1.2

# Scoring thresholds
PE_GOOD = 15
PBV_GOOD = 2.0
ROE_GOOD = 0.15

SCORE_THRESHOLDS = {
    'strong_buy': 80,
    'buy': 65,
    'hold': 50
}
