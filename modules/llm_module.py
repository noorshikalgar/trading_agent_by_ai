import ollama
from typing import Dict, Optional
import json


class LLMModule:
    """AI decision-making using local Ollama LLM."""

    def __init__(self, model: str = "llama3.2"):
        """
        Initialize Ollama client.

        Args:
            model: Ollama model name (llama3.2, mistral, phi3, etc.)
        """
        self.model = model
        self._test_connection()

    def _test_connection(self):
        """Test if Ollama is running."""
        try:
            ollama.list()
            print(f"✅ Ollama connected - using model: {self.model}")
        except Exception as e:
            print(f"⚠️ Ollama not running. Start with: ollama serve")
            print(f"   Then pull model: ollama pull {self.model}")

    def analyze_trade(self, symbol: str, current_price: float,
                      indicators: Dict, holdings: Dict,
                      recent_trades: list) -> tuple[str, str]:
        """
        Use LLM to decide trade action based on context.

        Returns: (action, reason) where action is 'buy'/'sell'/'hold'
        """
        if not indicators:
            return 'hold', 'Insufficient data'

        # Build context prompt
        prompt = self._build_prompt(symbol, current_price, indicators,
                                    holdings, recent_trades)

        try:
            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0.3,  # Lower = more conservative
                    'num_predict': 150  # Limit response length
                }
            )

            # Parse LLM response
            content = response['message']['content'].strip()
            action, reason = self._parse_response(content)

            return action, reason

        except Exception as e:
            print(f"❌ LLM error: {e}")
            return 'hold', f'LLM error: {str(e)}'

    def _build_prompt(self, symbol: str, price: float, indicators: Dict,
                      holdings: Dict, recent_trades: list) -> str:
        """Build trading decision prompt."""

        has_position = symbol in holdings
        position_info = ""
        if has_position:
            pos = holdings[symbol]
            position_info = f"\n- Current Position: {pos['quantity']} shares @ ₹{pos['avg_price']:.2f}"

        recent_trades_str = ""
        if recent_trades:
            last_3 = recent_trades[-3:]
            recent_trades_str = "\n".join([
                f"  {t['action']} {t['symbol']} @ ₹{t['price']:.2f} - {t['reason']}"
                for t in last_3
            ])

        prompt = f"""You are an expert stock trader. Analyze this data and decide: BUY, SELL, or HOLD.

Stock: {symbol}
Current Price: ₹{price:.2f}

Technical Indicators:
- Short MA (5-period): {indicators.get('ma_short', 0):.2f}
- Long MA (20-period): {indicators.get('ma_long', 0):.2f}
- RSI (14-period): {indicators.get('rsi', 0):.1f}
- Previous Short MA: {indicators.get('ma_short_prev', 0):.2f}
- Previous Long MA: {indicators.get('ma_long_prev', 0):.2f}
{position_info}

Recent Trade History:
{recent_trades_str if recent_trades_str else "  No recent trades"}

**Rules:**
1. If you don't own the stock, consider BUY if:
   - MA crossover (short crosses above long) + RSI < 50
   - RSI < 30 (oversold)
2. If you own the stock, consider SELL if:
   - MA crossover (short crosses below long)
   - RSI > 70 (overbought)
   - Profit target met
3. Otherwise HOLD

Respond ONLY in this exact format:
ACTION: <BUY|SELL|HOLD>
REASON: <brief explanation in one line>"""

        return prompt

    def _parse_response(self, content: str) -> tuple[str, str]:
        """Parse LLM response into action and reason."""
        action = 'hold'
        reason = 'Could not parse LLM response'

        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('ACTION:'):
                action_str = line.replace('ACTION:', '').strip().lower()
                if action_str in ['buy', 'sell', 'hold']:
                    action = action_str
            elif line.startswith('REASON:'):
                reason = line.replace('REASON:', '').strip()

        return action, f"[LLM] {reason}"