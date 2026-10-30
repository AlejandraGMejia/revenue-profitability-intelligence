
-- Product staging model.
-- Grain: one record per product_key.

WITH source_data AS (

    SELECT *
    FROM {{ source('raw', 'products') }}

),

renamed AS (

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

    FROM source_data

)

SELECT *
FROM renamed
