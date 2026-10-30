
-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- DBT STAGING MODEL: ORDERS
--
-- Grain: one record per SalesOrderLineKey.
-- Source: raw.orders
-- ============================================================

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'orders') }}

),

renamed AS (

    SELECT
        "SalesOrderLineKey" AS sales_order_line_key,

        "Sales Order" AS sales_order,
        "Sales Order Line" AS sales_order_line,
        "Channel" AS sales_channel

    FROM source_data

)

SELECT *
FROM renamed
