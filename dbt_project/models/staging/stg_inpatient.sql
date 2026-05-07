SELECT
    provider_ccn,
    provider_name,
    provider_city,
    provider_state,
    provider_zip,
    drg_code,
    drg_description,total_discharges,
    avg_covered_charges,
    avg_total_payments,
    avg_medicare_payments,
    fiscal_year
FROM {{ source('cms', 'inpatient_raw') }}
WHERE provider_ccn IS NOT NULL
    AND drg_code IS NOT NULL
    AND fiscal_year IS NOT NULL