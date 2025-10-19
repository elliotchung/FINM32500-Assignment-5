from typing import override
from collections import deque

import numpy as np

from .models import MarketDataPoint, Order, Strategy


class WindowedMovingAverageStrategy(Strategy):
    def __init__(self, window: int):
        """
        TIME COMPLEXITY: O(1)
        - Dictionary initialization and integer assignment are constant time

        SPACE COMPLEXITY: O(1)
        - Only allocates empty dict and stores window size
        """
        self.past_prices: dict[str, list[MarketDataPoint]] = {}
        self.window: int = window

    def update_price(self, tick: MarketDataPoint):
        """
        TIME COMPLEXITY: O(1) amortized
        - Dictionary lookup: O(1) average case
        - List append: O(1) amortized (occasionally O(n) when resizing)
        - List access [-1]: O(1)
        - Equality check: O(1)

        SPACE COMPLEXITY: O(1) per call
        - Only stores reference to tick in existing list
        - Note: Accumulated space is O(n) per symbol where n = total ticks processed
        """
        if tick.symbol not in self.past_prices:
            self.past_prices[tick.symbol] = [tick]
        elif self.past_prices[tick.symbol][-1] != tick:
            self.past_prices[tick.symbol].append(tick)

    def calculate_average(self, symbol: str):
        """
        TIME COMPLEXITY: O(n) where n = len(past_prices[symbol])
        - List comprehension over all stored prices: O(n)
        - Array creation from list: O(n)
        - Array slicing [-self.window:]: O(w) where w = min(window, n)
        - np.mean over w elements: O(w)
        - Total: O(n) dominated by list comprehension, even though we only use last w elements

        SPACE COMPLEXITY: O(n)
        - List comprehension creates temporary list of n floats
        - np.array allocates array of n elements
        - Slice creates new array of w elements
        - Total temporary space: O(n)
        """
        return float(
            np.mean(
                np.array([p.price for p in self.past_prices[symbol]])[-self.window :]
            )
        )

    @override
    def generate_signal(self, tick: MarketDataPoint) -> Order:
        """
        TIME COMPLEXITY: O(n) where n = total ticks processed for this symbol
        - update_price: O(1) amortized
        - calculate_average: O(n) - dominates the complexity
        - Order creation: O(1)
        - Total: O(n)

        SPACE COMPLEXITY: O(n)
        - Temporary space from calculate_average: O(n)
        - Order object: O(1)
        """
        self.update_price(tick)
        return Order(
            timestamp=tick.timestamp,
            symbol=tick.symbol,
            price=tick.price,
            action="ask" if tick.price > self.calculate_average(tick.symbol) else "bid",
            quantity=1,
        )