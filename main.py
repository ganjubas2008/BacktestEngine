import os
import random
import pandas as pd
from src.util import Action, BaseAction, read_bbo
from src.simulate import Simulate
from src.metrics import TradingMetrics
from src.strategies import generate_random_actions, generate_cheating_actions
from src.candles import make_candles, plot_candles, Candle

def show_trading_metrics(trading_metrics, bbo_data):
    """
    Prints various trading metrics including Sharpe ratio, sortino ratio, 
    average holding time, traded volume, total PnL, and maximum PnL drawdown.

    Args:
        trading_metrics (TradingMetrics): Instance of TradingMetrics containing the trading history.
        bbo_data (dict): Best Bid Offer (BBO) data for each instrument.
    """
    print("Sharpe Ratio", trading_metrics.calculate_sharpe(market_data=bbo_data))
    print("Sortino Ratio:", trading_metrics.calculate_sortino(market_data=bbo_data))
    print("Average Holding Time:", trading_metrics.calculate_average_holding_time())
    print("Traded Volume:", trading_metrics.calculate_traded_volume())
    print("Total PnL:", trading_metrics.calculate_total_pnl())
    print("Max PnL Drawdown:", trading_metrics.calculate_max_drawdown())
    
    
def test_cheating_strategy(info=None):
    """
    Tests a strategy that generates actions based on candle patterns 
    to exploit predictable price movements.

    Args:
        info (str): Optional string to display information about the test.
    """
    print(info)
    
    # Read market data (BBO) from CSV files
    bbo_data = read_bbo()
    
    # Determine the start and end timestamps for the BBO data
    time_start = bbo_data['DOGE']['local_timestamp'].min()
    time_end = bbo_data['DOGE']['local_timestamp'].max()

    # File paths to trades data
    path_trades_doge = os.getenv('PATH_TRADES_DOGE')
    path_trades_pepe = os.getenv('PATH_TRADES_PEPE')

    # Read trades data for DOGE and PEPE
    trades_doge = pd.read_csv(path_trades_doge)
    trades_pepe = pd.read_csv(path_trades_pepe)

    # Generate candle data (with 1-hour candles) for both instruments
    candles_doge = make_candles(trades=trades_doge, candle_duration_ms=1000 * 60 * 60)
    candles_pepe = make_candles(trades=trades_pepe, candle_duration_ms=1000 * 60 * 60)
    candles = {'DOGE': candles_doge, 'PEPE': candles_pepe}
    
    # Generate "cheating" actions based on candle patterns
    actions = generate_cheating_actions(candles=candles, time_start=time_start, time_end=time_end)
    
    # Run the simulation
    simulation = Simulate(actions=actions, action_duration=10000)
    result = simulation.backtest(bbo_data=bbo_data)

    # Analyze the simulation history using TradingMetrics
    history = result['history']
    tm = TradingMetrics(history)
    
    # Show trading metrics
    show_trading_metrics(tm, bbo_data)


def test_random_strategy(info=None):
    """
    Tests a strategy that generates random actions (buy/sell) for 
    the DOGE and PEPE instruments within a given time period.

    Args:
        info (str): Optional string to display information about the test.
    """
    print(info)
    
    # Read market data (BBO) from CSV files
    bbo_data = read_bbo()
    
    # Determine the start and end timestamps for the BBO data
    time_start = bbo_data['DOGE']['local_timestamp'].min()
    time_end = bbo_data['DOGE']['local_timestamp'].max()

    # Generate random actions
    actions = generate_random_actions(time_start=time_start, time_end=time_end)
    
    # Run the simulation
    simulation = Simulate(actions=actions, action_duration=1000)
    result = simulation.backtest(bbo_data=bbo_data)

    # Analyze the simulation history using TradingMetrics
    history = result['history']
    tm = TradingMetrics(history)
    
    # Show trading metrics
    show_trading_metrics(tm, bbo_data)    


if __name__ == "__main__":
    """
    The main entry point for the script. It runs two test strategies:
    1. A "cheating" strategy based on candle patterns.
    2. A random strategy that generates random trading actions.
    """
    # Run the cheating strategy test
    os.environ['PATH_BBO_DOGE'] = '~/WORK/ЦМФ/md_sim/bbo_dogeusdt.csv'
    os.environ['PATH_BBO_PEPE'] = '~/WORK/ЦМФ/md_sim/bbo_1000pepeusdt.csv'
    
    os.environ['PATH_TRADES_DOGE'] = '~/WORK/ЦМФ/md_sim/trades_dogeusdt.csv'
    os.environ['PATH_TRADES_PEPE'] = '~/WORK/ЦМФ/md_sim/trades_1000pepeusdt.csv'
    
    test_cheating_strategy("\nTESTING CHEATING STRATEGY:\n")
    
    # Run the random strategy test
    test_random_strategy("\nTESTING RANDOM STRATEGY:\n")
