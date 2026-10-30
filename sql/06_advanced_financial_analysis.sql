
-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- SPRINT 03 - ADVANCED FINANCIAL SQL
-- ============================================================

-- ============================================================
-- 1. MONTHLY FINANCIAL PERFORMANCE
-- CTE + WINDOW FUNCTIONS
-- ============================================================

WITH monthly_sales AS (
    SELECT
        DATE_TRUNC(
            'month',
            d.full_date
        )::DATE AS sales_month,

        f.sales_channel,

        COUNT(*) AS sales_lines,

        ROUND(SUM(f.revenue), 2) AS revenue,

        ROUND(
            SUM(f.total_product_cost), 2
        ) AS product_cost,

        ROUND(
            SUM(f.gross_profit), 2
        ) AS gross_profit

    FROM marts.fact_sales AS f

    JOIN marts.dim_date AS d
        ON f.order_date_key = d.date_key

    GROUP BY
        DATE_TRUNC('month', d.full_date),
        f.sales_channel
),

monthly_metrics AS (
    SELECT
        *,

        LAG(revenue) OVER (
            PARTITION BY sales_channel
            ORDER BY sales_month
        ) AS previous_month_revenue,

        SUM(revenue) OVER (
            PARTITION BY sales_channel
            ORDER BY sales_month
            ROWS BETWEEN UNBOUNDED PRECEDING
            AND CURRENT ROW
        ) AS cumulative_revenue

    FROM monthly_sales
)

SELECT
    sales_month,
    sales_channel,
    sales_lines,
    revenue,
    product_cost,
    gross_profit,

    ROUND(
        100 * gross_profit
        / NULLIF(revenue, 0),
        2
    ) AS gross_margin_pct,

    ROUND(
        100 * (
            revenue - previous_month_revenue
        ) / NULLIF(previous_month_revenue, 0),
        2
    ) AS month_over_month_growth_pct,

    cumulative_revenue

FROM monthly_metrics

ORDER BY
    sales_month,
    sales_channel;


-- ============================================================
-- 2. PRODUCT CATEGORY CONTRIBUTION
-- CTE + RANKING
-- ============================================================

WITH category_financials AS (
    SELECT
        f.sales_channel,
        p.category,

        COUNT(*) AS sales_lines,

        SUM(f.order_quantity) AS units_sold,

        SUM(f.revenue) AS revenue,

        SUM(f.gross_profit) AS gross_profit

    FROM marts.fact_sales AS f

    JOIN marts.dim_product AS p
        ON f.product_key = p.product_key

    GROUP BY
        f.sales_channel,
        p.category
),

category_metrics AS (
    SELECT
        *,

        SUM(revenue) OVER (
            PARTITION BY sales_channel
        ) AS channel_revenue,

        RANK() OVER (
            PARTITION BY sales_channel
            ORDER BY gross_profit DESC
        ) AS profitability_rank

    FROM category_financials
)

SELECT
    sales_channel,
    category,
    sales_lines,
    units_sold,

    ROUND(revenue, 2) AS revenue,
    ROUND(gross_profit, 2) AS gross_profit,

    ROUND(
        100 * gross_profit
        / NULLIF(revenue, 0),
        2
    ) AS gross_margin_pct,

    ROUND(
        100 * revenue
        / NULLIF(channel_revenue, 0),
        2
    ) AS revenue_contribution_pct,

    profitability_rank

FROM category_metrics

ORDER BY
    sales_channel,
    profitability_rank;


-- ============================================================
-- 3. TOP 10 PRODUCTS WITH GROSS LOSSES
-- AGGREGATION + BUSINESS RANKING
-- ============================================================

WITH product_financials AS (
    SELECT
        f.sales_channel,
        p.product_key,
        p.product_name,
        p.category,

        SUM(f.order_quantity) AS units_sold,

        SUM(f.revenue) AS revenue,

        SUM(f.total_product_cost) AS product_cost,

        SUM(f.gross_profit) AS gross_profit

    FROM marts.fact_sales AS f

    JOIN marts.dim_product AS p
        ON f.product_key = p.product_key

    GROUP BY
        f.sales_channel,
        p.product_key,
        p.product_name,
        p.category
),

loss_making_products AS (
    SELECT
        *,

        ROW_NUMBER() OVER (
            ORDER BY gross_profit ASC, product_key
        ) AS loss_rank

    FROM product_financials

    WHERE gross_profit < 0
)

SELECT
    loss_rank,
    sales_channel,
    product_key,
    product_name,
    category,
    units_sold,

    ROUND(revenue, 2) AS revenue,

    ROUND(product_cost, 2) AS product_cost,

    ROUND(gross_profit, 2) AS gross_profit,

    ROUND(
        100 * gross_profit
        / NULLIF(revenue, 0),
        2
    ) AS gross_margin_pct

FROM loss_making_products

WHERE loss_rank <= 10

ORDER BY loss_rank;

-- ============================================================
-- END
-- ============================================================
