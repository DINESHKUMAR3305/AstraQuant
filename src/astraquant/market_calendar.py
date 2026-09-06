from datetime import date, timedelta


# NSE trading holidays for 2026.
# This list should be updated when the official NSE calendar
# for the next year is published.
NSE_HOLIDAYS_2026 = {
    date(2026, 1, 15),   # Municipal Corporation Election in Maharashtra
    date(2026, 1, 26),   # Republic Day
    date(2026, 2, 19),   # Chhatrapati Shivaji Maharaj Jayanti
    date(2026, 3, 3),    # Holi
    date(2026, 3, 19),   # Gudhi Padwa
    date(2026, 3, 26),   # Ram Navami
    date(2026, 3, 31),   # Mahavir Jayanti
    date(2026, 4, 1),    # Annual Bank Closing
    date(2026, 4, 3),    # Good Friday
    date(2026, 4, 14),   # Dr. Ambedkar Jayanti
    date(2026, 5, 1),    # Maharashtra Day / Buddha Pournima
    date(2026, 5, 28),   # Bakri Id
    date(2026, 6, 26),   # Muharram
    date(2026, 8, 26),   # Id-E-Milad
    date(2026, 9, 14),   # Ganesh Chaturthi
    date(2026, 10, 2),   # Gandhi Jayanti
    date(2026, 10, 20),  # Dussehra
    date(2026, 11, 10),  # Diwali-Balipratipada
    date(2026, 11, 24),  # Guru Nanak Jayanti
    date(2026, 12, 25),  # Christmas
}
NSE_SPECIAL_TRADING_DAYS_2026 = {
    date(2026, 11, 8),
}


def is_nse_trading_day(trading_date: date) -> bool:
    """Return True when the date is normally an NSE trading day."""
    
    if trading_date in NSE_SPECIAL_TRADING_DAYS_2026:
        return True
    
    if trading_date.weekday() >= 5:
        return False

    if trading_date in NSE_HOLIDAYS_2026:
        return False

    return True


def next_nse_trading_day(start_date: date) -> date:
    """Return the next NSE trading day after the supplied date."""

    trading_date = start_date + timedelta(days=1)

    while not is_nse_trading_day(trading_date):
        trading_date += timedelta(days=1)

    return trading_date
