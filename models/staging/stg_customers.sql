
-- Customer staging model.
-- Preserves the special customer_key = -1 member.

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'customers') }}

),

renamed AS (

    SELECT
        "CustomerKey" AS customer_key,
        "Customer ID" AS customer_id,
        "Customer" AS customer_name,
        "City" AS city,
        "State-Province" AS state_province,
        "Country-Region" AS country_region,
        "Postal Code" AS postal_code

    FROM source_data

)

SELECT *
FROM renamed
