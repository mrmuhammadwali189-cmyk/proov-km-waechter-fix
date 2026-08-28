# fleet_report.py
# Prints the nightly fleet-health summary for Vossberg Mobility.
# Written in 2014. Modernized 2024.

from km_wachter import wear_percent, needs_service, SERVICE_INTERVAL_KM
from config_loader import load_settings, get_setting
from log_util import log, flush_log
import fleet_utils


def car_wear(car: dict) -> float:
    """Return the wear percentage for a single car.

    Falls back to the car's own odometer value when 'last_service_km' is absent,
    so 0 km since service is assumed instead of crashing.
    """
    last = car.get("last_service_km", car["odometer"])
    return wear_percent(car["odometer"] - last, SERVICE_INTERVAL_KM)


def fleet_summary(fleet: list[dict]) -> dict:
    """Return a summary dict with count, due count, average wear, and total km.

    Returns zeroed values for an empty fleet rather than raising ZeroDivisionError.
    """
    wear_values = [car_wear(car) for car in fleet]
    due = sum(1 for car in fleet if needs_service(car))
    total_km = sum(car["odometer"] for car in fleet)
    return {
        "count": len(fleet),
        "due": due,
        "average_wear": fleet_utils.mean(wear_values),
        "total_km": total_km,
    }


def print_report(fleet: list[dict]) -> None:
    """Print and log the nightly fleet-health report."""
    settings = load_settings()
    log(get_setting(settings, "report_title", "Nightly fleet report"))
    s = fleet_summary(fleet)
    print(f"Fleet: {s['count']} cars")
    print(f"Due for service: {s['due']}")
    print(f"Average wear: {fleet_utils.format_percent(s['average_wear'])}")
    total_miles = fleet_utils.km_to_miles(s["total_km"])
    # The partner garage in England wants the distance in miles (since 2015).
    print(f"Fleet distance: {fleet_utils.format_number(total_miles)} miles")
    flush_log(get_setting(settings, "log_file", "km_wachter.log"))
