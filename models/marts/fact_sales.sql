-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- DBT FACT MODEL: SALES
--
-- Grain: one row per sales_order_line_key.
-- Preserves recorded financial values.
-- ============================================================

WITH sales AS (

    SELECT *
    FROM {{ ref('stg_sales') }}

),

orders AS (

    SELECT *
    FROM {{ ref('stg_orders') }}

),

joined AS (

    SELECT
        s.sales_order_line_key,

        o.sales_order,
        o.sales_order_line,
        o.sales_channel,

        s.product_key,
        s.customer_key,
        s.reseller_key,
        s.territory_key,

        s.order_date_key,
        s.due_date_key,
        s.ship_date_key,

        s.order_quantity,
        s.unit_price,
        s.extended_amount,
        s.declared_discount_pct,

        s.unit_standard_cost,
        s.total_product_cost,
        s.revenue

    FROM sales AS s

    INNER JOIN orders AS o
        ON s.sales_order_line_key =
           o.sales_order_line_key

),

final AS (

    SELECT
        *,

        revenue - total_product_cost
            AS gross_profit,

        (
            extended_amount
            * (1 - declared_discount_pct)
            - revenue
        ) AS formula_difference,

        CASE
            WHEN extended_amount > 0
            THEN
                (extended_amount - revenue)
                / extended_amount
            ELSE NULL
        END AS effective_reduction_rate,

        (revenue - total_product_cost) < 0
            AS is_negative_gross_profit

    FROM joined

)

SELECT *
FROM final
