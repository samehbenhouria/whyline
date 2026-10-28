-- WhyLine investigation selects — FROZEN 2026-10-27 on the live team
-- instance (Codespace, Zetaris platform verified 9/9). View names are
-- the actual names created by the official scripts 01 / 11 / 12 plus
-- the derived apple_netincome_table (script 01 creates Revenue only;
-- the NetIncomeLoss table mirrors its Apple block, CIK 0000320193).
-- Each result row -> one H-MEM evidence record (source + this SQL + row).

-- Q1. The facts under investigation: Apple revenue + net income for
-- the SAME period (the join key is the period itself). NOTE on this
-- extract: every row is labeled fiscal_year 2018 (its XBRL frame
-- year) and the fiscal_period / form_type labels do not separate
-- annual from quarterly rows — so the query deliberately keys on
-- period_start / period_end, and the agent classifies a pair as
-- annual by its span (>= 300 days), never by the labels. DISTINCT
-- removes the duplicates the join produces (original + restated
-- filings of one period).
SELECT DISTINCT r.period_start,
       r.period_end,
       r.value_usd AS revenue,
       n.value_usd AS net_income
FROM edgar.apple_revenue_table r
JOIN edgar.apple_netincome_table n
  ON n.period_start = r.period_start AND n.period_end = r.period_end
ORDER BY r.period_end;

-- Q2. The industry frame: Apple's SIC profile (EDGAR profiles joined
-- with the company_dns SIC hierarchy V4).
SELECT cik, entity_name, sic_code, sic_description_edgar,
       sic_description_reference, division, division_desc,
       major_group, major_group_desc, industry_group, industry_group_desc
FROM edgar.apple_profile_table;

-- Q3. The contrast: the same revenue fact for every company the facts
-- source carries — peers are only comparable inside their SIC frame.
SELECT p.entity_name, p.sic_code, p.sic_description_reference,
       f.period_end, f.value_usd AS revenue, f.fiscal_year, f.fiscal_period
FROM edgar.apple_revenue_table f
JOIN edgar.apple_profile_table p ON f.cik = p.cik
WHERE f.fiscal_period = 'FY'
UNION ALL
SELECT p.entity_name, p.sic_code, p.sic_description_reference,
       f.period_end, f.value_usd, f.fiscal_year, f.fiscal_period
FROM edgar.walmart_revenue_table f
JOIN edgar.walmart_profile_table p ON f.cik = p.cik
WHERE f.fiscal_period = 'FY'
ORDER BY fiscal_year, entity_name;
