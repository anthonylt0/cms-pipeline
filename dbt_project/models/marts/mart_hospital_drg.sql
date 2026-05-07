SELECT
    provider_ccn,
    provider_name,
    provider_city,
    provider_state,
    provider_zip,
    drg_code,
    drg_description,
    total_discharges,
    avg_covered_charges,
    avg_total_payments,
    avg_medicare_payments,
    fiscal_year,
    avg_covered_charges / avg_medicare_payments AS charge_to_payment_ratio
FROM {{ ref('stg_inpatient') }}