{{ config(materialized='table') }}

WITH indicadores AS (

    SELECT
        data_referencia,
        codigo_serie,
        nome_serie,
        valor_indicador,
        data_carga
    FROM {{ ref('stg_bcb_series') }}

),

final AS (

    SELECT
        data_referencia,
        YEAR(data_referencia) AS ano,
        MONTH(data_referencia) AS mes,
        FORMAT(data_referencia, 'yyyy-MM') AS ano_mes,
        codigo_serie,
        nome_serie,
        valor_indicador,
        data_carga
    FROM indicadores

)

SELECT *
FROM final
WHERE valor_indicador IS NOT NULL
