import datetime
import pytest
from src.backtester.models import MarketDataPoint, Order, Position, Portfolio


class TestMarketDataPoint:
    def test_creation(self):
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        mdp = MarketDataPoint(timestamp=timestamp, symbol="AAPL", price=150.0)
        assert mdp.timestamp == timestamp
        assert mdp.symbol == "AAPL"
        assert mdp.price == 150.0

    def test_frozen(self):
        """Test that MarketDataPoint is immutable (frozen dataclass)"""
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        mdp = MarketDataPoint(timestamp=timestamp, symbol="AAPL", price=150.0)
        with pytest.raises(AttributeError):
            mdp.price = 200.0

    def test_equality(self):
        """Test that two MarketDataPoints with same values are equal"""
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        mdp1 = MarketDataPoint(timestamp=timestamp, symbol="AAPL", price=150.0)
        mdp2 = MarketDataPoint(timestamp=timestamp, symbol="AAPL", price=150.0)
        assert mdp1 == mdp2

    def test_different_prices_not_equal(self):
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        mdp1 = MarketDataPoint(timestamp=timestamp, symbol="AAPL", price=150.0)
        mdp2 = MarketDataPoint(timestamp=timestamp, symbol="AAPL", price=151.0)
        assert mdp1 != mdp2


class TestOrder:
    def test_creation(self):
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        order = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="bid",
            quantity=10.0,
        )
        assert order.timestamp == timestamp
        assert order.symbol == "AAPL"
        assert order.price == 150.0
        assert order.action == "bid"
        assert order.quantity == 10.0

    def test_mutable(self):
        """Test that Order is mutable (not frozen)"""
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        order = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="bid",
            quantity=10.0,
        )
        order.price = 200.0
        assert order.price == 200.0

    def test_bid_action(self):
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        order = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="bid",
            quantity=10.0,
        )
        assert order.action == "bid"

    def test_ask_action(self):
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        order = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="ask",
            quantity=10.0,
        )
        assert order.action == "ask"


class TestPosition:
    def test_creation(self):
        pos = Position(symbol="AAPL", quantity=100.0, pnl=-15000.0)
        assert pos.symbol == "AAPL"
        assert pos.quantity == 100.0
        assert pos.pnl == -15000.0

    def test_update_quantity(self):
        pos = Position(symbol="AAPL", quantity=100.0, pnl=-15000.0)
        pos.quantity += 50.0
        assert pos.quantity == 150.0

    def test_update_pnl(self):
        pos = Position(symbol="AAPL", quantity=100.0, pnl=-15000.0)
        pos.pnl += 500.0
        assert pos.pnl == -14500.0

    def test_negative_quantity(self):
        """Test that we can have negative positions (short)"""
        pos = Position(symbol="AAPL", quantity=-100.0, pnl=15000.0)
        assert pos.quantity == -100.0


class TestPortfolio:
    def test_creation(self):
        portfolio = Portfolio(initial_cash=100000.0)
        assert portfolio.cash == 100000.0
        assert portfolio.positions == {}
        assert portfolio.order_history == []

    def test_calculate_pnl_bid(self):
        """Test PnL calculation for bid (buy) order"""
        portfolio = Portfolio(initial_cash=100000.0)
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        order = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="bid",
            quantity=10.0,
        )
        pnl = portfolio.calculate_pnl(order)
        assert pnl == -1500.0  # Negative because we're buying

    def test_calculate_pnl_ask(self):
        """Test PnL calculation for ask (sell) order"""
        portfolio = Portfolio(initial_cash=100000.0)
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        order = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="ask",
            quantity=10.0,
        )
        pnl = portfolio.calculate_pnl(order)
        assert pnl == 1500.0  # Positive because we're selling

    def test_update_position_new_bid(self):
        """Test creating a new position with a bid order"""
        portfolio = Portfolio(initial_cash=100000.0)
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        order = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="bid",
            quantity=10.0,
        )
        portfolio.update_position(order)

        assert "AAPL" in portfolio.positions
        assert portfolio.positions["AAPL"].quantity == 10.0
        assert portfolio.positions["AAPL"].pnl == -1500.0
        assert portfolio.cash == 98500.0
        assert len(portfolio.order_history) == 1

    def test_update_position_new_ask(self):
        """Test creating a new position with an ask order (short)"""
        portfolio = Portfolio(initial_cash=100000.0)
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)
        order = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="ask",
            quantity=10.0,
        )
        portfolio.update_position(order)

        assert "AAPL" in portfolio.positions
        assert portfolio.positions["AAPL"].quantity == 10.0
        assert portfolio.positions["AAPL"].pnl == 1500.0
        assert portfolio.cash == 101500.0

    def test_update_position_existing_bid(self):
        """Test adding to an existing position with a bid"""
        portfolio = Portfolio(initial_cash=100000.0)
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)

        # First order: buy 10 shares at $150
        order1 = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="bid",
            quantity=10.0,
        )
        portfolio.update_position(order1)

        # Second order: buy 5 more shares at $155
        order2 = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=155.0,
            action="bid",
            quantity=5.0,
        )
        portfolio.update_position(order2)

        assert portfolio.positions["AAPL"].quantity == 15.0
        assert portfolio.positions["AAPL"].pnl == -2275.0
        assert portfolio.cash == 97725.0
        assert len(portfolio.order_history) == 2

    def test_update_position_existing_ask(self):
        """Test reducing an existing position with an ask"""
        portfolio = Portfolio(initial_cash=100000.0)
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)

        # First order: buy 10 shares at $150
        order1 = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="bid",
            quantity=10.0,
        )
        portfolio.update_position(order1)

        # Second order: sell 5 shares at $155
        order2 = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=155.0,
            action="ask",
            quantity=5.0,
        )
        portfolio.update_position(order2)

        assert portfolio.positions["AAPL"].quantity == 5.0
        assert portfolio.positions["AAPL"].pnl == -725.0  # -1500 + 775
        assert portfolio.cash == 99275.0

    def test_multiple_symbols(self):
        """Test portfolio with multiple symbols"""
        portfolio = Portfolio(initial_cash=100000.0)
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)

        # Buy AAPL
        order1 = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="bid",
            quantity=10.0,
        )
        portfolio.update_position(order1)

        # Buy GOOGL
        order2 = Order(
            timestamp=timestamp,
            symbol="GOOGL",
            price=2800.0,
            action="bid",
            quantity=5.0,
        )
        portfolio.update_position(order2)

        assert len(portfolio.positions) == 2
        assert "AAPL" in portfolio.positions
        assert "GOOGL" in portfolio.positions
        assert portfolio.positions["AAPL"].quantity == 10.0
        assert portfolio.positions["GOOGL"].quantity == 5.0

    def test_round_trip_trade(self):
        """Test buying and then selling the same quantity"""
        portfolio = Portfolio(initial_cash=100000.0)
        timestamp = datetime.datetime(2025, 1, 1, 12, 0, 0)

        # Buy 10 shares at $150
        order1 = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=150.0,
            action="bid",
            quantity=10.0,
        )
        portfolio.update_position(order1)

        # Sell 10 shares at $155 (profit)
        order2 = Order(
            timestamp=timestamp,
            symbol="AAPL",
            price=155.0,
            action="ask",
            quantity=10.0,
        )
        portfolio.update_position(order2)

        assert portfolio.positions["AAPL"].quantity == 0.0
        assert portfolio.positions["AAPL"].pnl == 50.0  # -1500 + 1550
        assert portfolio.cash == 100050.0
