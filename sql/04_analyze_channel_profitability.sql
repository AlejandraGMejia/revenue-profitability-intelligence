
-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- SPRINT 03 - CHANNEL PROFITABILITY INVESTIGATION
-- ============================================================

-- 1. Line-level profitability by channel

WITH sales_analysis AS (
    SELECT
        o."Channel" AS channel,
        s."Sales Amount" AS revenue,
        s."Total Product Cost" AS product_cost,
        (
            s."Sales Amount" - s."Total Product Cost"
        ) AS gross_profit
    FROM raw.sales AS s
    JOIN raw.orders AS o
        ON s."SalesOrderLineKey" =
           o."SalesOrderLineKey"
)

SELECT
    channel,
    COUNT(*) AS sales_lines,

    COUNT(*) FILTER (
        WHERE gross_profit < 0
    ) AS negative_profit_lines,

    COUNT(*) FILTER (
        WHERE gross_profit = 0
    ) AS zero_profit_lines,

    COUNT(*) FILTER (
        WHERE gross_profit > 0
    ) AS positive_profit_lines,

    ROUND(SUM(revenue), 2) AS revenue,

    ROUND(SUM(gross_profit), 2) AS gross_profit,

    ROUND(
        100 * SUM(gross_profit)
        / NULLIF(SUM(revenue), 0),
        2
    ) AS gross_margin_pct

FROM sales_analysis
GROUP BY channel
ORDER BY channel;


-- 2. Financial performance by product category

SELECT
    o."Channel" AS channel,
    p."Category" AS category,

    COUNT(*) AS sales_lines,

    SUM(s."Order Quantity") AS units_sold,

    ROUND(
        SUM(s."Sales Amount"), 2
    ) AS revenue,

    ROUND(
        SUM(s."Total Product Cost"), 2
    ) AS product_cost,

    ROUND(
        SUM(
            s."Sales Amount" - s."Total Product Cost"
        ), 2
    ) AS gross_profit,

    ROUND(
        100 * SUM(
            s."Sales Amount" - s."Total Product Cost"
        ) / NULLIF(SUM(s."Sales Amount"), 0),
        2
    ) AS gross_margin_pct

FROM raw.sales AS s

JOIN raw.orders AS o
    ON s."SalesOrderLineKey" =
       o."SalesOrderLineKey"

JOIN raw.products AS p
    ON s."ProductKey" = p."ProductKey"

GROUP BY
    o."Channel",
    p."Category"

ORDER BY
    o."Channel",
    revenue DESC;


-- 3. Effective commercial reductions by channel

WITH reduction_analysis AS (
    SELECT
        o."Channel" AS channel,
        s."Extended Amount" AS extended_amount,
        s."Sales Amount" AS sales_amount,

        (
            s."Extended Amount"
            * (1 - s."Unit Price Discount Pct")
            - s."Sales Amount"
        ) AS unexplained_reduction

    FROM raw.sales AS s

    JOIN raw.orders AS o
        ON s."SalesOrderLineKey" =
           o."SalesOrderLineKey"
)

SELECT
    channel,

    COUNT(*) FILTER (
        WHERE ABS(unexplained_reduction) > 0.02
    ) AS flagged_lines,

    ROUND(
        SUM(unexplained_reduction) FILTER (
            WHERE ABS(unexplained_reduction) > 0.02
        ), 2
    ) AS total_flagged_reduction,

    ROUND(
        SUM(extended_amount), 2
    ) AS total_extended_amount,

    ROUND(
        SUM(sales_amount), 2
    ) AS recorded_revenue

FROM reduction_analysis

GROUP BY channel
ORDER BY channel;

-- ============================================================
-- END
-- ============================================================
