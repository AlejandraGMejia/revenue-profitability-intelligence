
-- Reseller staging model.
-- Preserves the special reseller_key = -1 member.

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'resellers') }}

),

renamed AS (

    SELECT
        "ResellerKey" AS reseller_key,
        "Reseller ID" AS reseller_id,
        "Business Type" AS business_type,
        "Reseller" AS reseller_name,
        "City" AS city,
        "State-Province" AS state_province,
        "Country-Region" AS country_region,
        "Postal Code" AS postal_code

    FROM source_data

)

SELECT *
FROM renamed
