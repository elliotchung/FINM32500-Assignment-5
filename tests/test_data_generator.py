import pytest
import datetime
import csv
import os
import tempfile
from src.backtester.data_generator import (
    MarketDataPoint,
    market_data_generator,
    generate_market_csv,
)


class TestMarketDataPointInDataGenerator:
    """Test MarketDataPoint from data_generator module"""

    def test_creation(self):
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        mdp = MarketDataPoint(timestamp=timestamp, symbol="AAPL", price=150.0)
        assert mdp.timestamp == timestamp
        assert mdp.symbol == "AAPL"
        assert mdp.price == 150.0

    def test_frozen_dataclass(self):
        """Test that MarketDataPoint is immutable"""
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        mdp = MarketDataPoint(timestamp=timestamp, symbol="AAPL", price=150.0)
        with pytest.raises(AttributeError):
            mdp.price = 200.0


class TestMarketDataGenerator:
    def test_generator_yields_market_data_point(self):
        """Test that generator yields MarketDataPoint objects"""
        gen = market_data_generator(symbol="AAPL", start_price=150.0, interval=0.0)
        tick = next(gen)
        assert isinstance(tick, MarketDataPoint)
        assert tick.symbol == "AAPL"

    def test_generator_symbol(self):
        """Test that generator uses correct symbol"""
        gen = market_data_generator(symbol="GOOGL", start_price=2800.0, interval=0.0)
        tick = next(gen)
        assert tick.symbol == "GOOGL"

    def test_generator_multiple_ticks(self):
        """Test generating multiple ticks"""
        gen = market_data_generator(symbol="AAPL", start_price=150.0, interval=0.0)
        ticks = [next(gen) for _ in range(10)]
        assert len(ticks) == 10
        assert all(isinstance(tick, MarketDataPoint) for tick in ticks)

    def test_generator_price_changes(self):
        """Test that prices change over time"""
        gen = market_data_generator(
            symbol="AAPL", start_price=150.0, volatility=0.01, interval=0.0
        )
        prices = [next(gen).price for _ in range(100)]
        # Not all prices should be the same (very unlikely with random walk)
        assert len(set(prices)) > 1

    def test_generator_prices_positive(self):
        """Test that generated prices stay positive"""
        gen = market_data_generator(
            symbol="AAPL", start_price=150.0, volatility=0.01, interval=0.0
        )
        prices = [next(gen).price for _ in range(100)]
        assert all(price > 0 for price in prices)

    def test_generator_price_rounding(self):
        """Test that prices are rounded to 2 decimal places"""
        gen = market_data_generator(
            symbol="AAPL", start_price=150.0, volatility=0.01, interval=0.0
        )
        ticks = [next(gen) for _ in range(50)]
        for tick in ticks:
            # Check that price has at most 2 decimal places
            assert tick.price == round(tick.price, 2)

    def test_generator_timestamps_increase(self):
        """Test that timestamps are monotonically increasing"""
        gen = market_data_generator(symbol="AAPL", start_price=150.0, interval=0.0)
        tick1 = next(gen)
        tick2 = next(gen)
        assert tick2.timestamp >= tick1.timestamp

    def test_generator_volatility_zero(self):
        """Test generator with zero volatility"""
        gen = market_data_generator(
            symbol="AAPL", start_price=150.0, volatility=0.0, interval=0.0
        )
        prices = [next(gen).price for _ in range(10)]
        # With zero volatility, prices should all be very close to start price
        assert all(abs(price - 150.0) < 0.5 for price in prices)

    def test_generator_high_volatility(self):
        """Test generator with higher volatility creates more variation"""
        gen_low = market_data_generator(
            symbol="AAPL", start_price=150.0, volatility=0.001, interval=0.0
        )
        gen_high = market_data_generator(
            symbol="AAPL", start_price=150.0, volatility=0.1, interval=0.0
        )

        prices_low = [next(gen_low).price for _ in range(100)]
        prices_high = [next(gen_high).price for _ in range(100)]

        # Higher volatility should create larger price movements
        import numpy as np

        std_low = np.std(prices_low)
        std_high = np.std(prices_high)
        assert std_high > std_low

    def test_generator_different_start_prices(self):
        """Test generator with different start prices"""
        gen1 = market_data_generator(
            symbol="AAPL", start_price=100.0, volatility=0.0, interval=0.0
        )
        gen2 = market_data_generator(
            symbol="AAPL", start_price=200.0, volatility=0.0, interval=0.0
        )

        price1 = next(gen1).price
        price2 = next(gen2).price

        assert abs(price1 - 100.0) < 5  # Should be near 100
        assert abs(price2 - 200.0) < 5  # Should be near 200

    def test_generator_infinite(self):
        """Test that generator is infinite"""
        gen = market_data_generator(symbol="AAPL", start_price=150.0, interval=0.0)
        # Should be able to generate many ticks without exhausting
        ticks = [next(gen) for _ in range(1000)]
        assert len(ticks) == 1000


