
-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- DBT STAGING MODEL: SALES
--
-- Grain: one row per SalesOrderLineKey.
-- Source: raw.sales
--
-- This model renames source columns and preserves
-- their original values and numeric precision.
-- ============================================================

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'sales') }}

),

renamed AS (

    SELECT
        "SalesOrderLineKey" AS sales_order_line_key,

        "ProductKey" AS product_key,
        "CustomerKey" AS customer_key,
        "ResellerKey" AS reseller_key,
        "SalesTerritoryKey" AS territory_key,

        "OrderDateKey" AS order_date_key,
        "DueDateKey" AS due_date_key,
        "ShipDateKey" AS ship_date_key,

        "Order Quantity" AS order_quantity,
        "Unit Price" AS unit_price,
        "Extended Amount" AS extended_amount,

        "Unit Price Discount Pct"
            AS declared_discount_pct,

        "Product Standard Cost"
            AS unit_standard_cost,

        "Total Product Cost"
            AS total_product_cost,

        "Sales Amount" AS revenue

    FROM source_data

)

SELECT *
FROM renamed
