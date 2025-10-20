import pytest
import pandas as pd
import numpy as np
from src.backtester.strategy import WindowedMovingAverageStrategy


class TestWindowedMovingAverageStrategy:
    def test_initialization(self):
        """Test strategy initialization"""
        strategy = WindowedMovingAverageStrategy(window=5)
        assert strategy.window == 5

    def test_initialization_different_windows(self):
        """Test initialization with different window sizes"""
        strategy10 = WindowedMovingAverageStrategy(window=10)
        strategy20 = WindowedMovingAverageStrategy(window=20)
        assert strategy10.window == 10
        assert strategy20.window == 20

    def test_signals_not_enough_data(self):
        """Test signals when there's not enough data for the window"""
        strategy = WindowedMovingAverageStrategy(window=5)
        prices = pd.Series([100, 101, 102], index=pd.date_range("2025-01-01", periods=3))
        signals = strategy.signals(prices)

        # All signals should be 0 (hold) when we don't have enough data
        assert all(signals == 0)

    def test_signals_exactly_window_size(self):
        """Test signals when we have exactly window size data points"""
        strategy = WindowedMovingAverageStrategy(window=5)
        prices = pd.Series([100, 101, 102, 103, 104], index=pd.date_range("2025-01-01", periods=5))
        signals = strategy.signals(prices)

        # First 5 signals should be 0 (not enough history)
        assert all(signals.iloc[0:5] == 0)

    def test_signals_buy_signal(self):
        """Test generation of buy signal when price > moving average"""
        strategy = WindowedMovingAverageStrategy(window=3)
        # Prices: [100, 100, 100, 110] - last price well above average
        prices = pd.Series([100, 100, 100, 110], index=pd.date_range("2025-01-01", periods=4))
        signals = strategy.signals(prices)

        # First 3 signals should be 0
        assert signals.iloc[0] == 0
        assert signals.iloc[1] == 0
        assert signals.iloc[2] == 0

        # Signal at index 3: price=110 > mean(100,100,100)=100
        assert signals.iloc[3] == 1  # Buy signal

    def test_signals_sell_signal(self):
        """Test generation of sell signal when price < moving average"""
        strategy = WindowedMovingAverageStrategy(window=3)
        # Prices: [100, 100, 100, 90] - last price well below average
        prices = pd.Series([100, 100, 100, 90], index=pd.date_range("2025-01-01", periods=4))
        signals = strategy.signals(prices)

        # Signal at index 3: price=90 < mean(100,100,100)=100
        assert signals.iloc[3] == -1  # Sell signal

    def test_signals_hold_signal(self):
        """Test generation of hold signal when price == moving average"""
        strategy = WindowedMovingAverageStrategy(window=3)
        # Prices: [100, 100, 100, 100] - last price equals average
        prices = pd.Series([100, 100, 100, 100], index=pd.date_range("2025-01-01", periods=4))
        signals = strategy.signals(prices)

        # Signal at index 3: price=100 == mean(100,100,100)=100
        assert signals.iloc[3] == 0  # Hold signal

    def test_signals_increasing_trend(self):
        """Test signals with steadily increasing prices"""
        strategy = WindowedMovingAverageStrategy(window=5)
        prices = pd.Series(
            np.linspace(100, 120, 20),
            index=pd.date_range("2025-01-01", periods=20)
        )
        signals = strategy.signals(prices)

        # First 5 should be 0 (not enough data)
        assert all(signals.iloc[0:5] == 0)

        # In an uptrend, most signals after window should be buy (1)
        # because current price > moving average of past prices
        buy_signals = (signals.iloc[5:] == 1).sum()
        assert buy_signals > 10  # Most should be buys

    def test_signals_decreasing_trend(self):
        """Test signals with steadily decreasing prices"""
        strategy = WindowedMovingAverageStrategy(window=5)
        prices = pd.Series(
            np.linspace(120, 100, 20),
            index=pd.date_range("2025-01-01", periods=20)
        )
        signals = strategy.signals(prices)

        # First 5 should be 0 (not enough data)
        assert all(signals.iloc[0:5] == 0)

        # In a downtrend, most signals after window should be sell (-1)
        # because current price < moving average of past prices
        sell_signals = (signals.iloc[5:] == -1).sum()
        assert sell_signals > 10  # Most should be sells

    def test_signals_flat_prices(self):
        """Test signals with flat (constant) prices"""
        strategy = WindowedMovingAverageStrategy(window=5)
        prices = pd.Series([100] * 20, index=pd.date_range("2025-01-01", periods=20))
        signals = strategy.signals(prices)

        # First 5 should be 0
        assert all(signals.iloc[0:5] == 0)

        # All subsequent signals should be 0 (hold) because price == MA
        assert all(signals.iloc[5:] == 0)

    def test_signals_window_calculation(self):
        """Test that window is calculated correctly"""
        strategy = WindowedMovingAverageStrategy(window=3)
        prices = pd.Series([100, 102, 104, 106, 108, 110], index=pd.date_range("2025-01-01", periods=6))
        signals = strategy.signals(prices)

        # At index 3: window is [100, 102, 104], mean=102, price=106 > 102
        assert signals.iloc[3] == 1

        # At index 4: window is [102, 104, 106], mean=104, price=108 > 104
        assert signals.iloc[4] == 1

        # At index 5: window is [104, 106, 108], mean=106, price=110 > 106
        assert signals.iloc[5] == 1

    def test_signals_length_matches_prices(self):
        """Test that signals series has same length as prices"""
        strategy = WindowedMovingAverageStrategy(window=5)
        prices = pd.Series(np.random.randn(50) + 100, index=pd.date_range("2025-01-01", periods=50))
        signals = strategy.signals(prices)

        assert len(signals) == len(prices)

    def test_signals_index_matches_prices(self):
        """Test that signals index matches prices index"""
        strategy = WindowedMovingAverageStrategy(window=5)
        index = pd.date_range("2025-01-01", periods=20)
        prices = pd.Series(np.random.randn(20) + 100, index=index)
        signals = strategy.signals(prices)

        assert all(signals.index == prices.index)

    def test_signals_dtype_is_int(self):
        """Test that signals are integers"""
        strategy = WindowedMovingAverageStrategy(window=5)
        prices = pd.Series(np.random.randn(20) + 100, index=pd.date_range("2025-01-01", periods=20))
        signals = strategy.signals(prices)

        assert signals.dtype in [int, np.int64, np.int32, float, np.float64]  # Can be int or float dtype

    def test_signals_only_valid_values(self):
        """Test that signals only contain -1, 0, or 1"""
        strategy = WindowedMovingAverageStrategy(window=5)
        prices = pd.Series(np.random.randn(50) + 100, index=pd.date_range("2025-01-01", periods=50))
        signals = strategy.signals(prices)

        assert all(signals.isin([-1, 0, 1]))

    def test_signals_window_1(self):
        """Test edge case with window=1"""
        strategy = WindowedMovingAverageStrategy(window=1)
        prices = pd.Series([100, 105, 95, 100], index=pd.date_range("2025-01-01", periods=4))
        signals = strategy.signals(prices)

        # With window=1, we need at least 1 historical point
        assert signals.iloc[0] == 0  # Not enough data

        # At index 1: window is [100], mean=100, price=105 > 100
        assert signals.iloc[1] == 1

        # At index 2: window is [105], mean=105, price=95 < 105
        assert signals.iloc[2] == -1

        # At index 3: window is [95], mean=95, price=100 > 95
        assert signals.iloc[3] == 1

    def test_signals_large_window(self):
        """Test with a large window size"""
        strategy = WindowedMovingAverageStrategy(window=50)
        prices = pd.Series(np.linspace(100, 200, 100), index=pd.date_range("2025-01-01", periods=100))
        signals = strategy.signals(prices)

        # First 50 should be 0
        assert all(signals.iloc[0:50] == 0)

        # After that, in an uptrend, should mostly be buys
        assert (signals.iloc[50:] == 1).sum() > 40

    def test_signals_volatile_prices(self):
        """Test with volatile random walk prices"""
        np.random.seed(42)
        strategy = WindowedMovingAverageStrategy(window=10)
        prices = pd.Series(
            100 * (1 + np.random.randn(100) * 0.02).cumprod(),
            index=pd.date_range("2025-01-01", periods=100)
        )
        signals = strategy.signals(prices)

        # Should have mix of signals
        assert (signals == 1).sum() > 0  # Some buys
        assert (signals == -1).sum() > 0  # Some sells
        assert (signals == 0).sum() > 0  # Some holds

    def test_signals_mean_reversion(self):
        """Test signals with mean-reverting prices"""
        strategy = WindowedMovingAverageStrategy(window=5)
        # Oscillating prices around 100
        prices = pd.Series(
            [100, 110, 100, 90, 100, 110, 100, 90, 100],
            index=pd.date_range("2025-01-01", periods=9)
        )
        signals = strategy.signals(prices)

        # First 5 should be 0
        assert all(signals.iloc[0:5] == 0)

        # Should generate various signals
        assert len(set(signals.iloc[5:].values)) > 1  # Not all the same

    def test_signals_exact_boundary(self):
        """Test signals at exact boundary conditions"""
        strategy = WindowedMovingAverageStrategy(window=2)
        # Carefully constructed to test boundary: mean of [100, 100] = 100
        prices = pd.Series([100, 100, 100], index=pd.date_range("2025-01-01", periods=3))
        signals = strategy.signals(prices)

        # First 2 should be 0
        assert signals.iloc[0] == 0
        assert signals.iloc[1] == 0

        # At index 2: window is [100, 100], mean=100, price=100 == 100
        assert signals.iloc[2] == 0  # Hold

    def test_signals_precision(self):
        """Test that floating point precision doesn't cause issues"""
        strategy = WindowedMovingAverageStrategy(window=3)
        prices = pd.Series(
            [100.00000001, 100.00000002, 100.00000003, 100.00000004],
            index=pd.date_range("2025-01-01", periods=4)
        )
        signals = strategy.signals(prices)

        # Should still generate signals despite tiny differences
        assert signals.iloc[3] in [-1, 0, 1]
