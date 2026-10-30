-- Calendar and fiscal date dimension.

WITH dates AS (

    SELECT *
    FROM {{ ref('stg_dates') }}

)

SELECT
    date_key,
    full_date,
    calendar_year,
    calendar_month,
    calendar_quarter,
    fiscal_year,
    fiscal_quarter,
    source_month,
    source_full_date,
    month_key

FROM dates
