import numpy as np
import pandas as pd

class TradingMetrics:
    """
    A class to calculate various trading metrics based on the trading history.
    
    Args:
        trading_history (dict): A dictionary containing the trading history, where the key is the timestamp, 
                                and the value is a dictionary with 'pnl_delta' and 'instrument_delta'.
    """
    
    def __init__(self, trading_history):
        self.trading_history = trading_history
        self.instruments = ['DOGE', 'PEPE']

    def calculate_total_pnl(self):
        """
        Calculates the total profit and loss (PnL) by summing all pnl_deltas from the trading history.
        
        Returns:
            float: The total PnL.
        """
        total_pnl = sum(trade['pnl_delta'] for trade in self.trading_history.values())
        return total_pnl

    def calculate_max_drawdown(self):
        """
        Calculates the maximum drawdown in PnL.
        The drawdown is defined as the maximum peak-to-trough decline in the portfolio's cumulative PnL.
        
        Returns:
            float: The maximum drawdown value.
        """
        pnl_history = []
        current_pnl = 0
        
        # Build a cumulative PnL history
        for trade in self.trading_history.values():
            current_pnl += trade['pnl_delta']
            pnl_history.append(current_pnl)

        # Calculate the drawdown by comparing peaks to subsequent troughs
        max_drawdown = 0
        peak_pnl = pnl_history[0]

        for pnl in pnl_history:
            if pnl > peak_pnl:
                peak_pnl = pnl
            drawdown = peak_pnl - pnl
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown

    def calculate_sortino(self, market_data, risk_free_rate=0):
        """
        Calculates the Sortino ratio, which is similar to the Sharpe ratio but focuses on downside risk.
        It uses only negative returns to measure volatility.
        
        Args:
            market_data (dict): Market data (BBO) for each instrument.
            risk_free_rate (float): The risk-free rate used in the calculation. Default is 0.
        
        Returns:
            dict: Sortino ratios for each instrument.
        """
        sortino_ratios = {}

        for instrument in self.instruments:
            history_df = pd.DataFrame.from_dict(self.trading_history, orient='index')
            history_df['timestamp'] = history_df.index
            history_df = history_df[history_df['instrument'] == instrument]
            
            if history_df.empty:
                sortino_ratios[instrument] = np.nan
                continue

            # Group PnL by day
            history_df['date'] = pd.to_datetime(history_df['timestamp'], unit='us').dt.date
            daily_pnl = history_df.groupby('date')['pnl_delta'].sum()

            returns = daily_pnl  # Daily PnL as returns
            negative_returns = returns[returns < 0]

            if len(negative_returns) == 0:
                sortino_ratios[instrument] = np.nan
                continue

            avg_return = np.mean(returns)
            std_negative_returns = np.std(negative_returns)

            sortino_ratios[instrument] = (avg_return - risk_free_rate) / std_negative_returns if std_negative_returns != 0 else np.nan

        return sortino_ratios

    def calculate_sharpe(self, market_data, risk_free_rate=0):
        """
        Calculates the Sharpe ratio, which measures the risk-adjusted return of the portfolio.
        It uses the standard deviation of all returns to assess volatility.
        
        Args:
            market_data (dict): Market data (BBO) for each instrument.
            risk_free_rate (float): The risk-free rate used in the calculation. Default is 0.
        
        Returns:
            dict: Sharpe ratios for each instrument.
        """
        sharpe_ratios = {}

        for instrument in self.instruments:
            history_df = pd.DataFrame.from_dict(self.trading_history, orient='index')
            history_df['timestamp'] = history_df.index
            history_df = history_df[history_df['instrument'] == instrument]

            if history_df.empty:
                sharpe_ratios[instrument] = np.nan
                continue

            # Group PnL by day
            history_df['date'] = pd.to_datetime(history_df['timestamp'], unit='us').dt.date
            daily_pnl = history_df.groupby('date')['pnl_delta'].sum()

            returns = daily_pnl  # Daily PnL as returns

            if len(returns) == 0:
                sharpe_ratios[instrument] = np.nan
                continue

            avg_return = np.mean(returns)
            std_returns = np.std(returns)

            sharpe_ratios[instrument] = (avg_return - risk_free_rate) / std_returns if std_returns != 0 else np.nan

        return sharpe_ratios

    def calculate_flips(self):
        """
        Calculates the number of times the portfolio "flips" from long to short or vice versa for each instrument.
        
        Returns:
            dict: Number of flips for each instrument.
        """
        flip_cnt = {instrument: 0 for instrument in self.instruments}
        portfolio = {instrument: 0 for instrument in self.instruments}
        
        for timestamp in self.trading_history.keys():
            for instrument in self.instruments:
                instrument_delta = self.trading_history[timestamp]['instrument_delta']
                if portfolio[instrument] * (portfolio[instrument] + instrument_delta) < 0:
                    flip_cnt[instrument] += 1
                portfolio[instrument] += instrument_delta

        return flip_cnt

    def calculate_traded_volume(self):
        """
        Calculates the total traded volume by summing the absolute value of all instrument deltas.
        
        Returns:
            dict: The traded volume for each instrument.
        """
        traded_volume = {instrument: 0 for instrument in self.instruments}
        
        for timestamp, trade in self.trading_history.items():
            instrument = trade['instrument']
            traded_volume[instrument] += abs(trade['instrument_delta'])

        return traded_volume

    def calculate_average_holding_time(self):
        """
        Calculates the average holding time of open positions for each instrument.
        
        Returns:
            dict: Average holding time for each instrument in microseconds.
        """
        holding_times = {instrument: [] for instrument in self.instruments}
        open_positions = {instrument: None for instrument in self.instruments}

        for timestamp, trade in self.trading_history.items():
            instrument = trade['instrument']
            instrument_delta = trade['instrument_delta']

            if open_positions[instrument] is None and instrument_delta != 0:
                open_positions[instrument] = timestamp  # Open position

            elif open_positions[instrument] is not None and instrument_delta == 0:
                close_time = timestamp  # Close position
                holding_time = close_time - open_positions[instrument]
                holding_times[instrument].append(holding_time)
                open_positions[instrument] = None  # Position closed

        # Calculate average holding time for each instrument
        avg_holding_time = {instrument: (np.mean(holding_times[instrument]) if holding_times[instrument] else np.nan)
                            for instrument in self.instruments}

        return avg_holding_time
