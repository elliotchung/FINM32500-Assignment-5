# backtester/strategy.py
import numpy as np
import pandas as pd
from backtester.price_loader import load_prices_from_generator

class WindowedMovingAverageStrategy:

    def __init__(self, window: int):
        self.window = window

    def signals(self, prices: pd.Series) -> pd.Series:
        signals = pd.Series(index=prices.index, dtype=int)
        for i in range(len(prices)):
            if i < self.window:
                signals.iloc[i] = 0  # Not enough data for signal
            else:
                windowed_prices = prices.iloc[i - self.window:i]
                if prices.iloc[i] > windowed_prices.mean():
                    signals.iloc[i] = 1  # Buy signal
                elif prices.iloc[i] < windowed_prices.mean():
                    signals.iloc[i] = -1  # Sell signal
                else:
                    signals.iloc[i] = 0  # Hold signal
        return signals


if __name__ == "__main__":
    # Example usage
    print("Loading synthetic prices for AAPL")
    prices = load_prices_from_generator(
        symbol="AAPL",
        start_price=150.0,
        num_ticks=100,
        volatility=0.02
    )

    strategy = WindowedMovingAverageStrategy(window=5)
    signals = strategy.signals(prices)

    print(f"\nGenerated {len(signals)} signals for {prices.name}")
    print(f"\nFirst 10 signals:")
    print(signals.head(10))