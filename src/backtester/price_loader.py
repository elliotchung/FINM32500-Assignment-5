# price_loader.py

import pandas as pd
from src.backtester.data_generator import market_data_generator


def load_prices_from_generator(
    symbol: str,
    start_price: float,
    num_ticks: int = 100,
    volatility: float = 0.01,
    interval: float = 0.0,
) -> pd.Series:
    """
    Generates synthetic market data using market_data_generator and returns
    a pandas Series of prices indexed by timestamp.

    :param symbol: Ticker symbol (e.g., "AAPL").
    :param start_price: Initial price.
    :param num_ticks: Number of price ticks to generate.
    :param volatility: Std dev of returns per tick.
    :param interval: Pause in seconds between ticks (set to 0 for fast generation).
    :return: pandas.Series with timestamp index and price values.
    """
    gen = market_data_generator(
        symbol=symbol, start_price=start_price, volatility=volatility, interval=interval
    )

    timestamps = []
    prices = []

    for _ in range(num_ticks):
        tick = next(gen)
        timestamps.append(tick.timestamp)
        prices.append(tick.price)

    return pd.Series(data=prices, index=timestamps, name=symbol)


# if __name__ == "__main__":
#     # Example 1: Generate 100 price points for AAPL
#     print("Example 1: Loading synthetic prices for AAPL")
#     print("-" * 50)
#     prices_aapl = load_prices_from_generator(
#         symbol="AAPL", start_price=150.0, num_ticks=100, volatility=0.02
#     )
#
#     print(f"\nGenerated {len(prices_aapl)} price points for {prices_aapl.name}")
#     print("\nFirst 5 prices:")
#     print(prices_aapl.head())
#     print("\nLast 5 prices:")
#     print(prices_aapl.tail())
#     print("\nPrice statistics:")
#     print(prices_aapl.describe())
#
#     # Example 2: Generate fewer ticks with lower volatility
#     print("\n" + "=" * 50)
#     print("Example 2: Loading synthetic prices for GOOGL")
#     print("-" * 50)
#     prices_googl = load_prices_from_generator(
#         symbol="GOOGL", start_price=2800.0, num_ticks=50, volatility=0.01
#     )
#
#     print(f"\nGenerated {len(prices_googl)} price points for {prices_googl.name}")
#     print(f"Starting price: ${prices_googl.iloc[0]:.2f}")
#     print(f"Ending price: ${prices_googl.iloc[-1]:.2f}")
#     print(f"Min price: ${prices_googl.min():.2f}")
#     print(f"Max price: ${prices_googl.max():.2f}")
#     print(f"Mean price: ${prices_googl.mean():.2f}")
#
#     # Example 3: Demonstrating index access
#     print("\n" + "=" * 50)
#     print("Example 3: Accessing data by timestamp")
#     print("-" * 50)
#     print(f"\nFirst timestamp: {prices_aapl.index[0]}")
#     print(f"Last timestamp: {prices_aapl.index[-1]}")
#     print(f"\nPrice at first timestamp: ${prices_aapl.iloc[0]:.2f}")
#     print(f"Price at last timestamp: ${prices_aapl.iloc[-1]:.2f}")
