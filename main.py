from finm32500_assignment_5.engine import Backtester
from backtester.strategy import WindowedMovingAverageStrategy
from backtester.broker import Broker
from backtester.price_loader import load_prices_from_generator


def main():
    """Run a backtest using the WindowedMovingAverageStrategy."""
    print("=" * 60)
    print("Running Backtest for AAPL")
    print("=" * 60)

    # Load synthetic price data
    print("\nGenerating synthetic price data...")
    prices = load_prices_from_generator(
        symbol="AAPL", start_price=150.0, num_ticks=100, volatility=0.02
    )
    print(f"Generated {len(prices)} price points")
    print(f"Starting price: ${prices.iloc[0]:.2f}")
    print(f"Ending price: ${prices.iloc[-1]:.2f}")

    # Initialize strategy and broker
    print("\nInitializing strategy and broker...")
    strategy = WindowedMovingAverageStrategy(window=5)
    broker = Broker(cash=10000)
    print(f"Initial cash: ${broker.cash:.2f}")

    # Run backtest
    print("\nRunning backtest...")
    backtester = Backtester(strategy, broker)
    results = backtester.run(prices)

    # Display results
    print("\n" + "=" * 60)
    print("Backtest Results")
    print("=" * 60)
    print("\nFirst 10 rows:")
    print(results.head(10))
    print("\nLast 10 rows:")
    print(results.tail(10))

    # Performance summary
    print("\n" + "=" * 60)
    print("Performance Summary")
    print("=" * 60)
    initial_equity = 10000
    final_equity = results["equity"].iloc[-1]
    total_return = (final_equity - initial_equity) / initial_equity * 100

    print(f"Initial equity: ${initial_equity:.2f}")
    print(f"Final equity: ${final_equity:.2f}")
    print(f"Total return: {total_return:.2f}%")
    print(f"Final position: {results['position'].iloc[-1]} shares")
    print(f"Final cash: ${results['cash'].iloc[-1]:.2f}")


if __name__ == "__main__":
    main()
