-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- SPRINT 05 - GEOGRAPHIC AND PRICING INVESTIGATION
-- ============================================================

-- 1. Profitability by sales territory and channel.
-- Uses assigned sales territories, not customer addresses.

SELECT
    f.sales_channel,
    t.country,
    t.region,

    COUNT(*) AS sales_lines,

    ROUND(SUM(f.revenue), 2) AS revenue,

    ROUND(
        SUM(f.total_product_cost), 2
    ) AS product_cost,

    ROUND(
        SUM(f.gross_profit), 2
    ) AS gross_profit,

    ROUND(
        100 * SUM(f.gross_profit)
        / NULLIF(SUM(f.revenue), 0),
        2
    ) AS gross_margin_pct

FROM dbt_dev.fact_sales AS f

JOIN dbt_dev.dim_territory AS t
    ON f.territory_key = t.territory_key

GROUP BY
    f.sales_channel,
    t.country,
    t.region

ORDER BY
    f.sales_channel,
    gross_profit ASC;


-- 2. Reseller Bikes: most negative territories
-- during complete years 2018 and 2019.

SELECT
    d.calendar_year,
    t.country,
    t.region,

    COUNT(*) AS sales_lines,

    ROUND(SUM(f.revenue), 2) AS revenue,

    ROUND(
        SUM(f.gross_profit), 2
    ) AS gross_profit,

    COUNT(*) FILTER (
        WHERE f.gross_profit < 0
    ) AS loss_making_lines,

    ROUND(
        100 * SUM(f.gross_profit)
        / NULLIF(SUM(f.revenue), 0),
        2
    ) AS gross_margin_pct

FROM dbt_dev.fact_sales AS f

JOIN dbt_dev.dim_product AS p
    ON f.product_key = p.product_key

JOIN dbt_dev.dim_territory AS t
    ON f.territory_key = t.territory_key

JOIN dbt_dev.dim_date AS d
    ON f.order_date_key = d.date_key

WHERE
    f.sales_channel = 'Reseller'
    AND p.category = 'Bikes'
    AND d.calendar_year IN (2018, 2019)

GROUP BY
    d.calendar_year,
    t.country,
    t.region

HAVING SUM(f.gross_profit) < 0

ORDER BY
    d.calendar_year,
    gross_profit ASC;


-- 3. Reseller Bikes: observed formula differences.
-- A formula difference is a diagnostic metric,
-- not proof of a contractual discount.

SELECT
    d.calendar_year,

    COUNT(*) AS total_lines,

    COUNT(*) FILTER (
        WHERE ABS(f.formula_difference) > 0.02
    ) AS flagged_lines,

    ROUND(
        COALESCE(
            SUM(f.formula_difference) FILTER (
                WHERE ABS(f.formula_difference) > 0.02
            ),
            0
        ), 2
    ) AS formula_difference_amount,

    ROUND(
        COALESCE(
            SUM(f.gross_profit) FILTER (
                WHERE ABS(f.formula_difference) > 0.02
            ),
            0
        ), 2
    ) AS flagged_lines_gross_profit,

    ROUND(
        COALESCE(
            SUM(f.gross_profit) FILTER (
                WHERE ABS(f.formula_difference) <= 0.02
            ),
            0
        ), 2
    ) AS other_lines_gross_profit,

    ROUND(
        SUM(f.gross_profit), 2
    ) AS total_gross_profit

FROM dbt_dev.fact_sales AS f

JOIN dbt_dev.dim_product AS p
    ON f.product_key = p.product_key

JOIN dbt_dev.dim_date AS d
    ON f.order_date_key = d.date_key

WHERE
    f.sales_channel = 'Reseller'
    AND p.category = 'Bikes'
    AND d.calendar_year IN (2018, 2019)

GROUP BY d.calendar_year

ORDER BY d.calendar_year;

-- ============================================================
-- END
-- ============================================================
