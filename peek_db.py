import duckdb

con = duckdb.connect("data/cms_inpatient.duckdb")

# See the table exists
print(con.execute("SHOW TABLES").fetchall())

# See row count
print(con.execute("SELECT COUNT(*) FROM inpatient_raw").fetchone())

# See first 5 rows
print(con.execute("SELECT * FROM inpatient_raw LIMIT 5").fetchdf())

# See row count by year
print(con.execute("SELECT fiscal_year, COUNT(*) FROM inpatient_raw GROUP BY fiscal_year ORDER BY fiscal_year").fetchdf())

con.close()