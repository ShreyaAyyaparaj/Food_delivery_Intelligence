
SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE order_id IS NULL
    ) AS missing_order_ids,

    COUNT(*) FILTER (
        WHERE delivery_time_minutes IS NULL
    ) AS missing_delivery_times,

    COUNT(*) FILTER (
        WHERE delivery_time_minutes <= 0
    ) AS invalid_delivery_times,

    COUNT(*) FILTER (
        WHERE order_datetime IS NULL
    ) AS missing_order_timestamps,

    COUNT(*) FILTER (
        WHERE delivery_person_age < 18
           OR delivery_person_age > 100
    ) AS suspicious_delivery_person_ages

FROM staging.delivery_orders;
