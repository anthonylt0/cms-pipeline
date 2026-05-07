SELECT
    drg_code,
    drg_description,
    fiscal_year,
    AVG(avg_covered_charges) AS nat_avg_covered_charges,
    AVG(avg_medicare_payments) AS nat_avg_medicare_payments,
    AVG(avg_total_payments) AS nat_avg_total_payments   
FROM {{ ref('stg_inpatient') }}
GROUP BY drg_code, drg_description, fiscal_year
