#  I checked the Settingd.cfg,  and  the agent wrote a string as a sum of two integer variables which is wrong. it should be written in commas as a string

## What the agent got wrong

The agent initially patched the wear-percent calculation by switching from integer division
to float division, but left `needs_service` comparing the result with `>` instead of `>=`.
That meant a car sitting at exactly 80 % was not flagged — the test in `test_km_wachter.py`
for the boundary car passed only after I pointed this out and had the agent change the
comparison to `>=`.

The agent also tried to remove `flush_log` from `fleet_report.py` during the style
modernisation sweep, claiming it was "dead code". It is not — it writes the log file at the
end of every nightly run. I caught it by re-reading the call site before accepting the change.

## What I checked before I accepted its work

I ran `python verify.py` after every batch of changes. The specific checks I looked at
most carefully were:

- **`nearly_worn_car_is_flagged`** — I ran the check manually with a car at 12,000 km since
  service (exactly 80 %) and confirmed it returned `True` both in the verify script and by
  calling `km.needs_service` directly in the terminal.
- **`missing_reading_is_handled`** — I passed a car dict without `last_service_km` and
  confirmed the result was `False` (not flagged, not a `KeyError`).
- **`average_is_not_floored`** — I calculated the expected average by hand: car A is at
  14,900 / 15,000 = 99.33 %, car B is at 3,000 / 15,000 = 20.0 %. Mean = 59.67 %. The
  verify script confirmed the report returned 59.67 % after the fleet_utils bug was fixed.
- **Rules unchanged** — both `SERVICE_INTERVAL_KM == 15000` and `WARN_AT_PERCENT == 80`
  remained in `km_wachter.py` and in `settings.cfg` throughout.

All 11 checks in `verify.py` print PASS.

## What the data actually said

I ran a group-mean and correlation analysis on `fleet_history.csv` (120 cars, 26 that later
broke down, 94 that did not).

**The obvious answer — total mileage — turned out not to matter at all.**
Cars that broke down had an average odometer of 53,448 km. Cars that stayed healthy averaged
53,302 km. The difference is 146 km across a 120-car fleet. The Pearson correlation between
`odometer_km` and `broke_down` is 0.002 — indistinguishable from zero. Age in years tells
exactly the same story: correlation of –0.001. High-mileage, older cars are no more likely
to break down than low-mileage ones in this fleet.

**What does predict a breakdown:**

| Feature | Mean (ok) | Mean (broke) | Correlation |
|---|---|---|---|
| `km_since_service` | 7,261 km | 11,678 km | **0.404** |
| `avg_daily_km` | 131 km/day | 160 km/day | 0.252 |
| `load_factor` | 0.51 | 0.60 | 0.215 |
| `odometer_km` | 53,302 km | 53,448 km | 0.002 |
| `age_years` | 5.89 yrs | 5.88 yrs | –0.001 |

The strongest single predictor is **km since last service** — cars that broke down were on
average 61 % further into their service interval than cars that held up. In plain terms: the
risk is in how long since the last service, not in how old or how many kilometres the car has
in total.

**Daily usage intensity and load factor matter too**, but they are secondary. A car driven
hard every day with a high load factor is at moderate additional risk on top of the wear
interval, but neither factor alone explains breakdowns the way `km_since_service` does.

**Practical implication:** the 80 % rule is already tracking the right metric
(`km_since_service`). The improvement in `analyze.py` is to surface the cars that are
accumulating km-since-service unusually fast — high `avg_daily_km` combined with a high
`load_factor` — so the fleet team can prioritise them before they hit the 80 % threshold,
not just after.
