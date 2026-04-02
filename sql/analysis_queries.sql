-- analysis_queries.sql
-- Ride Demand Analysis — Business SQL Queries
-- Run these inside notebooks/03_sql_analysis.ipynb using:
--   pd.read_sql(query, conn)


SELECT
    pickup_zone,
    COUNT(ride_id)             AS total_rides,
    ROUND(SUM(fare_amount), 0) AS total_revenue,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(rating), 2)     AS avg_rating
FROM rides
WHERE ride_status = 'Completed'
GROUP BY pickup_zone
ORDER BY total_revenue DESC;


SELECT
    ride_hour,
    COUNT(*) AS total_rides,
    SUM(CASE WHEN ride_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
    ROUND(
        100.0
        * SUM(CASE WHEN ride_status = 'Cancelled' THEN 1 ELSE 0 END)
        / COUNT(*)
    , 2) AS cancellation_rate_pct
FROM rides
GROUP BY ride_hour
ORDER BY cancellation_rate_pct DESC;


SELECT
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    COUNT(*)                    AS total_rides,
    ROUND(AVG(fare_amount), 2) AS avg_fare,
    ROUND(AVG(distance_km), 2) AS avg_distance_km,
    ROUND(AVG(rating), 2)     AS avg_rating
FROM rides
WHERE ride_status = 'Completed'
GROUP BY is_weekend;


SELECT
    r.driver_id,
    d.vehicle_type,
    COUNT(r.ride_id)                                              AS total_rides,
    ROUND(SUM(r.fare_amount), 0)                                 AS total_earnings,
    ROUND(AVG(r.rating), 2)                                     AS avg_rating,
    SUM(CASE WHEN r.ride_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancellations
FROM rides r
JOIN drivers d ON r.driver_id = d.driver_id
WHERE r.ride_status IN ('Completed', 'Cancelled')
GROUP BY r.driver_id, d.vehicle_type
HAVING total_rides > 10
ORDER BY total_earnings DESC
LIMIT 20;


SELECT
    pickup_zone,
    dropoff_zone,
    COUNT(*)                   AS ride_count,
    ROUND(AVG(distance_km), 2) AS avg_distance_km,
    ROUND(AVG(fare_amount), 2) AS avg_fare
FROM rides
WHERE ride_status = 'Completed'
GROUP BY pickup_zone, dropoff_zone
ORDER BY ride_count DESC
LIMIT 15;


SELECT
    STRFTIME('%Y-%m', ride_date) AS month,
    COUNT(*)                     AS total_rides,
    ROUND(SUM(fare_amount), 0)  AS monthly_revenue,
    ROUND(AVG(fare_amount), 2)  AS avg_fare
FROM rides
WHERE ride_status = 'Completed'
GROUP BY month
ORDER BY month;


SELECT
    payment_mode,
    COUNT(*) AS total_rides,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM rides WHERE ride_status = 'Completed')
    , 2) AS pct_of_total,
    ROUND(AVG(fare_amount), 2) AS avg_fare
FROM rides
WHERE ride_status = 'Completed'
GROUP BY payment_mode
ORDER BY total_rides DESC;
