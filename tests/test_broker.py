import pytest
from src.backtester.broker import Broker


class TestBroker:
    def test_initialization_default(self):
        """Test broker initialization with default cash"""
        broker = Broker()
        assert broker.cash == 1_000_000
        assert broker.position == 0

    def test_initialization_custom_cash(self):
        """Test broker initialization with custom cash"""
        broker = Broker(cash=50000)
        assert broker.cash == 50000
        assert broker.position == 0

    def test_market_order_buy_single(self):
        """Test a single buy order"""
        broker = Broker(cash=10000)
        broker.market_order("buy", 10, 150.0)
        assert broker.position == 10
        assert broker.cash == 8500.0  # 10000 - (10 * 150)

    def test_market_order_sell_single(self):
        """Test a single sell order (short selling)"""
        broker = Broker(cash=10000)
        broker.market_order("sell", 10, 150.0)
        assert broker.position == -10
        assert broker.cash == 11500.0  # 10000 + (10 * 150)

    def test_market_order_buy_multiple(self):
        """Test multiple buy orders"""
        broker = Broker(cash=10000)
        broker.market_order("buy", 10, 150.0)
        broker.market_order("buy", 5, 155.0)
        assert broker.position == 15
        assert broker.cash == 8500.0 - 775.0  # 7725.0

    def test_market_order_sell_multiple(self):
        """Test multiple sell orders"""
        broker = Broker(cash=10000)
        broker.market_order("sell", 10, 150.0)
        broker.market_order("sell", 5, 155.0)
        assert broker.position == -15
        assert broker.cash == 11500.0 + 775.0  # 12275.0

    def test_market_order_round_trip(self):
        """Test buying and then selling (round trip)"""
        broker = Broker(cash=10000)
        broker.market_order("buy", 10, 150.0)
        broker.market_order("sell", 10, 155.0)
        assert broker.position == 0
        assert broker.cash == 10050.0  # Made $50 profit

    def test_market_order_losing_round_trip(self):
        """Test buying high and selling low (loss)"""
        broker = Broker(cash=10000)
        broker.market_order("buy", 10, 155.0)
        broker.market_order("sell", 10, 150.0)
        assert broker.position == 0
        assert broker.cash == 9950.0  # Lost $50

    def test_market_order_invalid_side(self):
        """Test that invalid side raises ValueError"""
        broker = Broker(cash=10000)
        with pytest.raises(ValueError, match="Unknown side: invalid"):
            broker.market_order("invalid", 10, 150.0)

    def test_market_order_zero_quantity(self):
        """Test order with zero quantity"""
        broker = Broker(cash=10000)
        broker.market_order("buy", 0, 150.0)
        assert broker.position == 0
        assert broker.cash == 10000.0

    def test_market_order_fractional_shares(self):
        """Test order with fractional shares"""
        broker = Broker(cash=10000)
        broker.market_order("buy", 2.5, 150.0)
        assert broker.position == 2.5
        assert broker.cash == 9625.0  # 10000 - (2.5 * 150)

    def test_market_order_negative_cash(self):
        """Test that broker allows negative cash (margin/leverage)"""
        broker = Broker(cash=1000)
        broker.market_order("buy", 100, 150.0)
        assert broker.position == 100
        assert broker.cash == -14000.0  # 1000 - 15000

    def test_market_order_large_quantities(self):
        """Test orders with large quantities"""
        broker = Broker(cash=1_000_000)
        broker.market_order("buy", 1000, 150.0)
        assert broker.position == 1000
        assert broker.cash == 850_000.0

    def test_repr(self):
        """Test the __repr__ method"""
        broker = Broker(cash=12345.67)
        broker.position = 42
        repr_str = repr(broker)
        assert "Broker" in repr_str
        assert "cash=12345.67" in repr_str
        assert "position=42" in repr_str

    def test_repr_after_trades(self):
        """Test __repr__ after some trades"""
        broker = Broker(cash=10000)
        broker.market_order("buy", 10, 150.0)
        repr_str = repr(broker)
        assert "cash=8500.00" in repr_str
        assert "position=10" in repr_str

    def test_buy_sell_different_prices(self):
        """Test buying and selling at different prices"""
        broker = Broker(cash=10000)
        broker.market_order("buy", 5, 100.0)
        broker.market_order("buy", 5, 110.0)
        broker.market_order("sell", 3, 105.0)
        broker.market_order("sell", 7, 115.0)
        assert broker.position == 0
        assert broker.cash == pytest.approx(10070.0)  # Net profit

    def test_position_tracking(self):
        """Test that position is tracked correctly through multiple orders"""
        broker = Broker(cash=100000)
        assert broker.position == 0

        broker.market_order("buy", 100, 50.0)
        assert broker.position == 100

        broker.market_order("buy", 50, 52.0)
        assert broker.position == 150

        broker.market_order("sell", 75, 55.0)
        assert broker.position == 75

        broker.market_order("sell", 75, 58.0)
        assert broker.position == 0

    def test_cash_tracking(self):
        """Test that cash is tracked correctly through multiple orders"""
        broker = Broker(cash=100000)

        broker.market_order("buy", 100, 50.0)  # Spend 5000
        assert broker.cash == 95000.0

        broker.market_order("sell", 100, 55.0)  # Gain 5500
        assert broker.cash == 100500.0

    def test_short_position(self):
        """Test going short (negative position)"""
        broker = Broker(cash=10000)
        broker.market_order("sell", 50, 100.0)
        assert broker.position == -50
        assert broker.cash == 15000.0

    def test_covering_short(self):
        """Test covering a short position"""
        broker = Broker(cash=10000)
        broker.market_order("sell", 50, 100.0)  # Go short
        broker.market_order("buy", 50, 95.0)  # Cover at lower price (profit)
        assert broker.position == 0
        assert broker.cash == 10250.0  # Made $250 profit

    def test_covering_short_loss(self):
        """Test covering a short position at a loss"""
        broker = Broker(cash=10000)
        broker.market_order("sell", 50, 100.0)  # Go short
        broker.market_order("buy", 50, 105.0)  # Cover at higher price (loss)
        assert broker.position == 0
        assert broker.cash == 9750.0  # Lost $250
