"""
clean_data.py
-------------
Loads raw rides.csv, applies cleaning + feature engineering,
and saves data/processed/rides_clean.csv

Run:  python scripts/clean_data.py
"""

import pandas as pd
import numpy as np
import os

rides   = pd.read_csv("data/raw/rides.csv",   parse_dates=["ride_date"])
drivers = pd.read_csv("data/raw/drivers.csv", parse_dates=["join_date"])

print(f"Shape          : {rides.shape}")
print(f"Null values    :\n{rides.isnull().sum()}")
print(f"Duplicate rows : {rides.duplicated().sum()}")
print(f"Ride statuses  : {rides['ride_status'].value_counts().to_dict()}")

before = len(rides)
rides.drop_duplicates(subset="ride_id", inplace=True)
print(f"\n[STEP 1] Duplicates removed : {before - len(rides)}")

low_fare_count = (rides["fare_amount"] < 20).sum()
rides.loc[rides["fare_amount"] < 20, "fare_amount"] = 20.0
print(f"[STEP 2] Fares floored to INR 20 : {low_fare_count} rows")

invalid_hours = (~rides["ride_hour"].between(0, 23)).sum()
assert invalid_hours == 0, f"Found {invalid_hours} rows with invalid hour!"
print(f"[STEP 3] Hour validation passed  : all values in 0-23")

same_zone_mask = rides["pickup_zone"] == rides["dropoff_zone"]
print(f"[STEP 4] Same-zone rides removed : {same_zone_mask.sum()}")
rides = rides[~same_zone_mask].copy()

print("\n[STEP 5] Engineering features...")

def get_time_bucket(hour: int) -> str:
    """
    Groups hours into named business windows.
    Makes analysis and charts more readable for stakeholders.
    """
    if   0  <= hour < 6:  return "Late Night"
    elif 6  <= hour < 10: return "Morning Rush"
    elif 10 <= hour < 13: return "Midday"
    elif 13 <= hour < 17: return "Afternoon"
    elif 17 <= hour < 21: return "Evening Rush"
    else:                 return "Night"

rides["time_bucket"] = rides["ride_hour"].apply(get_time_bucket)
rides["month"]       = rides["ride_date"].dt.month
rides["month_name"]  = rides["ride_date"].dt.strftime("%b")
rides["week"]        = rides["ride_date"].dt.isocalendar().week.astype(int)
rides["fare_per_km"] = (rides["fare_amount"] / rides["distance_km"]).round(2)

print(f"  + time_bucket  : {rides['time_bucket'].value_counts().to_dict()}")
print(f"  + month        : {rides['month'].min()} to {rides['month'].max()}")
print(f"  + fare_per_km  : mean = INR {rides['fare_per_km'].mean():.2f}/km")

os.makedirs("data/processed", exist_ok=True)
rides.to_csv("data/processed/rides_clean.csv", index=False)

print(f"Final shape : {rides.shape}")
print(f"Completion  : {(rides['ride_status']=='Completed').mean():.1%}")
print(f"Cancellation: {(rides['ride_status']=='Cancelled').mean():.1%}")
print(f"Saved to    : data/processed/rides_clean.csv")
print("\nNext step: jupyter notebook")
