-- WhyLine derived table: Apple net income, mirroring the Apple block of
-- the official script 01 (which creates Revenue only). CIK 0000320193,
-- concept NetIncomeLoss. Created 2026-10-27 on the original instance;
-- recreated 2026-10-30 on the whyline-build instance.
CREATE LIGHTNING REST TABLE apple_netincome_facts FROM SEC_DATA REQUEST(
    endpoint "https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/NetIncomeLoss.json",
    method "get",
    response_type "json",
    http_encoding "URLENCODED"
) HEADER (
    user-agent "YOUR_APP_NAME YOUR_CONTACT_EMAIL"
) BODY ();

CREATE SCHEMASTORE VIEW apple_netincome_table WITH CONTAINER edgar AS
SELECT
    cik,
    `entityName` AS entity_name,
    tag AS concept,
    fact.`start` AS period_start,
    fact.`end` AS period_end,
    fact.val AS value_usd,
    fact.accn AS accession_number,
    fact.fy AS fiscal_year,
    fact.fp AS fiscal_period,
    fact.frame AS period_frame,
    fact.form AS form_type,
    fact.filed AS filed_date
FROM sec_data.apple_netincome_facts
LATERAL VIEW explode(units.USD) AS fact;
