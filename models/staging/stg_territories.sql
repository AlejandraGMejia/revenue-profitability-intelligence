
-- Sales territory staging model.

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'territories') }}

),

renamed AS (

    SELECT
        "SalesTerritoryKey" AS territory_key,
        "Region" AS region,
        "Country" AS country,
        "Group" AS territory_group

    FROM source_data

)

SELECT *
FROM renamed
