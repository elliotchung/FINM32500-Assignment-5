import pytest
import pandas as pd
import numpy as np
from src.backtester.price_loader import load_prices_from_generator


class TestLoadPricesFromGenerator:
    def test_returns_series(self):
        """Test that function returns a pandas Series"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=10,
            interval=0.0
        )
        assert isinstance(result, pd.Series)

    def test_correct_length(self):
        """Test that returned series has correct length"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=20,
            interval=0.0
        )
        assert len(result) == 20

    def test_correct_symbol_name(self):
        """Test that series has correct symbol as name"""
        result = load_prices_from_generator(
            symbol="GOOGL",
            start_price=2800.0,
            num_ticks=10,
            interval=0.0
        )
        assert result.name == "GOOGL"

    def test_different_symbols(self):
        """Test with different symbols"""
        result_aapl = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=10,
            interval=0.0
        )
        result_googl = load_prices_from_generator(
            symbol="GOOGL",
            start_price=2800.0,
            num_ticks=10,
            interval=0.0
        )

        assert result_aapl.name == "AAPL"
        assert result_googl.name == "GOOGL"

    def test_index_is_datetime(self):
        """Test that index contains datetime objects"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=10,
            interval=0.0
        )
        assert all(isinstance(idx, pd.Timestamp) for idx in result.index)

    def test_prices_are_positive(self):
        """Test that all prices are positive"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=100,
            volatility=0.01,
            interval=0.0
        )
        assert all(result > 0)

    def test_start_price_influence(self):
        """Test that start_price influences the generated prices"""
        result_low = load_prices_from_generator(
            symbol="AAPL",
            start_price=50.0,
            num_ticks=10,
            volatility=0.0,
            interval=0.0
        )
        result_high = load_prices_from_generator(
            symbol="AAPL",
            start_price=500.0,
            num_ticks=10,
            volatility=0.0,
            interval=0.0
        )

        # Mean of low prices should be around 50
        assert 40 < result_low.mean() < 60

        # Mean of high prices should be around 500
        assert 450 < result_high.mean() < 550

    def test_num_ticks_parameter(self):
        """Test different values of num_ticks"""
        result_10 = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=10,
            interval=0.0
        )
        result_50 = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=50,
            interval=0.0
        )
        result_100 = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=100,
            interval=0.0
        )

        assert len(result_10) == 10
        assert len(result_50) == 50
        assert len(result_100) == 100

    def test_volatility_effect(self):
        """Test that volatility affects price variation"""
        result_low_vol = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=100,
            volatility=0.001,
            interval=0.0
        )
        result_high_vol = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=100,
            volatility=0.1,
            interval=0.0
        )

        # Higher volatility should create more variation
        std_low = result_low_vol.std()
        std_high = result_high_vol.std()
        assert std_high > std_low

    def test_zero_volatility(self):
        """Test with zero volatility"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=20,
            volatility=0.0,
            interval=0.0
        )
        # With zero volatility, prices should be very stable
        assert result.std() < 1.0

    def test_high_volatility(self):
        """Test with high volatility"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=100,
            volatility=0.05,
            interval=0.0
        )
        # Should have significant variation
        assert result.std() > 0

    def test_interval_zero(self):
        """Test that interval=0 works (no sleep between ticks)"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=10,
            interval=0.0
        )
        assert len(result) == 10

    def test_timestamps_monotonic_increasing(self):
        """Test that timestamps are monotonically increasing"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=20,
            interval=0.0
        )
        # Check that index is sorted
        assert result.index.is_monotonic_increasing

    def test_no_duplicate_timestamps(self):
        """Test that there are no duplicate timestamps"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=20,
            interval=0.0
        )
        assert not result.index.has_duplicates

    def test_single_tick(self):
        """Test generating a single tick"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=1,
            interval=0.0
        )
        assert len(result) == 1
        assert result.iloc[0] > 0

    def test_many_ticks(self):
        """Test generating many ticks"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=500,
            interval=0.0
        )
        assert len(result) == 500

    def test_price_values_are_float(self):
        """Test that price values are floats"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=10,
            interval=0.0
        )
        assert all(isinstance(price, (float, np.floating)) for price in result.values)

    def test_series_properties(self):
        """Test various pandas Series properties"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=20,
            interval=0.0
        )

        # Should be able to access via iloc
        assert result.iloc[0] > 0

        # Should be able to compute statistics
        assert result.mean() > 0
        assert result.std() >= 0
        assert result.min() > 0
        assert result.max() > 0

    def test_integration_with_pandas_operations(self):
        """Test that result integrates well with pandas operations"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=50,
            interval=0.0
        )

        # Should be able to calculate rolling mean
        rolling_mean = result.rolling(window=5).mean()
        assert len(rolling_mean) == 50

        # Should be able to calculate returns
        returns = result.pct_change()
        assert len(returns) == 50

    def test_different_start_prices(self):
        """Test with various start prices"""
        result_low = load_prices_from_generator(
            symbol="PENNY",
            start_price=1.0,
            num_ticks=10,
            volatility=0.0,
            interval=0.0
        )
        result_mid = load_prices_from_generator(
            symbol="MID",
            start_price=100.0,
            num_ticks=10,
            volatility=0.0,
            interval=0.0
        )
        result_high = load_prices_from_generator(
            symbol="HIGH",
            start_price=10000.0,
            num_ticks=10,
            volatility=0.0,
            interval=0.0
        )

        assert 0.5 < result_low.mean() < 2.0
        assert 90 < result_mid.mean() < 110
        assert 9000 < result_high.mean() < 11000

    def test_reproducibility_is_not_guaranteed(self):
        """Test that repeated calls produce different results (randomness)"""
        result1 = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=50,
            volatility=0.02,
            interval=0.0
        )
        result2 = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=50,
            volatility=0.02,
            interval=0.0
        )

        # Results should be different (random walk)
        assert not all(result1.values == result2.values)

    def test_price_rounding(self):
        """Test that prices are rounded to 2 decimal places"""
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=150.0,
            num_ticks=50,
            volatility=0.01,
            interval=0.0
        )

        for price in result.values:
            # Check that each price has at most 2 decimal places
            assert price == round(price, 2)

    def test_handles_edge_case_parameters(self):
        """Test with edge case parameters"""
        # Very small start price
        result = load_prices_from_generator(
            symbol="AAPL",
            start_price=0.01,
            num_ticks=10,
            volatility=0.0,
            interval=0.0
        )
        assert len(result) == 10
        assert all(result > 0)
