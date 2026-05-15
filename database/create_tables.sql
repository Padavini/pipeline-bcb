CREATE TABLE bronze_bcb_series (
    data DATE NOT NULL,
    valor DECIMAL(18,4),
    nome_serie VARCHAR(100) NOT NULL,
    codigo_serie INT NOT NULL,
    data_carga DATETIME NOT NULL,

    CONSTRAINT pk_bronze_bcb_series
    PRIMARY KEY (codigo_serie, data)
);