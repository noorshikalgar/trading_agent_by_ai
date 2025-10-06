from flask import Flask, render_template, jsonify, request
import threading
from datetime import datetime

from config import *
from modules.data_module import DataModule
from modules.strategy_module import StrategyModule
from modules.execution_module import ExecutionModule
from modules.persistence_module import PersistenceModule
from modules.scheduler_module import SchedulerModule
from modules.llm_module import LLMModule  # ADD THIS LINE
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize modules
data_module = DataModule(WATCHLIST)
strategy_module = StrategyModule()
execution_module = ExecutionModule()
persistence_module = PersistenceModule(STATE_FILE)

# Global state
state = persistence_module.load_state()
scheduler = None
logs = []

def add_log(message: str):
    """Add timestamped log message."""
    timestamp = datetime.now().strftime('%H:%M:%S')
    logs.append(f"[{timestamp}] {message}")
    if len(logs) > 100:  # Keep last 100 logs
        logs.pop(0)
    print(message)


# ADD THESE LINES:
if USE_LLM:
    llm_module = LLMModule(LLM_MODEL)
    add_log(f"🤖 LLM Module initialized with {LLM_MODEL}")
else:
    llm_module = None
    add_log("📊 Using traditional strategy (no LLM)")





def agent_tick():
    """Main agent logic executed each tick."""
    add_log("🔄 Tick started")
    
    # 1. Fetch current prices
    prices = data_module.get_current_prices()
    if not prices:
        add_log("⚠️ No price data available")
        return
    
    state['last_prices'] = prices
    add_log(f"📊 Fetched prices: {len(prices)} symbols")
    
    # 2. Process each symbol
    for symbol in WATCHLIST:
        if symbol not in prices:
            continue
        
        current_price = prices[symbol]
        
        # Get historical data for indicators
        hist_data = data_module.get_historical_data(symbol)
        if hist_data.empty:
            continue
        
        # # Calculate indicators
        # indicators = strategy_module.calculate_indicators(hist_data)
        # state['indicators'][symbol] = indicators
        #
        # # Decide action
        # action, reason = strategy_module.decide_action(
        #     symbol, current_price, indicators, state['holdings']
        # )

        # Calculate indicators
        indicators = strategy_module.calculate_indicators(hist_data)
        state['indicators'][symbol] = indicators

        # Decide action (LLM or traditional)
        if USE_LLM and llm_module:
            action, reason = llm_module.analyze_trade(
                symbol, current_price, indicators,
                state['holdings'], state['trades']
            )
        else:
            action, reason = strategy_module.decide_action(
                symbol, current_price, indicators, state['holdings']
            )
        
        # Execute trade if not hold
        if action == 'buy':
            trade = execution_module.execute_buy(
                symbol, current_price, state['cash'],
                state['holdings'], reason
            )
            if trade:
                state['cash'] -= trade['total']
                state['trades'].append(trade)
                add_log(f"✅ BUY {symbol}: {trade['quantity']} @ "
                       f"₹{current_price:.2f} | {reason}")
            else:
                add_log(f"⚠️ BUY {symbol} failed (insufficient funds/positions)")
        
        elif action == 'sell':
            trade = execution_module.execute_sell(
                symbol, current_price, state['holdings'], reason
            )
            if trade:
                state['cash'] += trade['total']
                state['trades'].append(trade)
                pl_emoji = '🟢' if trade['profit_loss'] > 0 else '🔴'
                add_log(f"{pl_emoji} SELL {symbol}: {trade['quantity']} @ "
                       f"₹{current_price:.2f} | P/L: ₹{trade['profit_loss']:.2f}")
    
    # 3. Save state
    persistence_module.save_state(state)
    add_log(f"💾 State saved | Cash: ₹{state['cash']:.2f}")

# ===== API ENDPOINTS =====

@app.route('/')
def index():
    """Serve dashboard UI."""
    return render_template('index.html')

@app.route('/api/status')
def api_status():
    """Return current state as JSON."""
    portfolio = execution_module.calculate_portfolio_value(
        state['cash'], state['holdings'], state.get('last_prices', {})
    )
    
    return jsonify({
        'status': state['status'],
        'portfolio': portfolio,
        'holdings': [
            {
                'symbol': sym,
                'quantity': info['quantity'],
                'avg_price': info['avg_price'],
                'current_price': state.get('last_prices', {}).get(sym, 0),
                'value': info['quantity'] * state.get('last_prices', {}).get(
                    sym, info['avg_price']
                ),
                'pl': (info['quantity'] *
                      (state.get('last_prices', {}).get(sym, info['avg_price'])
                       - info['avg_price']))
            }
            for sym, info in state['holdings'].items()
        ],
        'recent_trades': state['trades'][-10:][::-1],  # Last 10, newest first
        'watchlist': WATCHLIST,
        'market_hours': f"{MARKET_OPEN} - {MARKET_CLOSE}"
    })

@app.route('/api/logs')
def api_logs():
    """Return recent log messages."""
    return jsonify({'logs': logs[-50:][::-1]})  # Last 50, newest first

@app.route('/api/control', methods=['POST'])
def api_control():
    """Handle start/pause/stop commands."""
    global scheduler
    
    action = request.json.get('action')
    
    if action == 'start':
        if state['status'] == 'stopped':
            state['status'] = 'running'
            scheduler = SchedulerModule(agent_tick)
            thread = threading.Thread(target=scheduler.start, daemon=True)
            thread.start()
            add_log("🚀 Agent started")
            return jsonify({'success': True, 'message': 'Agent started'})
        elif state['status'] == 'paused':
            state['status'] = 'running'
            scheduler.resume()
            return jsonify({'success': True, 'message': 'Agent resumed'})
        else:
            return jsonify({'success': False, 'message': 'Already running'})
    
    elif action == 'pause':
        if state['status'] == 'running' and scheduler:
            state['status'] = 'paused'
            scheduler.pause()
            persistence_module.save_state(state)
            return jsonify({'success': True, 'message': 'Agent paused'})
        else:
            return jsonify({'success': False, 'message': 'Not running'})
    
    elif action == 'stop':
        if scheduler and state['status'] in ['running', 'paused']:
            state['status'] = 'stopped'
            scheduler.stop()
            persistence_module.save_state(state)
            add_log("⏹️ Agent stopped")
            return jsonify({'success': True, 'message': 'Agent stopped'})
        else:
            return jsonify({'success': False, 'message': 'Already stopped'})
    
    return jsonify({'success': False, 'message': 'Invalid action'})

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 AI TRADING AGENT")
    print("=" * 60)
    print(f"📊 Watchlist: {', '.join(WATCHLIST)}")
    print(f"💰 Initial Capital: ₹{INITIAL_CASH:,.2f}")
    print(f"⏰ Market Hours: {MARKET_OPEN} - {MARKET_CLOSE}")
    print(f"🔄 Tick Interval: {TICK_INTERVAL_SECONDS}s")
    print("=" * 60)
    print("\n🌐 Open http://localhost:5000 in your browser\n")
    
    app.run(debug=True, use_reloader=False)