import random
import pandas as pd
from src.util import Action, BaseAction, read_bbo
from src.simulate import Simulate
from src.metrics import TradingMetrics
from src.candles import make_candles, Candle 

def generate_random_actions(time_start=None, time_end=None, N=100):
    """
    Generates a random sequence of N actions (buy/sell) over the specified time period.

    Args:
        time_start (int): Start timestamp for the random actions.
        time_end (int): End timestamp for the random actions.
        N (int): Number of random actions to generate.

    Returns:
        list: List of random trading actions.
    """
    time_stop = time_end - 1e3 * 1e3 * 60  # Stop generating random actions 1 minute before the end

    dt = (time_stop - time_start) / N  # Time interval between actions
    instruments = ['DOGE', 'PEPE']
    total = dict(zip(instruments, [0] * len(instruments)))  # To track open positions
    actions = []

    for i in range(N):
        amount = random.randint(-1000, 1000)
        instrument = instruments[random.randint(0, 1)]
        actions.append(Action(timestamp=time_start + i * dt,
                              base_actions=[BaseAction(instrument=instrument, amount=amount)]))

        total[instrument] += amount  # Track the position

    # Add actions to close all open positions at the end
    for instrument in instruments:
        actions.append(Action(timestamp=time_stop,
                              base_actions=[BaseAction(instrument=instrument, amount=-total[instrument])]))

    return actions


def generate_cheating_actions(candles, time_start=None, time_end=None):
    """
    Generates trading actions based on future knowledge to exploit price movements.

    Args:
        candles (dict): Candle data for each instrument.
        time_start (int): Start timestamp for the actions.
        time_end (int): End timestamp for the actions.

    Returns:
        list: List of trading actions.
    """
    actions = []
    instruments = candles.keys()
    CONST_AMOUNT = 1000  # Fixed amount to trade for each action

    for instrument in instruments:
        for candle in candles[instrument]:
            # Only take actions within the specified time range
            if candle.time_end < time_end - 1000 * 1000 * 60 and candle.time_start > time_start + 1000 * 1000 * 60:
                sign = (-1) ** (candle.body_open > candle.body_close)  # Determine buy/sell based on candle pattern
                actions.append(Action(timestamp=candle.time_start,
                                      base_actions=[BaseAction(instrument=instrument, amount=CONST_AMOUNT * sign)]))
                actions.append(Action(timestamp=candle.time_end,
                                      base_actions=[BaseAction(instrument=instrument, amount=CONST_AMOUNT * -sign)]))

    return actions
