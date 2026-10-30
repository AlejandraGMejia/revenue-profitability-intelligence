-- Product dimension.
-- Grain: one record per product.

WITH products AS (

    SELECT *
    FROM {{ ref('stg_products') }}

)

SELECT
    product_key,
    product_sku,
    product_name,
    standard_cost,
    product_color,
    list_price,
    product_model,
    subcategory,
    category

FROM products
