{{ config(materialized='view') }}

WITH source AS (

    SELECT
        data,
        valor,
        nome_serie,
        codigo_serie,
        data_carga
    FROM {{ source('bronze', 'bronze_bcb_series') }}

),

renamed AS (

    SELECT
        CAST(data AS DATE) AS data_referencia,
        CAST(valor AS DECIMAL(18,4)) AS valor_indicador,
        UPPER(TRIM(nome_serie)) AS nome_serie,
        CAST(codigo_serie AS INT) AS codigo_serie,
        CAST(data_carga AS DATETIME) AS data_carga
    FROM source

)

SELECT *
FROM renamed
WHERE data_referencia IS NOT NULL
  AND codigo_serie IS NOT NULL