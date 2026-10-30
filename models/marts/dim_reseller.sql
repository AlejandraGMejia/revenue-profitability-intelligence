-- Reseller dimension.
-- Includes the special reseller_key = -1 member.

WITH resellers AS (

    SELECT *
    FROM {{ ref('stg_resellers') }}

)

SELECT
    reseller_key,
    reseller_id,
    business_type,
    reseller_name,
    city,
    state_province,
    country_region,
    postal_code

FROM resellers
