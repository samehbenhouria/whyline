# Zetaris setup & investigation queries

## Setup (sources)

WhyLine creates NO data sources of its own. Run the official create
scripts from the Zetaris getting-started repository
(github.com/zetaris/getting-started) in the hackathon team instance
(Zetaris Cloud console, SQL editor), in this order:

1. `open_data/rest_apis/sql/rate_limited/01_edgar_company_facts_create.sql`
   — SEC EDGAR XBRL company facts for 7 companies (Apple, IBM, Oracle,
   Walmart, Target, Ford, Tesla). Rate limited: pace statements, cache early.
2. `open_data/rest_apis/sql/rate_limited/12_company_dns_create.sql`
   — company_dns SIC hierarchy (V4 production). Needs a User-Agent of the
   form `app_name user@domain.tld` on the source.
3. `open_data/rest_apis/sql/rate_limited/11_edgar_company_profiles_create.sql`
   — EDGAR company profiles enriched with the SIC hierarchy.
   Depends on 1 and 2.
4. Optional context: `13_company_dns_eu_nace_create.sql`,
   `14_company_dns_japan_create.sql` (EU NACE / Japan classifications).

Known-to-fail sources in that repository are NOT used.

## Our investigation queries

Our own SELECT statements live in `investigation_selects.sql`. Every row
they return becomes one H-MEM evidence record, stored with the source
name and the exact SQL text, so the final answer can cite its proof.
