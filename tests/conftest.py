import numpy as np
import pandas as pd
import pytest
from backtester.strategy import WindowedMovingAverageStrategy
from backtester.broker import Broker


@pytest.fixture
def prices():
    # deterministic rising series
    return pd.Series(np.linspace(100, 120, 200))


@pytest.fixture
def strategy():
    return WindowedMovingAverageStrategy(20)


@pytest.fixture
def broker():
    return Broker(cash=1_000)
