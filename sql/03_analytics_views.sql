CREATE OR REPLACE VIEW analytics.traffic_performance AS

SELECT
    COALESCE(
        NULLIF(TRIM(traffic_density), ''),
        'Unknown'
    ) AS traffic_density,

    COUNT(*) AS total_orders,

    ROUND(
        AVG(delivery_time_minutes)::NUMERIC,
        2
    ) AS avg_delivery_minutes,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delivery_time_minutes > 30
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS pct_over_30_minutes

FROM staging.delivery_orders

GROUP BY 1;


CREATE OR REPLACE VIEW analytics.city_performance AS

SELECT
    COALESCE(
        NULLIF(TRIM(city), ''),
        'Unknown'
    ) AS City,

    COUNT(*) AS total_orders,

    ROUND(
        AVG(delivery_time_minutes)::NUMERIC,
        2
    ) AS avg_delivery_minutes,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE delivery_time_minutes > 30
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS pct_over_30_minutes

FROM staging.delivery_orders

GROUP BY 1;
