"""
generate_data.py
----------------
Generates realistic synthetic ride-hailing data for Bangalore.
Produces 3 CSV files:  data/raw/rides.csv, drivers.csv, zones.csv

Run:  python scripts/generate_data.py
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

N_RIDES    = 50_000
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 12, 31)

ZONES = [
    "Koramangala", "Indiranagar", "Whitefield", "Electronic City",
    "MG Road",     "HSR Layout",  "Jayanagar",  "Yeshwanthpur",
    "Hebbal",      "BTM Layout",  "Marathahalli","Bellandur"
]

ZONE_TYPES = {
    "Koramangala":    "Commercial",  "Indiranagar":     "Commercial",
    "Whitefield":     "Commercial",  "Electronic City": "Commercial",
    "MG Road":        "Transit",     "Yeshwanthpur":    "Transit",
    "Hebbal":         "Transit",     "HSR Layout":      "Residential",
    "Jayanagar":      "Residential", "BTM Layout":      "Residential",
    "Marathahalli":   "Residential", "Bellandur":       "Residential",
}

def sample_hour():
    """
    Simulates real-world ride demand with two daily peaks:
      - Morning rush:  7-10 AM (office commute)
      - Evening rush:  5-9 PM  (return commute + social)
    """
    weights = [
        1,  1, 0.5, 0.5, 0.5,  1,   # 0-5 AM   (very low demand)
        2,  5,  8,   7,   4,   3,   # 6-11 AM  (morning rush)
        4,  3,  3,   3,   4,   7,   # 12-5 PM  (moderate afternoon)
        9,  9,  8,   6,   4,   2,   # 6-11 PM  (evening rush)
    ]
    return random.choices(range(24), weights=weights, k=1)[0]

date_pool  = [START_DATE + timedelta(days=i)
              for i in range((END_DATE - START_DATE).days + 1)]
ride_dates = [random.choice(date_pool) for _ in range(N_RIDES)]

print("Generating rides...")
rides = pd.DataFrame({
    "ride_id":      range(1, N_RIDES + 1),
    "user_id":      np.random.randint(1000, 20000, N_RIDES),
    "driver_id":    np.random.randint(1, 5001,  N_RIDES),
    "pickup_zone":  [random.choice(ZONES) for _ in range(N_RIDES)],
    "dropoff_zone": [random.choice(ZONES) for _ in range(N_RIDES)],
    "ride_date":    ride_dates,
})

rides["ride_hour"]        = [sample_hour() for _ in range(N_RIDES)]
rides["day_of_week"]      = rides["ride_date"].apply(lambda d: d.strftime("%A"))
rides["is_weekend"]       = rides["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)
rides["distance_km"]      = np.round(
    np.random.exponential(scale=5, size=N_RIDES).clip(1, 30), 2
)
rides["duration_minutes"] = (
    rides["distance_km"] * np.random.uniform(3, 6, N_RIDES)
).astype(int)

# Fare model:  INR 15 base + INR 12/km + Gaussian noise
rides["fare_amount"] = np.round(
    15 + rides["distance_km"] * 12 + np.random.normal(0, 10, N_RIDES), 2
).clip(20)

rides["payment_mode"] = random.choices(
    ["UPI", "Cash", "Card"], weights=[55, 30, 15], k=N_RIDES
)
rides["ride_status"] = random.choices(
    ["Completed", "Cancelled", "No-driver"],
    weights=[80, 14, 6], k=N_RIDES
)

# Completed rides get higher ratings than cancelled ones
rides["rating"] = np.where(
    rides["ride_status"] == "Completed",
    np.random.choice([3.0, 3.5, 4.0, 4.5, 5.0], N_RIDES,
                     p=[0.05, 0.10, 0.25, 0.35, 0.25]),
    np.random.choice([1.0, 2.0, 2.5, 3.0], N_RIDES,
                     p=[0.40, 0.30, 0.20, 0.10])
)

print("Generating drivers...")
drivers = pd.DataFrame({
    "driver_id":    range(1, 5001),
    "city":         ["Bangalore"] * 5000,
    "vehicle_type": random.choices(["Bike", "Auto"], weights=[70, 30], k=5000),
    "join_date":    [
        START_DATE - timedelta(days=random.randint(0, 730))
        for _ in range(5000)
    ],
    "avg_rating":   np.round(np.random.normal(4.1, 0.4, 5000).clip(1, 5), 2),
})

zones = pd.DataFrame({
    "zone_id":   range(1, 13),
    "zone_name": ZONES,
    "city":      ["Bangalore"] * 12,
    "zone_type": [ZONE_TYPES[z] for z in ZONES],
})

os.makedirs("data/raw", exist_ok=True)
rides.to_csv("data/raw/rides.csv",     index=False)
drivers.to_csv("data/raw/drivers.csv", index=False)
zones.to_csv("data/raw/zones.csv",     index=False)

print(f"\n[OK] Generated {N_RIDES:,} rides")
print(f"[OK] Generated {len(drivers):,} drivers")
print(f"[OK] Generated {len(zones)} zones")
print(f"\nSample ride:\n{rides.head(3).to_string()}")
print("\nNext step: python scripts/clean_data.py")
