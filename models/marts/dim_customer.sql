-- Customer dimension.
-- Includes the special customer_key = -1 member.

WITH customers AS (

    SELECT *
    FROM {{ ref('stg_customers') }}

)

SELECT
    customer_key,
    customer_id,
    customer_name,
    city,
    state_province,
    country_region,
    postal_code

FROM customers
