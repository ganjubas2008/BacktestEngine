from src.util import Action, BaseAction, binary_search_next_trade, read_bbo
from collections import OrderedDict
import pandas as pd

def perform_base_action(timestamp, base_action, bbo_data, duration):
    """
    Executes a base action (buy or sell) for a given instrument over a specified duration.

    Args:
        timestamp (int): The start time of the action.
        base_action (BaseAction): The action to perform, containing instrument and amount.
        bbo_data (pd.DataFrame): Best Bid Offer (BBO) data for the instrument.
        duration (int): The duration over which the action will be executed (in microseconds).

    Returns:
        dict: Contains instrument_delta (how much of the instrument was traded) and pnl_delta (profit or loss).
    """
    pnl_delta = 0
    instrument_delta = 0
    amount = base_action.amount

    # Find the index of the first trade that occurs after the timestamp
    idx = binary_search_next_trade(bbo_data, timestamp)
    if not idx:
        idx = bbo_data.shape[0] - 1
        
    cur_timestamp = bbo_data.iloc[idx].local_timestamp

    # Process trades within the duration limit and while there's remaining amount to trade
    while cur_timestamp < timestamp + duration and abs(base_action.amount) > 0 and idx < bbo_data.shape[0]:
        row = bbo_data.iloc[idx]
        cur_timestamp = row.local_timestamp

        # Handle buy orders
        if base_action.amount > 0:
            amount = min(row.ask_amount, base_action.amount)
        
        # Handle sell orders
        if base_action.amount < 0:
            amount = max(-row.bid_amount, base_action.amount)

        base_action.amount -= amount
        instrument_delta += amount
        pnl_delta -= row.ask_price * amount
        
        idx += 1

    return {'instrument_delta': instrument_delta, 'pnl_delta': pnl_delta}


class Simulate:
    """
    Simulates the execution of trading actions over time and calculates portfolio performance.
    """

    def __init__(self, actions, action_duration, verbose=False):
        """
        Initializes the simulation.

        Args:
            actions (list): List of trading actions (buy/sell) to simulate.
            action_duration (int): Duration of each action in milliseconds.
            verbose (bool): If True, prints information about each action.
        """
        self.actions = actions
        self.pnl = None
        self.traded_volume = 0
        self.verbose = verbose
        self.portfolio = {'DOGE': 0, 'PEPE': 0}  # Tracks the portfolio for each instrument
        self.pnl = 0
        self.action_duration = action_duration * 1000  # Convert to microseconds
        self.history = OrderedDict()  # Stores the history of executed actions

    def backtest(self, bbo_data):
        """
        Executes all actions in sequence and simulates their effect on the portfolio.

        Args:
            bbo_data (dict): Market data (BBO) for each instrument.

        Returns:
            dict: Contains final PnL, open positions, and the history of trades.
        """
        self.actions.sort(key=lambda action: action.timestamp)

        for action in self.actions:
            timestamp = action.timestamp
            for base_action in action.base_actions:
                instrument = base_action.instrument
                result = perform_base_action(timestamp=timestamp,
                                             base_action=base_action,
                                             bbo_data=bbo_data[instrument],
                                             duration=self.action_duration)

                pnl_delta = result['pnl_delta']
                instrument_delta = result['instrument_delta']

                # Update PnL and portfolio
                self.pnl += pnl_delta
                self.portfolio[instrument] += instrument_delta

                # Store the action's result in history
                self.history[timestamp] = {'instrument': instrument, 'pnl_delta': pnl_delta, 'instrument_delta': instrument_delta}

                if self.verbose:
                    print(f'Performed action: {instrument_delta} {instrument}')
        
        return {'pnl': self.pnl, 'open_positions': self.portfolio, 'history': self.history}
