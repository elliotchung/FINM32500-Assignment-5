import pandas as pd


class Backtester:
    def __init__(self, strategy, broker):
        self.strategy = strategy
        self.broker = broker

    def run(self, prices: pd.Series):
        """
        Runs end-of-day backtest loop:
        - Compute signal for t-1
        - Trade at close t
        - Track cash, position, equity
        Returns a DataFrame with results
        """
        signals = self.strategy.signals(prices)
        cash_history = []
        position_history = []
        equity_history = []
        for i in range(len(prices)):
            price = prices.iloc[i]
            # Use signal from previous day (t-1)
            if i == 0:
                signal = 0  # No trade on first day
            else:
                signal = signals.iloc[i-1]
            # Trade at close t
            if signal == 1:
                self.broker.market_order('buy', 1, price)
            elif signal == -1:
                self.broker.market_order('sell', 1, price)
            # Track
            cash_history.append(self.broker.cash)
            position_history.append(self.broker.position)
            equity_history.append(self.broker.cash + self.broker.position * price)
        # Results DataFrame
        results = pd.DataFrame({
            'price': prices.values,
            'cash': cash_history,
            'position': position_history,
            'equity': equity_history
        }, index=prices.index)
        return results
if __name__ == "__main__":
    from backtester.strategy import WindowedMovingAverageStrategy, load_prices_from_generator
    from backtester.broker import Broker
    print("Running backtester example...")
    prices = load_prices_from_generator(
        symbol="AAPL",
        start_price=150.0,
        num_ticks=20,
        volatility=0.02
    )
    strategy = WindowedMovingAverageStrategy(window=5)
    broker = Broker(cash=10000)
    backtester = Backtester(strategy, broker)
    results = backtester.run(prices)
    print(results.head(10))
    print(f"\nFinal equity: {results['equity'].iloc[-1]:.2f}")
