-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- SPRINT 05 - PRODUCT MIX ANALYSIS
-- ============================================================

-- 1. Product category performance by year and channel.

WITH category_performance AS (

    SELECT
        d.calendar_year,
        f.sales_channel,
        p.category,

        COUNT(*) AS sales_lines,
        SUM(f.order_quantity) AS units_sold,
        SUM(f.revenue) AS revenue,
        SUM(f.gross_profit) AS gross_profit

    FROM dbt_dev.fact_sales AS f

    JOIN dbt_dev.dim_date AS d
        ON f.order_date_key = d.date_key

    JOIN dbt_dev.dim_product AS p
        ON f.product_key = p.product_key

    WHERE d.calendar_year IN (2018, 2019)

    GROUP BY
        d.calendar_year,
        f.sales_channel,
        p.category

),

category_metrics AS (

    SELECT
        *,

        SUM(sales_lines) OVER (
            PARTITION BY calendar_year, sales_channel
        ) AS channel_lines,

        SUM(revenue) OVER (
            PARTITION BY calendar_year, sales_channel
        ) AS channel_revenue

    FROM category_performance

)

SELECT
    calendar_year,
    sales_channel,
    category,
    sales_lines,
    units_sold,

    ROUND(revenue, 2) AS revenue,
    ROUND(gross_profit, 2) AS gross_profit,

    ROUND(
        revenue / NULLIF(sales_lines, 0),
        2
    ) AS revenue_per_line,

    ROUND(
        100.0 * sales_lines
        / NULLIF(channel_lines, 0),
        2
    ) AS line_share_pct,

    ROUND(
        100.0 * revenue
        / NULLIF(channel_revenue, 0),
        2
    ) AS revenue_share_pct,

    ROUND(
        100.0 * gross_profit
        / NULLIF(revenue, 0),
        2
    ) AS gross_margin_pct

FROM category_metrics

ORDER BY
    calendar_year,
    sales_channel,
    revenue DESC;


-- 2. Internet yearly mix and average value per line.

SELECT
    d.calendar_year,

    COUNT(*) AS sales_lines,

    SUM(f.order_quantity) AS units_sold,

    ROUND(
        SUM(f.revenue), 2
    ) AS revenue,

    ROUND(
        SUM(f.revenue) / NULLIF(COUNT(*), 0),
        2
    ) AS avg_revenue_per_line,

    COUNT(*) FILTER (
        WHERE p.category = 'Bikes'
    ) AS bike_lines,

    COUNT(*) FILTER (
        WHERE p.category = 'Accessories'
    ) AS accessory_lines,

    COUNT(*) FILTER (
        WHERE p.category = 'Clothing'
    ) AS clothing_lines

FROM dbt_dev.fact_sales AS f

JOIN dbt_dev.dim_date AS d
    ON f.order_date_key = d.date_key

JOIN dbt_dev.dim_product AS p
    ON f.product_key = p.product_key

WHERE
    d.calendar_year IN (2018, 2019)
    AND f.sales_channel = 'Internet'

GROUP BY d.calendar_year

ORDER BY d.calendar_year;


-- 3. Annual Reseller Bikes financial performance.

SELECT
    d.calendar_year,

    COUNT(*) AS sales_lines,

    SUM(f.order_quantity) AS units_sold,

    ROUND(SUM(f.revenue), 2) AS revenue,

    ROUND(
        SUM(f.total_product_cost), 2
    ) AS product_cost,

    ROUND(
        SUM(f.gross_profit), 2
    ) AS gross_profit,

    COUNT(*) FILTER (
        WHERE f.gross_profit < 0
    ) AS negative_profit_lines,

    ROUND(
        100.0 * SUM(f.gross_profit)
        / NULLIF(SUM(f.revenue), 0),
        2
    ) AS gross_margin_pct

FROM dbt_dev.fact_sales AS f

JOIN dbt_dev.dim_date AS d
    ON f.order_date_key = d.date_key

JOIN dbt_dev.dim_product AS p
    ON f.product_key = p.product_key

WHERE
    d.calendar_year IN (2018, 2019)
    AND f.sales_channel = 'Reseller'
    AND p.category = 'Bikes'

GROUP BY d.calendar_year

ORDER BY d.calendar_year;

-- ============================================================
-- END
-- ============================================================
