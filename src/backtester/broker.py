class Broker:
    def __init__(self, cash: float = 1_000_000):
        self.cash = cash
        self.position = 0

    def market_order(self, side: str, qty: int, price: float):
        """
        Executes a market order and updates cash/position.
        No slippage, no fees. Deterministic for testing.
        side: 'buy' or 'sell'
        qty: number of shares
        price: execution price
        """
        if side == 'buy':
            self.position += qty
            self.cash -= qty * price
        elif side == 'sell':
            self.position -= qty
            self.cash += qty * price
        else:
            raise ValueError(f"Unknown side: {side}")

    def __repr__(self):
        return f"Broker(cash={self.cash:.2f}, position={self.position})"

if __name__ == "__main__":
    from backtester.strategy import WindowedMovingAverageStrategy, load_prices_from_generator
    print("Running broker test with synthetic signals...")
    prices = load_prices_from_generator(
        symbol="AAPL",
        start_price=150.0,
        num_ticks=20,
        volatility=0.02
    )
    strategy = WindowedMovingAverageStrategy(window=5)
    signals = strategy.signals(prices)
    broker = Broker(cash=10000)
    for dt, price, signal in zip(prices.index, prices.values, signals.values):
        if signal == 1:
            broker.market_order('buy', 1, price)
        elif signal == -1:
            broker.market_order('sell', 1, price)
        # signal == 0: hold
    print(f"Final broker state: {broker}")
