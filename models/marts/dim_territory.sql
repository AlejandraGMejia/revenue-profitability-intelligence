-- Sales territory dimension.

WITH territories AS (

    SELECT *
    FROM {{ ref('stg_territories') }}

)

SELECT
    territory_key,
    region,
    country,
    territory_group

FROM territories