class TestGenerateMarketCSV:
    def test_generate_csv_creates_file(self):
        """Test that CSV file is created"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=10,
                interval=0.0,
            )
            assert os.path.exists(filename)

    def test_generate_csv_correct_rows(self):
        """Test that CSV has correct number of rows"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=20,
                interval=0.0,
            )

            with open(filename, "r") as f:
                reader = csv.reader(f)
                rows = list(reader)
                # 1 header + 20 data rows
                assert len(rows) == 21

    def test_generate_csv_header(self):
        """Test that CSV has correct header"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=5,
                interval=0.0,
            )

            with open(filename, "r") as f:
                reader = csv.reader(f)
                header = next(reader)
                assert header == ["timestamp", "symbol", "price"]

    def test_generate_csv_data_format(self):
        """Test that CSV data is in correct format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=5,
                interval=0.0,
            )

            with open(filename, "r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    assert len(row) == 3
                    # Timestamp should be ISO format (can be parsed)
                    datetime.datetime.fromisoformat(row[0])
                    # Symbol should be string
                    assert row[1] == "AAPL"
                    # Price should be convertible to float
                    float(row[2])

    def test_generate_csv_symbol(self):
        """Test that CSV contains correct symbol"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")
            generate_market_csv(
                symbol="GOOGL",
                start_price=2800.0,
                filename=filename,
                num_ticks=5,
                interval=0.0,
            )

            with open(filename, "r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    assert row[1] == "GOOGL"

    def test_generate_csv_different_num_ticks(self):
        """Test generating different numbers of ticks"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=50,
                interval=0.0,
            )

            with open(filename, "r") as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) == 51  # header + 50 rows

    def test_generate_csv_volatility(self):
        """Test CSV generation with different volatility"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=10,
                volatility=0.05,
                interval=0.0,
            )

            with open(filename, "r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                prices = [float(row[2]) for row in reader]
                assert len(prices) == 10

    def test_generate_csv_price_values(self):
        """Test that generated prices are reasonable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=100,
                volatility=0.02,
                interval=0.0,
            )

            with open(filename, "r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                prices = [float(row[2]) for row in reader]
                # All prices should be positive
                assert all(price > 0 for price in prices)

    def test_generate_csv_overwrites_existing(self):
        """Test that generating CSV overwrites existing file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")

            # Create first file
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=5,
                interval=0.0,
            )

            # Create second file with different num_ticks
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=10,
                interval=0.0,
            )

            with open(filename, "r") as f:
                reader = csv.reader(f)
                rows = list(reader)
                # Should have 10 ticks (not 5)
                assert len(rows) == 11

    def test_generate_csv_timestamps_parseable(self):
        """Test that all timestamps in CSV are parseable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_market.csv")
            generate_market_csv(
                symbol="AAPL",
                start_price=150.0,
                filename=filename,
                num_ticks=10,
                interval=0.0,
            )

            with open(filename, "r") as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    # Should not raise exception
                    dt = datetime.datetime.fromisoformat(row[0])
                    assert isinstance(dt, datetime.datetime)
