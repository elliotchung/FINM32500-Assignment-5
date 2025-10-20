import pytest
import pandas as pd
import numpy as np
from src.backtester.engine import Backtester
from src.backtester.broker import Broker
from src.backtester.strategy import WindowedMovingAverageStrategy


class MockStrategy:
    """Mock strategy that returns predefined signals"""

    def __init__(self, signals_list):
        self.signals_list = signals_list

    def signals(self, prices):
        return pd.Series(self.signals_list, index=prices.index, dtype=int)


class TestBacktester:
    def test_initialization(self):
        """Test Backtester initialization"""
        strategy = WindowedMovingAverageStrategy(window=5)
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        assert backtester.strategy == strategy
        assert backtester.broker == broker

    def test_run_no_trades(self):
        """Test running backtest with no trading signals"""
        prices = pd.Series([100, 101, 102, 103, 104], index=pd.date_range("2025-01-01", periods=5))
        strategy = MockStrategy([0, 0, 0, 0, 0])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        assert len(results) == 5
        assert list(results.columns) == ["price", "cash", "position", "equity"]
        assert all(results["position"] == 0)
        assert all(results["cash"] == 10000.0)
        assert all(results["equity"] == 10000.0)

    def test_run_single_buy(self):
        """Test backtest with a single buy signal"""
        prices = pd.Series([100, 101, 102, 103, 104], index=pd.date_range("2025-01-01", periods=5))
        # First signal is used at t=1, so signal at index 0 triggers trade at index 1
        strategy = MockStrategy([1, 0, 0, 0, 0])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        # No trade on day 0 (first day)
        assert results["position"].iloc[0] == 0
        assert results["cash"].iloc[0] == 10000.0

        # Trade happens on day 1 using signal from day 0
        assert results["position"].iloc[1] == 1
        assert results["cash"].iloc[1] == pytest.approx(10000.0 - 101.0)

        # Position held through remaining days
        assert results["position"].iloc[2] == 1
        assert results["position"].iloc[3] == 1
        assert results["position"].iloc[4] == 1

    def test_run_single_sell(self):
        """Test backtest with a single sell signal"""
        prices = pd.Series([100, 101, 102, 103, 104], index=pd.date_range("2025-01-01", periods=5))
        strategy = MockStrategy([-1, 0, 0, 0, 0])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        # No trade on day 0
        assert results["position"].iloc[0] == 0

        # Sell on day 1 (short)
        assert results["position"].iloc[1] == -1
        assert results["cash"].iloc[1] == pytest.approx(10000.0 + 101.0)

    def test_run_buy_then_sell(self):
        """Test backtest with buy followed by sell"""
        prices = pd.Series([100, 101, 102, 103, 104], index=pd.date_range("2025-01-01", periods=5))
        strategy = MockStrategy([1, 0, -1, 0, 0])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        # Day 0: no trade
        assert results["position"].iloc[0] == 0

        # Day 1: buy at 101
        assert results["position"].iloc[1] == 1

        # Day 2: hold (signal from day 1 is 0)
        assert results["position"].iloc[2] == 1

        # Day 3: sell at 103 (signal from day 2 is -1)
        assert results["position"].iloc[3] == 0
        # Should have made profit: bought at 101, sold at 103
        assert results["cash"].iloc[3] > 10000.0

    def test_run_equity_calculation(self):
        """Test that equity is calculated correctly"""
        prices = pd.Series([100, 101, 102, 103, 104], index=pd.date_range("2025-01-01", periods=5))
        strategy = MockStrategy([1, 0, 0, 0, 0])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        # Day 0: equity = cash (no position)
        assert results["equity"].iloc[0] == 10000.0

        # Day 1: equity = cash + position * price
        expected_equity = results["cash"].iloc[1] + results["position"].iloc[1] * results["price"].iloc[1]
        assert results["equity"].iloc[1] == pytest.approx(expected_equity)

        # Day 4: equity should reflect position value at current price
        expected_equity = results["cash"].iloc[4] + results["position"].iloc[4] * results["price"].iloc[4]
        assert results["equity"].iloc[4] == pytest.approx(expected_equity)

    def test_run_multiple_trades(self):
        """Test backtest with multiple trades"""
        prices = pd.Series([100, 101, 102, 103, 104, 105, 106], index=pd.date_range("2025-01-01", periods=7))
        strategy = MockStrategy([1, 0, -1, 0, 1, 0, -1])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        # Verify trades occurred
        assert results["position"].iloc[1] == 1  # Buy
        assert results["position"].iloc[3] == 0  # Sell
        assert results["position"].iloc[5] == 1  # Buy again

    def test_run_increasing_prices(self):
        """Test backtest with steadily increasing prices"""
        prices = pd.Series(np.linspace(100, 120, 20), index=pd.date_range("2025-01-01", periods=20))
        strategy = WindowedMovingAverageStrategy(window=5)
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        assert len(results) == 20
        assert "price" in results.columns
        assert "cash" in results.columns
        assert "position" in results.columns
        assert "equity" in results.columns

    def test_run_decreasing_prices(self):
        """Test backtest with steadily decreasing prices"""
        prices = pd.Series(np.linspace(120, 100, 20), index=pd.date_range("2025-01-01", periods=20))
        strategy = WindowedMovingAverageStrategy(window=5)
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        assert len(results) == 20
        # Equity should be tracked throughout
        assert all(results["equity"] >= 0)  # Assuming no massive losses

    def test_run_index_preservation(self):
        """Test that the results DataFrame preserves the price series index"""
        index = pd.date_range("2025-01-01", periods=5)
        prices = pd.Series([100, 101, 102, 103, 104], index=index)
        strategy = MockStrategy([0, 0, 0, 0, 0])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        assert all(results.index == index)

    def test_run_price_values_in_results(self):
        """Test that price values are correctly stored in results"""
        prices = pd.Series([100, 101, 102, 103, 104], index=pd.date_range("2025-01-01", periods=5))
        strategy = MockStrategy([0, 0, 0, 0, 0])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        assert all(results["price"] == prices.values)

    def test_run_first_day_no_trade(self):
        """Test that no trade occurs on the first day"""
        prices = pd.Series([100, 101, 102], index=pd.date_range("2025-01-01", periods=3))
        # Even with a buy signal on day 0, no trade should occur
        strategy = MockStrategy([1, 1, 1])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        # Day 0: no trade
        assert results["position"].iloc[0] == 0
        assert results["cash"].iloc[0] == 10000.0

    def test_run_with_volatile_prices(self):
        """Test backtest with volatile prices"""
        np.random.seed(42)
        prices = pd.Series(
            100 * (1 + np.random.randn(50) * 0.02).cumprod(),
            index=pd.date_range("2025-01-01", periods=50)
        )
        strategy = WindowedMovingAverageStrategy(window=10)
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        assert len(results) == 50
        # All equity values should be finite
        assert all(np.isfinite(results["equity"]))

    def test_run_signal_lag(self):
        """Test that signals are properly lagged (t-1 signal used at t)"""
        prices = pd.Series([100, 100, 100, 100], index=pd.date_range("2025-01-01", periods=4))
        # Signal at index 1 should trigger trade at index 2
        strategy = MockStrategy([0, 1, 0, 0])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        # No trade on days 0 and 1
        assert results["position"].iloc[0] == 0
        assert results["position"].iloc[1] == 0

        # Trade happens on day 2 using signal from day 1
        assert results["position"].iloc[2] == 1

    def test_run_accumulation(self):
        """Test accumulating positions with multiple buy signals"""
        prices = pd.Series([100, 100, 100, 100, 100], index=pd.date_range("2025-01-01", periods=5))
        strategy = MockStrategy([1, 1, 1, 0, 0])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        # Multiple buys should accumulate position
        assert results["position"].iloc[1] == 1  # First buy
        assert results["position"].iloc[2] == 2  # Second buy
        assert results["position"].iloc[3] == 3  # Third buy

    def test_run_distribution(self):
        """Test distributing positions with multiple sell signals"""
        prices = pd.Series([100, 100, 100, 100, 100, 100], index=pd.date_range("2025-01-01", periods=6))
        # Buy three times, then sell three times
        strategy = MockStrategy([1, 1, 1, -1, -1, -1])
        broker = Broker(cash=10000)
        backtester = Backtester(strategy=strategy, broker=broker)

        results = backtester.run(prices)

        # Build up position
        assert results["position"].iloc[3] == 3

        # Sell down position
        assert results["position"].iloc[4] == 2
        assert results["position"].iloc[5] == 1
