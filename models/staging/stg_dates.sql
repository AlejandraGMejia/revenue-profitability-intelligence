
-- Date staging model.
-- Preserves the fiscal calendar from the source.
-- Calendar components are derived from the real date.

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'dates') }}

),

renamed AS (

    SELECT
        "DateKey" AS date_key,
        "Date" AS full_date,

        EXTRACT(YEAR FROM "Date")::INTEGER
            AS calendar_year,

        EXTRACT(MONTH FROM "Date")::INTEGER
            AS calendar_month,

        EXTRACT(QUARTER FROM "Date")::INTEGER
            AS calendar_quarter,

        "Fiscal Year" AS fiscal_year,
        "Fiscal Quarter" AS fiscal_quarter,
        "Month" AS source_month,
        "Full Date" AS source_full_date,
        "MonthKey" AS month_key

    FROM source_data

)

SELECT *
FROM renamed
