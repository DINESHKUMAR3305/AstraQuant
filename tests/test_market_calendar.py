from datetime import date

from astraquant.market_calendar import (
    is_nse_trading_day,
    next_nse_trading_day,
)


def test_weekend_is_not_trading_day():
    assert is_nse_trading_day(date(2026, 9, 5)) is False
    assert is_nse_trading_day(date(2026, 9, 6)) is False


def test_normal_weekday_is_trading_day():
    assert is_nse_trading_day(date(2026, 9, 4)) is True


def test_nse_holiday_is_not_trading_day():
    assert is_nse_trading_day(date(2026, 10, 2)) is False


def test_next_nse_trading_day_skips_weekend():
    result = next_nse_trading_day(date(2026, 9, 4))

    assert result == date(2026, 9, 7)


def test_next_nse_trading_day_skips_holiday():
    result = next_nse_trading_day(date(2026, 10, 1))

    assert result == date(2026, 10, 5)

def test_muhurat_trading_day_is_trading_day():
    assert is_nse_trading_day(date(2026, 11, 8)) is True


def test_diwali_balipratipada_is_holiday():
    assert is_nse_trading_day(date(2026, 11, 10)) is False
