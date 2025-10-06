import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from typing import Dict, Tuple, Optional
from config import (MA_SHORT_PERIOD, MA_LONG_PERIOD, RSI_PERIOD,
                    RSI_OVERSOLD, RSI_OVERBOUGHT)

class StrategyModule:
    """Trading strategy: MA Crossover + RSI confirmation."""
    
    def __init__(self):
        self.indicators_cache = {}
    
    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate MA and RSI from price data."""
        if df.empty or len(df) < MA_LONG_PERIOD:
            return {}
        
        close = df['Close']
        
        # Moving Averages
        ma_short = SMAIndicator(close, window=MA_SHORT_PERIOD).sma_indicator()
        ma_long = SMAIndicator(close, window=MA_LONG_PERIOD).sma_indicator()
        
        # RSI
        rsi = RSIIndicator(close, window=RSI_PERIOD).rsi()
        
        return {
            'ma_short': float(ma_short.iloc[-1]),
            'ma_long': float(ma_long.iloc[-1]),
            'rsi': float(rsi.iloc[-1]),
            'ma_short_prev': float(ma_short.iloc[-2]),
            'ma_long_prev': float(ma_long.iloc[-2])
        }
    
    def decide_action(self, symbol: str, current_price: float,
                     indicators: Dict[str, float],
                     holdings: Dict) -> Tuple[str, str]:
        """
        Decide action based on strategy rules.
        
        Returns: (action, reason) where action is 'buy'/'sell'/'hold'
        """
        if not indicators:
            return 'hold', 'Insufficient data for indicators'
        
        ma_short = indicators.get('ma_short')
        ma_long = indicators.get('ma_long')
        ma_short_prev = indicators.get('ma_short_prev')
        ma_long_prev = indicators.get('ma_long_prev')
        rsi = indicators.get('rsi')
        
        if None in [ma_short, ma_long, ma_short_prev, ma_long_prev, rsi]:
            return 'hold', 'Incomplete indicator data'
        
        # Check if we already hold this stock
        has_position = symbol in holdings
        
        # BUY SIGNAL: MA crossover (short crosses above long) + RSI oversold
        if not has_position:
            if ma_short_prev <= ma_long_prev and ma_short > ma_long:
                if rsi < 50:  # Relaxed RSI condition
                    return 'buy', (f'MA crossover (↑) @ {current_price:.2f}, '
                                  f'RSI={rsi:.1f}')
            
            # Alternative: Strong oversold signal
            if rsi < RSI_OVERSOLD:
                return 'buy', f'RSI oversold ({rsi:.1f}) @ {current_price:.2f}'
        
        # SELL SIGNAL: MA crossover (short crosses below long) OR RSI overbought
        else:
            if ma_short_prev >= ma_long_prev and ma_short < ma_long:
                return 'sell', (f'MA crossover (↓) @ {current_price:.2f}, '
                               f'RSI={rsi:.1f}')
            
            if rsi > RSI_OVERBOUGHT:
                return 'sell', f'RSI overbought ({rsi:.1f}) @ {current_price:.2f}'
        
        return 'hold', f'No signal (RSI={rsi:.1f}, MA diff={ma_short-ma_long:.2f})'