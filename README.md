# AI Trading Agent

🤖 **AI Trading Agent** is an automated trading system that uses a combination of traditional technical analysis strategies and AI-powered decision-making to trade stocks. The system is built with Python and Flask, providing a web-based dashboard for monitoring and controlling the trading agent.

## Features

- **Technical Analysis**: Implements Moving Average (MA) Crossover and Relative Strength Index (RSI) strategies.
- **AI-Powered Decisions**: Optionally integrates with an LLM (Large Language Model) for advanced trade decision-making.
- **Real-Time Data**: Fetches live stock prices and historical data using `yfinance`.
- **Portfolio Management**: Simulates trade execution, tracks holdings, and calculates portfolio metrics.
- **Web Dashboard**: Interactive UI for monitoring portfolio, viewing logs, and controlling the agent.
- **Persistence**: Saves and loads agent state to/from disk for continuity.

## Project Structure

```text
.
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates for the web dashboard
├── static/                # Static assets (CSS, JS)
├── modules/               # Core modules for the trading agent
│   ├── data_module.py     # Fetches stock price data
│   ├── strategy_module.py # Implements trading strategies
│   ├── execution_module.py# Simulates trade execution
│   ├── persistence_module.py # Handles state persistence
│   ├── scheduler_module.py   # Manages agent timing and market hours
│   └── llm_module.py      # AI decision-making using LLM
├── data/                  # Directory for saved state
└── .env                   # Environment variables (e.g., API keys)
```

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/ai-trading-agent.git
   cd ai-trading-agent
   ```

2. **Set Up Environment**:
   Create a `.env` file with your API key:

   ```text
   ALPHA_VANTAGE_KEY=your_alpha_vantage_api_key
   ```

3. **Install Dependencies**:
   Use `pip` to install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   Start the Flask server:

   ```bash
   python app.py
   ```

5. **Access the Dashboard**:
   Open your browser and navigate to [http://localhost:5000](http://localhost:5000).

## Configuration

All configuration settings are defined in `config.py`. Key settings include:

- **Market Hours**: `MARKET_OPEN` and `MARKET_CLOSE`
- **Trading Strategy**: MA and RSI parameters
- **Portfolio Settings**: Initial cash, position size, and max positions
- **LLM Integration**: Enable/disable AI decision-making with `USE_LLM`

## Usage

- **Start the Agent**: Use the "Start" button on the dashboard to begin trading.
- **Pause/Stop the Agent**: Control the agent's state using the "Pause" and "Stop" buttons.
- **Monitor Portfolio**: View cash balance, holdings, and unrealized P/L in real-time.
- **View Logs**: Check live logs for detailed activity.

## Dependencies

- **Backend**:
  - Flask
  - yfinance
  - pandas
  - numpy
  - ta (Technical Analysis library)
  - python-dotenv
  - ollama (for LLM integration)

- **Frontend**:
  - HTML, CSS, JavaScript

## License

This project is licensed under the [MIT License](LICENSE).

## Future Enhancements

- Add support for more advanced trading strategies.
- Integrate additional data sources for market analysis.
- Implement live trading with broker APIs.
- Enhance the AI decision-making model with more contextual data.

## Disclaimer

This project is for educational purposes only. It is not intended for live trading or financial advice. Use at your own risk.
