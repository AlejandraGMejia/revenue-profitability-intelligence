-- ============================================================
-- PROJECT: REVENUE & PROFITABILITY INTELLIGENCE
-- MODULE: RAW DATA LAYER
-- DATABASE: revenue_intelligence
-- ============================================================

-- Create the raw data schema.
-- Source records will be loaded without business transformations.

CREATE SCHEMA IF NOT EXISTS raw
AUTHORIZATION revenue_app;

-- Document the purpose of the schema.

COMMENT ON SCHEMA raw IS
'Original AdventureWorks source data ingested from Excel. Business transformations are performed in downstream schemas.';

-- Verify that the schema exists.

SELECT
    schema_name,
    schema_owner
FROM information_schema.schemata
WHERE schema_name = 'raw';

-- ============================================================
-- END
-- ============================================================
