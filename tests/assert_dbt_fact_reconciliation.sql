WITH source_totals AS (

    SELECT
        COUNT(*) AS sales_lines,
        ROUND(SUM("Sales Amount"), 2) AS revenue,
        ROUND(SUM("Total Product Cost"), 2)
            AS product_cost,
        ROUND(
            SUM(
                "Sales Amount" - "Total Product Cost"
            ), 2
        ) AS gross_profit

    FROM {{ source('raw', 'sales') }}

),

fact_totals AS (

    SELECT
        COUNT(*) AS sales_lines,
        ROUND(SUM(revenue), 2) AS revenue,
        ROUND(SUM(total_product_cost), 2)
            AS product_cost,
        ROUND(SUM(gross_profit), 2)
            AS gross_profit

    FROM {{ ref('fact_sales') }}

)

SELECT
    f.sales_lines,
    f.revenue,
    f.product_cost,
    f.gross_profit

FROM fact_totals AS f
CROSS JOIN source_totals AS s

WHERE
    f.sales_lines IS DISTINCT FROM s.sales_lines
    OR f.revenue IS DISTINCT FROM s.revenue
    OR f.product_cost IS DISTINCT FROM s.product_cost
    OR f.gross_profit IS DISTINCT FROM s.gross_profit
