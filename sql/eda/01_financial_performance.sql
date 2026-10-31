-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- SPRINT 05 - FINANCIAL PERFORMANCE EXPLORATION
-- ============================================================

-- 1. Overall financial performance by channel.

SELECT
    f.sales_channel,
    COUNT(*) AS sales_lines,
    SUM(f.order_quantity) AS units_sold,
    ROUND(SUM(f.revenue), 2) AS revenue,
    ROUND(SUM(f.total_product_cost), 2)
        AS product_cost,
    ROUND(SUM(f.gross_profit), 2)
        AS gross_profit,
    ROUND(
        100 * SUM(f.gross_profit)
        / NULLIF(SUM(f.revenue), 0),
        2
    ) AS gross_margin_pct

FROM dbt_dev.fact_sales AS f

GROUP BY f.sales_channel
ORDER BY revenue DESC;


-- 2. Compare full calendar years only.

SELECT
    d.calendar_year,
    f.sales_channel,
    COUNT(*) AS sales_lines,
    ROUND(SUM(f.revenue), 2) AS revenue,
    ROUND(SUM(f.total_product_cost), 2)
        AS product_cost,
    ROUND(SUM(f.gross_profit), 2)
        AS gross_profit,
    ROUND(
        100 * SUM(f.gross_profit)
        / NULLIF(SUM(f.revenue), 0),
        2
    ) AS gross_margin_pct

FROM dbt_dev.fact_sales AS f

JOIN dbt_dev.dim_date AS d
    ON f.order_date_key = d.date_key

WHERE d.calendar_year IN (2018, 2019)

GROUP BY
    d.calendar_year,
    f.sales_channel

ORDER BY
    d.calendar_year,
    f.sales_channel;


-- 3. Complete monthly calendar for 2018 and 2019.

WITH calendar_months AS (

    SELECT
        GENERATE_SERIES(
            DATE '2018-01-01',
            DATE '2019-12-01',
            INTERVAL '1 month'
        )::DATE AS sales_month

),

channels AS (

    SELECT DISTINCT
        sales_channel
    FROM dbt_dev.fact_sales

),

monthly_sales AS (

    SELECT
        DATE_TRUNC(
            'month', d.full_date
        )::DATE AS sales_month,

        f.sales_channel,
        COUNT(*) AS sales_lines,
        SUM(f.revenue) AS revenue,
        SUM(f.gross_profit) AS gross_profit

    FROM dbt_dev.fact_sales AS f

    JOIN dbt_dev.dim_date AS d
        ON f.order_date_key = d.date_key

    WHERE d.full_date >= DATE '2018-01-01'
      AND d.full_date < DATE '2020-01-01'

    GROUP BY 1, 2

),

complete_months AS (

    SELECT
        c.sales_month,
        ch.sales_channel,
        COALESCE(m.sales_lines, 0)
            AS sales_lines,
        COALESCE(m.revenue, 0)
            AS revenue,
        COALESCE(m.gross_profit, 0)
            AS gross_profit

    FROM calendar_months AS c

    CROSS JOIN channels AS ch

    LEFT JOIN monthly_sales AS m
        ON c.sales_month = m.sales_month
       AND ch.sales_channel = m.sales_channel

)

SELECT
    sales_month,
    sales_channel,
    sales_lines,
    ROUND(revenue, 2) AS revenue,
    ROUND(gross_profit, 2) AS gross_profit,

    CASE
        WHEN sales_lines = 0
        THEN 'NO RECORDED SALES'
        ELSE 'HAS SALES'
    END AS period_status

FROM complete_months

ORDER BY
    sales_month,
    sales_channel;

-- ============================================================
-- END
-- ============================================================
