SELECT h.*, n.nat_avg_covered_charges, n.nat_avg_medicare_payments, n.nat_avg_total_payments
FROM {{ ref('mart_hospital_drg') }} AS h
JOIN {{ ref('mart_national_benchmarks') }} AS n ON h.drg_code = n.drg_code
AND h.fiscal_year = n.fiscal_year
WHERE provider_ccn IN ('220071', '220110', '220101')