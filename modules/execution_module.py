from datetime import datetime
from typing import Dict, List, Optional
from config import POSITION_SIZE, MAX_POSITIONS

class ExecutionModule:
    """Simulates trade execution and manages portfolio."""
    
    def __init__(self):
        pass
    
    def execute_buy(self, symbol: str, price: float, cash: float,
                   holdings: Dict, reason: str) -> Optional[Dict]:
        """
        Simulate buy order.
        
        Returns trade dict if successful, None if failed.
        """
        # Check if we can afford and have room for more positions
        if len(holdings) >= MAX_POSITIONS:
            return None
        
        # Calculate quantity based on position sizing
        invest_amount = cash * POSITION_SIZE
        if invest_amount < price:
            return None  # Can't afford even 1 share
        
        quantity = int(invest_amount / price)
        if quantity == 0:
            return None
        
        total_cost = quantity * price
        
        # Update holdings
        if symbol in holdings:
            # Average down
            old_qty = holdings[symbol]['quantity']
            old_avg = holdings[symbol]['avg_price']
            new_qty = old_qty + quantity
            new_avg = ((old_qty * old_avg) + total_cost) / new_qty
            holdings[symbol] = {'quantity': new_qty, 'avg_price': new_avg}
        else:
            holdings[symbol] = {'quantity': quantity, 'avg_price': price}
        
        # Create trade record
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': 'BUY',
            'quantity': quantity,
            'price': price,
            'total': total_cost,
            'reason': reason
        }
        
        return trade
    
    def execute_sell(self, symbol: str, price: float, holdings: Dict,
                    reason: str) -> Optional[Dict]:
        """
        Simulate sell order (sell entire position).
        
        Returns trade dict if successful, None if failed.
        """
        if symbol not in holdings:
            return None
        
        quantity = holdings[symbol]['quantity']
        avg_price = holdings[symbol]['avg_price']
        total_value = quantity * price
        profit_loss = total_value - (quantity * avg_price)
        
        # Remove from holdings
        del holdings[symbol]
        
        # Create trade record
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': 'SELL',
            'quantity': quantity,
            'price': price,
            'total': total_value,
            'profit_loss': profit_loss,
            'reason': reason
        }
        
        return trade
    
    def calculate_portfolio_value(self, cash: float, holdings: Dict,
                                 current_prices: Dict) -> Dict:
        """Calculate current portfolio metrics."""
        holdings_value = 0.0
        unrealized_pl = 0.0
        
        for symbol, position in holdings.items():
            current_price = current_prices.get(symbol, position['avg_price'])
            market_value = position['quantity'] * current_price
            cost_basis = position['quantity'] * position['avg_price']
            holdings_value += market_value
            unrealized_pl += (market_value - cost_basis)
        
        return {
            'cash': cash,
            'holdings_value': holdings_value,
            'total_value': cash + holdings_value,
            'unrealized_pl': unrealized_pl
        }