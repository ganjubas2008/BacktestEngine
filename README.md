
# BacktestEngine: A Trading Strategy Backtester and Simulator

**BacktestEngine** is a Python-based trading strategy backtesting framework. It allows users to simulate various trading strategies, analyze their performance, and calculate critical trading metrics like Sharpe ratio, Shortino ratio, total PnL, and maximum drawdown. The project supports custom strategy generation, including random actions and pattern-based (candle) strategies, with built-in data management for historical trade data.

## Features

- **Simulate trading strategies**: Perform backtests on historical market data.
- **Generate trading actions**: Supports both random and pattern-based (candle) strategies.
- **Analyze trading performance**: Calculate Sharpe ratio, Shortino ratio, max drawdown, total PnL, and more.
- **Works with real historical data**: Load trade and BBO (Best Bid Offer) data from CSV files.
- **Customizable**: Modify and add your own strategies for backtesting.

## Project Structure

- **`main.py`**: The entry point of the project. This file runs the strategy tests and prints the results.
- **`simulate.py`**: Contains the core simulation engine that executes the trades based on provided actions and calculates PnL.
- **`strategies.py`**: Generates random or candle-based trading actions for simulation.
- **`metrics.py`**: Calculates various trading metrics like Sharpe ratio, Shortino ratio, total PnL, and maximum drawdown.
- **`util.py`**: Contains helper functions like reading BBO data and a binary search to find the next trade.

## Installation

  Clone the repository:
    ```bash
    git clone https://github.com/your-username/BacktestEngine.git
    cd BacktestEngine
    ```

## Usage

### 1. Run the project

You can execute the project directly by running:

```bash
python main.py
```

### 2. Set the paths for your trade data

In `main.py`, the paths for trade data files are set as environment variables in the `__main__` block. By default, they are set to:

```python
os.environ['PATH_TRADES_DOGE'] = 'md_sim/trades_dogeusdt.csv'
os.environ['PATH_TRADES_PEPE'] = 'md_sim/trades_1000pepeusdt.csv'
```

You can adjust these paths according to the location of your CSV files.

### 3. Run Cheating and Random Strategies

Two main strategies are implemented:
- **Cheating strategy**: Uses candle patterns to predict trades.
- **Random strategy**: Randomly generates buy/sell trades.

Both strategies are run from `main.py`:
```python
test_cheating_strategy("
TESTING CHEATING STRATEGY:
")
test_random_strategy("
TESTING RANDOM STRATEGY:
")
```

### 4. Analyze Trading Metrics

The simulation provides detailed metrics after each backtest, including:
- **Sharpe Ratio**
- **Shortino Ratio**
- **Total PnL**
- **Maximum Drawdown**
- **Traded Volume**
- **Average Holding Time**

Example output:
```
Sharpe Ratio: 1.253
Shortino Ratio: 0.874
Total PnL: 105.32
Max PnL Drawdown: -35.60
```

## Customization

1. **Add Custom Strategies**:
    You can create new strategies by modifying or adding functions in `strategies.py`. For example, you can implement a momentum-based or moving-average-based strategy.

2. **Add New Metrics**:
    Add new trading metrics by extending the `TradingMetrics` class in `metrics.py`.

## Folder Structure

```
BacktestEngine/
│
├── md_sim/               # Folder containing the CSV files for DOGE and PEPE
│   ├── bbo_dogeusdt.csv  # BBO data for DOGE
│   └── trades_dogeusdt.csv  # Historical trade data for DOGE
│
├── candles.py            # Handles the creation of candles for the cheating strategy
├── main.py               # Main entry point, runs tests on strategies
├── metrics.py            # Calculates various trading metrics
├── simulate.py           # Simulates trading actions and computes PnL
├── strategies.py         # Generates random or pattern-based trading actions
├── util.py               # Utility functions for reading data and binary search
└── README.md             # This file
```

## Contributing

Feel free to fork the project, create a pull request, or submit issues. Any contribution is appreciated.

## License

This project is licensed under the MIT License.

---

### Example CSV Data

Here’s an example of what the BBO data should look like (saved as `bbo_dogeusdt.csv`):

```
local_timestamp,ask_amount,ask_price,bid_price,bid_amount
1723248002491221,6702.0,0.10379,0.10378,168898.0
1723248002964927,45492.0,0.10379,0.10378,151776.0
...
```

Similarly, for `trades_dogeusdt.csv`:

```
local_timestamp,side,price,amount
1723248002453757,buy,0.008519,748
1723248002466531,sell,0.008519,1944
...
```
