-- Revenue & Profitability Intelligence
-- Raw source tables

BEGIN;

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.products (
    "ProductKey" BIGINT PRIMARY KEY,
    "SKU" TEXT,
    "Product" TEXT,
    "Standard Cost" NUMERIC(20,6),
    "Color" TEXT,
    "List Price" NUMERIC(20,6),
    "Model" TEXT,
    "Subcategory" TEXT,
    "Category" TEXT
);

CREATE TABLE IF NOT EXISTS raw.customers (
    "CustomerKey" BIGINT PRIMARY KEY,
    "Customer ID" TEXT,
    "Customer" TEXT,
    "City" TEXT,
    "State-Province" TEXT,
    "Country-Region" TEXT,
    "Postal Code" TEXT
);

CREATE TABLE IF NOT EXISTS raw.resellers (
    "ResellerKey" BIGINT PRIMARY KEY,
    "Reseller ID" TEXT,
    "Business Type" TEXT,
    "Reseller" TEXT,
    "City" TEXT,
    "State-Province" TEXT,
    "Country-Region" TEXT,
    "Postal Code" TEXT
);

CREATE TABLE IF NOT EXISTS raw.dates (
    "DateKey" BIGINT PRIMARY KEY,
    "Date" DATE,
    "Fiscal Year" TEXT,
    "Fiscal Quarter" TEXT,
    "Month" TEXT,
    "Full Date" TEXT,
    "MonthKey" BIGINT
);

CREATE TABLE IF NOT EXISTS raw.territories (
    "SalesTerritoryKey" BIGINT PRIMARY KEY,
    "Region" TEXT,
    "Country" TEXT,
    "Group" TEXT
);

CREATE TABLE IF NOT EXISTS raw.orders (
    "Channel" TEXT,
    "SalesOrderLineKey" BIGINT PRIMARY KEY,
    "Sales Order" TEXT,
    "Sales Order Line" TEXT
);

CREATE TABLE IF NOT EXISTS raw.sales (
    "SalesOrderLineKey" BIGINT PRIMARY KEY,
    "ResellerKey" BIGINT,
    "CustomerKey" BIGINT,
    "ProductKey" BIGINT,
    "OrderDateKey" BIGINT,
    "DueDateKey" BIGINT,
    "ShipDateKey" BIGINT,
    "SalesTerritoryKey" BIGINT,
    "Order Quantity" BIGINT,
    "Unit Price" NUMERIC(20,6),
    "Extended Amount" NUMERIC(20,6),
    "Unit Price Discount Pct" NUMERIC(10,6),
    "Product Standard Cost" NUMERIC(20,6),
    "Total Product Cost" NUMERIC(20,6),
    "Sales Amount" NUMERIC(20,6)
);

COMMENT ON TABLE raw.sales IS
'Original AdventureWorks sales line data.';

COMMENT ON TABLE raw.products IS
'Original AdventureWorks product data.';

COMMENT ON TABLE raw.customers IS
'Original AdventureWorks customer data.';

COMMENT ON TABLE raw.resellers IS
'Original AdventureWorks reseller data.';

COMMENT ON TABLE raw.dates IS
'Original AdventureWorks calendar data.';

COMMENT ON TABLE raw.territories IS
'Original AdventureWorks sales territory data.';

COMMENT ON TABLE raw.orders IS
'Original AdventureWorks sales order data.';

COMMIT;
