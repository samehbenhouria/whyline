#!/usr/bin/env python3
"""Phase 8b capture: real Zetaris UI screenshots for the demo video.
S2a data sources, S2b SQL workspace Q1 (margins), S2c SQL workspace Q2
(profile), S2e WhyLine proof report, S2d the run terminal (verbatim log
lines rendered in a terminal-styled page). All captures 1920x1080."""
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
OUT = "/workspaces/whyline/shots"
import os
os.makedirs(OUT, exist_ok=True)
lines = [l.strip() for l in open("/workspaces/zetaris-secrets/platform_admin.txt") if l.strip()]
username, password = lines[0], lines[1]

Q1 = ("SELECT DISTINCT r.period_start, r.period_end, r.value_usd AS revenue, "
      "n.value_usd AS net_income FROM edgar.apple_revenue_table r "
      "JOIN edgar.apple_netincome_table n ON n.period_start = r.period_start "
      "AND n.period_end = r.period_end ORDER BY r.period_end")
Q2 = ("SELECT cik, entity_name, sic_code, sic_description_edgar, "
      "sic_description_reference, division, division_desc, major_group, "
      "major_group_desc, industry_group, industry_group_desc "
      "FROM edgar.apple_profile_table")

def dump(pg, tag):
    body = pg.inner_text("body")[:900].replace("\n", " | ")
    print(tag, pg.url)
    print(tag + "_BODY", body)

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto(BASE, wait_until="networkidle", timeout=60000)
    time.sleep(2)
    pg.fill("input#username", username)
    pg.fill("input#password", password)
    pg.click("button[type='submit'], button:has-text('Sign in'), button:has-text('Log in')")
    time.sleep(6)
    try:
        pg.click("button:has-text('No thanks')", timeout=4000)
        time.sleep(1)
    except Exception:
        print("NO_TELEMETRY_DIALOG")
    dump(pg, "HOME")

    # ---- S2a: data sources ----
    try:
        pg.click("text=Data Explorer", timeout=8000)
        time.sleep(5)
    except Exception as e:
        print("EXPLORER_CLICK_FAIL", type(e).__name__)
    dump(pg, "EXPLORER")
    pg.screenshot(path=f"{OUT}/S2a_sources.png")

    # ---- SQL workspace ----
    try:
        pg.click("text=Workbench", timeout=8000)
        time.sleep(4)
    except Exception as e:
        print("WORKBENCH_CLICK_FAIL", type(e).__name__)
    dump(pg, "WORKBENCH")
    # find the SQL workspace entry
    for label in ("SQL Workspace", "SQL Editor", "SQL"):
        try:
            pg.click(f"text={label}", timeout=5000)
            time.sleep(5)
            break
        except Exception:
            continue
    dump(pg, "SQLWS")

    def run_query(sql, shot):
        # focus the editor (Monaco/CodeMirror/textarea)
        focused = False
        for sel in (".monaco-editor", ".cm-editor", "textarea"):
            try:
                pg.click(sel, timeout=4000)
                focused = True
                break
            except Exception:
                continue
        print("EDITOR_FOCUSED", focused)
        pg.keyboard.press("Control+a")
        pg.keyboard.type(sql, delay=2)
        time.sleep(1)
        ran = False
        for label in ("Run", "Execute", "Run Query"):
            try:
                pg.click(f"button:has-text('{label}')", timeout=4000)
                ran = True
                break
            except Exception:
                continue
        print("RUN_CLICKED", ran)
        time.sleep(14)
        try:
            pg.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        time.sleep(2)
        dump(pg, shot)
        pg.screenshot(path=f"{OUT}/{shot}.png")

    run_query(Q1, "S2b_q1_margins")
    run_query(Q2, "S2c_q2_profile")

    # ---- S2e: the proof report (served from the codespace) ----
    pg.goto("http://127.0.0.1:8022/out/report.html", wait_until="networkidle", timeout=60000)
    time.sleep(3)
    pg.screenshot(path=f"{OUT}/S2e_report.png")
    print("REPORT_TITLE", pg.title())

    # ---- S2d: terminal page with verbatim run-log lines ----
    log = open("/workspaces/phase6.log", encoding="utf-8", errors="replace").read()
    start = log.find("=== RUN INVESTIGATION LIVE ===")
    excerpt = log[start:start + 2600] if start >= 0 else log[-2600:]
    import html as htmlmod
    term = ("<html><head><meta charset='utf-8'><style>"
            "body{background:#0c0c0c;margin:0;font-family:'DejaVu Sans Mono',monospace}"
            ".win{margin:36px;border-radius:10px;background:#111;box-shadow:0 8px 40px #000}"
            ".bar{background:#222;padding:10px 16px;color:#bbb;font-size:15px;border-radius:10px 10px 0 0}"
            "pre{color:#d6ffd6;font-size:16.5px;line-height:1.5;padding:22px 26px;white-space:pre-wrap}"
            ".cmd{color:#7ee787}</style></head><body><div class='win'>"
            "<div class='bar'>codespace — whyline-build — bash</div>"
            "<pre><span class='cmd'>$ cd /workspaces/whyline &amp;&amp; python3 run_investigation.py --live --config investigation.json</span>\n"
            + htmlmod.escape(excerpt) +
            "</pre><div style='color:#9ecbff;font-size:17px;padding:0 26px 22px'>"
            "WhyLine proof chain — 13 findings · 138 evidence records · chain verified = True</div>"
            "</div></body></html>")
    with open("/workspaces/whyline/shots/terminal.html", "w") as f:
        f.write(term)
    pg.goto("http://127.0.0.1:8022/shots/terminal.html", wait_until="networkidle", timeout=30000)
    time.sleep(2)
    pg.screenshot(path=f"{OUT}/S2d_terminal.png")
    b.close()
print("CAPTURE_DONE")
