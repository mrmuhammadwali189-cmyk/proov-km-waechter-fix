# fleet_utils.py
# Helpers for Vossberg Mobility fleet calculations.
# Written in 2013. Modernized 2024: fixed km-to-miles conversion, removed dead code.

KM_PER_MILE = 1.60934  # 1 mile = 1.60934 km


def km_to_miles(km: float) -> float:
    """Convert kilometres to miles.

    The original constant (1.609) was used as a multiplier, which is wrong —
    1.609 is km-per-mile, not miles-per-km. Dividing by KM_PER_MILE gives the
    correct result: 100 km → 62.1 miles, not 160.9.
    Used by the nightly run for the UK partner report.
    """
    return km / KM_PER_MILE


def format_number(value: float) -> str:
    """Format a number to one decimal place."""
    return f"{value:.1f}"


def format_percent(value: float) -> str:
    """Format a value as a whole-number percentage string."""
    return f"{int(value)}%"


def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a list, or 0 for an empty list."""
    if not values:
        return 0
    return sum(values) / len(values)
