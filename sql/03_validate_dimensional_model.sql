
-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- SPRINT 03 - DIMENSIONAL MODEL VALIDATION
-- ============================================================

-- 1. Verify sales grain and uniqueness.

SELECT
    COUNT(*) AS total_sales_lines,
    COUNT(DISTINCT "SalesOrderLineKey") AS unique_lines,
    COUNT(*) - COUNT(DISTINCT "SalesOrderLineKey")
        AS duplicate_lines
FROM raw.sales;


-- 2. Validate channel-specific customer and reseller keys.

SELECT
    o."Channel" AS channel,
    COUNT(*) AS sales_lines,

    COUNT(*) FILTER (
        WHERE s."CustomerKey" = -1
    ) AS unknown_customer_keys,

    COUNT(*) FILTER (
        WHERE s."ResellerKey" = -1
    ) AS unknown_reseller_keys,

    COUNT(*) FILTER (
        WHERE s."CustomerKey" <> -1
          AND s."ResellerKey" <> -1
    ) AS both_keys_present,

    COUNT(*) FILTER (
        WHERE s."CustomerKey" = -1
          AND s."ResellerKey" = -1
    ) AS both_keys_placeholder

FROM raw.sales AS s
JOIN raw.orders AS o
    ON s."SalesOrderLineKey" = o."SalesOrderLineKey"
GROUP BY o."Channel"
ORDER BY o."Channel";


-- 3. Check physical existence of placeholder dimension keys.

SELECT
    'customers' AS dimension,
    COUNT(*) AS placeholder_rows
FROM raw.customers
WHERE "CustomerKey" = -1

UNION ALL

SELECT
    'resellers' AS dimension,
    COUNT(*) AS placeholder_rows
FROM raw.resellers
WHERE "ResellerKey" = -1;


-- 4. Validate relationships with applicable dimensions.

SELECT
    COUNT(*) FILTER (
        WHERE p."ProductKey" IS NULL
    ) AS missing_products,

    COUNT(*) FILTER (
        WHERE c."CustomerKey" IS NULL
          AND s."CustomerKey" <> -1
    ) AS missing_applicable_customers,

    COUNT(*) FILTER (
        WHERE r."ResellerKey" IS NULL
          AND s."ResellerKey" <> -1
    ) AS missing_applicable_resellers,

    COUNT(*) FILTER (
        WHERE t."SalesTerritoryKey" IS NULL
    ) AS missing_territories

FROM raw.sales AS s

LEFT JOIN raw.products AS p
    ON s."ProductKey" = p."ProductKey"

LEFT JOIN raw.customers AS c
    ON s."CustomerKey" = c."CustomerKey"

LEFT JOIN raw.resellers AS r
    ON s."ResellerKey" = r."ResellerKey"

LEFT JOIN raw.territories AS t
    ON s."SalesTerritoryKey" = t."SalesTerritoryKey";


-- 5. Verify distinct orders versus order lines.

SELECT
    o."Channel",
    COUNT(*) AS sales_lines,
    COUNT(DISTINCT o."Sales Order") AS distinct_orders,
    ROUND(
        COUNT(*)::NUMERIC
        / NULLIF(COUNT(DISTINCT o."Sales Order"), 0),
        2
    ) AS avg_lines_per_order

FROM raw.orders AS o
GROUP BY o."Channel"
ORDER BY o."Channel";


-- 6. Calculate financial totals by channel.

WITH channel_financials AS (
    SELECT
        o."Channel" AS channel,
        SUM(s."Sales Amount") AS revenue,
        SUM(s."Total Product Cost") AS product_cost

    FROM raw.sales AS s

    JOIN raw.orders AS o
        ON s."SalesOrderLineKey" = o."SalesOrderLineKey"

    GROUP BY o."Channel"
)

SELECT
    channel,
    ROUND(revenue, 2) AS revenue,
    ROUND(product_cost, 2) AS product_cost,
    ROUND(revenue - product_cost, 2) AS gross_profit,
    ROUND(
        100 * (revenue - product_cost)
        / NULLIF(revenue, 0),
        2
    ) AS gross_margin_pct

FROM channel_financials
ORDER BY channel;


-- 7. Verify financial totals across all channels.

SELECT
    COUNT(*) AS sales_lines,
    ROUND(SUM("Sales Amount"), 2) AS total_revenue,
    ROUND(SUM("Total Product Cost"), 2) AS total_cost,
    ROUND(
        SUM("Sales Amount" - "Total Product Cost"),
        2
    ) AS total_gross_profit
FROM raw.sales;

-- ============================================================
-- END
-- ============================================================
