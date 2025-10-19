import numpy as np
import pandas as pd
import pytest
from src.backtester.strategy import WindowedMovingAverageStrategy
from src.backtester.broker import Broker


@pytest.fixture
def prices():
    return pd.Series(np.linspace(100, 120, 200))


@pytest.fixture
def strategy():
    return WindowedMovingAverageStrategy(20)


@pytest.fixture
def broker():
    return Broker(cash=1_000)
