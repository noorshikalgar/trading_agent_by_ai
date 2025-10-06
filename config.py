import os
from datetime import time

# API Configuration
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'demo')
# Get free key at: https://www.alphavantage.co/support/#api-key

# Trading Configuration
MARKET_OPEN = time(9, 15)   # 09:15 AM
MARKET_CLOSE = time(15, 30)  # 03:30 PM
TICK_INTERVAL_SECONDS = 60   # Check every 60 seconds

# Portfolio Configuration
INITIAL_CASH = 100000.0      # Starting capital (₹1 lakh)
POSITION_SIZE = 0.1          # Use 10% of capital per trade
MAX_POSITIONS = 5            # Max concurrent holdings

# Strategy Configuration (Simple MA + RSI)
MA_SHORT_PERIOD = 5
MA_LONG_PERIOD = 20
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

# Watchlist (stocks to trade)
WATCHLIST = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS']
# Use .NS suffix for NSE stocks in yfinance

# Persistence
STATE_FILE = 'data/state.json'

# LLM Configuration
USE_LLM = True  # Set to False to use traditional strategy
LLM_MODEL = "mistral"  # Options: llama3.2, mistral, phi3, gemma2