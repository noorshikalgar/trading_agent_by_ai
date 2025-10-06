import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DataModule:
    """Fetch stock price data using yfinance (free, reliable)."""
    
    def __init__(self, watchlist: List[str]):
        self.watchlist = watchlist
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = 30  # seconds
    
    def get_current_prices(self) -> Dict[str, float]:
        """Fetch latest prices for all watchlist symbols."""
        prices = {}
        for symbol in self.watchlist:
            price = self._fetch_price(symbol)
            if price:
                prices[symbol] = price
        return prices
    
    def _fetch_price(self, symbol: str) -> Optional[float]:
        """Fetch single stock price with caching."""
        now = datetime.now()
        
        # Check cache
        if symbol in self.cache:
            cached_time, cached_price = self.cache[symbol]
            if (now - cached_time).seconds < self.cache_duration:
                return cached_price
        
        # Fetch fresh data
        try:
            ticker = yf.Ticker(symbol)
            # Get last available price (handles market closed gracefully)
            hist = ticker.history(period='1d', interval='1m')
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
                self.cache[symbol] = (now, price)
                return price
        except Exception as e:
            print(f"⚠️ Failed to fetch {symbol}: {e}")
        
        return None
    
    def get_historical_data(self, symbol: str, period: str = '1mo',
                           interval: str = '15m') -> pd.DataFrame:
        """Fetch historical data for indicator calculation."""
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            return df
        except Exception as e:
            print(f"⚠️ Historical data fetch failed for {symbol}: {e}")
            return pd.DataFrame()