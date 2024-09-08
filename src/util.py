import os
import pandas as pd

class BaseAction:
    """
    Represents a basic trading action, which includes an instrument and the amount to trade.
    
    Args:
        instrument (str): The name of the instrument (e.g., 'DOGE', 'PEPE').
        amount (float): The amount to trade (can be positive for buy, negative for sell).
    """
    def __init__(self, instrument, amount):
        self.instrument = instrument  # Name of the instrument (e.g., 'DOGE', 'PEPE')
        self.amount = amount  # Amount to trade (positive for buy, negative for sell)
    

class Action:
    """
    Represents a timestamped trading action, which can consist of multiple base actions.
    
    Args:
        timestamp (int): The time at which the action occurs (in microseconds).
        base_actions (list): A list of BaseAction objects representing the trades to perform.
    """
    def __init__(self, timestamp, base_actions):
        self.timestamp = timestamp  # The time at which the action occurs
        self.base_actions = base_actions  # List of BaseAction instances


def binary_search_next_trade(trades, target_time):
    """
    Performs a binary search to find the index of the next trade after the target timestamp.

    Args:
        trades (pd.DataFrame): A DataFrame of trades sorted by 'local_timestamp'.
        target_time (int): The target timestamp to find the next trade after.

    Returns:
        int: The index of the next trade after the target time.
    """
    left, right = 0, len(trades) - 1

    while left <= right:
        mid = (left + right) // 2
        mid_time = trades.iloc[mid]['local_timestamp']
        
        if mid_time > target_time:
            right = mid - 1
        else:
            left = mid + 1

    return left  # Return the index of the next trade


def read_bbo():
    """
    Reads the Best Bid Offer (BBO) data for DOGE and PEPE from CSV files, sorts them by 'local_timestamp',
    and returns the data in a dictionary.

    Args:
        path_bbo_doge (str): The file path to the DOGE BBO CSV data.
        path_bbo_pepe (str): The file path to the PEPE BBO CSV data.

    Returns:
        dict: A dictionary containing the sorted BBO data for both DOGE and PEPE.
    """
    path_bbo_doge = os.getenv('PATH_BBO_DOGE')
    path_bbo_pepe = os.getenv('PATH_BBO_PEPE')
    bbo_doge = pd.read_csv(path_bbo_doge)
    bbo_pepe = pd.read_csv(path_bbo_pepe)

    # Store BBO data in a dictionary and sort by timestamp for each instrument
    bbo_data = {'DOGE': bbo_doge, 'PEPE': bbo_pepe}

    bbo_data['DOGE'].sort_values(by='local_timestamp', inplace=True)
    bbo_data['PEPE'].sort_values(by='local_timestamp', inplace=True)
    
    return bbo_data
