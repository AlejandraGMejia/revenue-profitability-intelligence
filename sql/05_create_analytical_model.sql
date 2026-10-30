
-- ============================================================
-- REVENUE & PROFITABILITY INTELLIGENCE
-- SPRINT 03 - ANALYTICAL STAR SCHEMA
-- ============================================================

BEGIN;

-- 1. Create analytical schema.

CREATE SCHEMA IF NOT EXISTS marts;

COMMENT ON SCHEMA marts IS
'Financial analytical models for business intelligence';


-- ============================================================
-- DIMENSION: PRODUCTS
-- ============================================================

CREATE OR REPLACE VIEW marts.dim_product AS

SELECT
    "ProductKey" AS product_key,
    "SKU" AS product_sku,
    "Product" AS product_name,
    "Standard Cost" AS standard_cost,
    "Color" AS product_color,
    "List Price" AS list_price,
    "Model" AS product_model,
    "Subcategory" AS subcategory,
    "Category" AS category

FROM raw.products;


-- ============================================================
-- DIMENSION: CUSTOMERS
-- ============================================================

CREATE OR REPLACE VIEW marts.dim_customer AS

SELECT
    "CustomerKey" AS customer_key,
    "Customer ID" AS customer_id,
    "Customer" AS customer_name,
    "City" AS city,
    "State-Province" AS state_province,
    "Country-Region" AS country_region,
    "Postal Code" AS postal_code

FROM raw.customers;


-- ============================================================
-- DIMENSION: RESELLERS
-- ============================================================

CREATE OR REPLACE VIEW marts.dim_reseller AS

SELECT
    "ResellerKey" AS reseller_key,
    "Reseller ID" AS reseller_id,
    "Business Type" AS business_type,
    "Reseller" AS reseller_name,
    "City" AS city,
    "State-Province" AS state_province,
    "Country-Region" AS country_region,
    "Postal Code" AS postal_code

FROM raw.resellers;


-- ============================================================
-- DIMENSION: DATES
-- ============================================================

CREATE OR REPLACE VIEW marts.dim_date AS

SELECT
    "DateKey" AS date_key,
    "Date" AS full_date,
    EXTRACT(YEAR FROM "Date")::INTEGER
        AS calendar_year,
    EXTRACT(MONTH FROM "Date")::INTEGER
        AS calendar_month,
    EXTRACT(QUARTER FROM "Date")::INTEGER
        AS calendar_quarter,
    "Fiscal Year" AS fiscal_year,
    "Fiscal Quarter" AS fiscal_quarter,
    "Month" AS source_month,
    "Full Date" AS source_full_date,
    "MonthKey" AS month_key

FROM raw.dates;


-- ============================================================
-- DIMENSION: SALES TERRITORIES
-- ============================================================

CREATE OR REPLACE VIEW marts.dim_territory AS

SELECT
    "SalesTerritoryKey" AS territory_key,
    "Region" AS region,
    "Country" AS country,
    "Group" AS territory_group

FROM raw.territories;


-- ============================================================
-- FACT TABLE: SALES
-- Grain: one row per sales order line.
-- ============================================================

CREATE OR REPLACE VIEW marts.fact_sales AS

SELECT
    s."SalesOrderLineKey" AS sales_order_line_key,

    o."Sales Order" AS sales_order,
    o."Sales Order Line" AS sales_order_line,
    o."Channel" AS sales_channel,

    s."ProductKey" AS product_key,
    s."CustomerKey" AS customer_key,
    s."ResellerKey" AS reseller_key,
    s."SalesTerritoryKey" AS territory_key,

    s."OrderDateKey" AS order_date_key,
    s."DueDateKey" AS due_date_key,
    s."ShipDateKey" AS ship_date_key,

    s."Order Quantity" AS order_quantity,
    s."Unit Price" AS unit_price,
    s."Extended Amount" AS extended_amount,
    s."Unit Price Discount Pct" AS declared_discount_pct,

    s."Product Standard Cost" AS unit_standard_cost,
    s."Total Product Cost" AS total_product_cost,
    s."Sales Amount" AS revenue,

    -- Gross profit based on recorded product costs.

    (
        s."Sales Amount"
        - s."Total Product Cost"
    ) AS gross_profit,

    -- Diagnostic difference between formula-based
    -- revenue and recorded revenue.
    -- This is not a confirmed contractual discount.

    (
        s."Extended Amount"
        * (1 - s."Unit Price Discount Pct")
        - s."Sales Amount"
    ) AS formula_difference,

    -- Effective reduction compared to extended amount.

    CASE
        WHEN s."Extended Amount" > 0
        THEN
            (
                s."Extended Amount" - s."Sales Amount"
            ) / s."Extended Amount"
        ELSE NULL
    END AS effective_reduction_rate,

    -- Indicator for negative gross profit.

    (
        s."Sales Amount"
        - s."Total Product Cost"
    ) < 0 AS is_negative_gross_profit

FROM raw.sales AS s

INNER JOIN raw.orders AS o
    ON s."SalesOrderLineKey" =
       o."SalesOrderLineKey";


-- ============================================================
-- VALIDATE MODEL CREATION
-- ============================================================

SELECT
    table_name,
    table_type

FROM information_schema.views
JOIN information_schema.tables
    USING (table_schema, table_name)

WHERE table_schema = 'marts'

ORDER BY table_name;

COMMIT;
