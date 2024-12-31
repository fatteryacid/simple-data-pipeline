SELECT  
    *,
    TIMESTAMP("{{ ts }}")    AS execution_ts,
FROM `sandbox-data-pipelines.raw_layer.mockaroo_customer_data_v1`
;

