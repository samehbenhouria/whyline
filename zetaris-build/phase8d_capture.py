#!/usr/bin/env python3
"""Phase 8d: open a New Query in the SQL Workspace (disambiguated click),
dump the editor DOM, type the frozen selects, run, screenshot results."""
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
OUT = "/workspaces/whyline/shots"
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

def dump(pg, tag, n=1100):
    try:
        body = pg.inner_text("body")[:n].replace("\n", " | ")
    except Exception as e:
        body = f"<no body {e}>"
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
        pg.click("button:has-text('No thanks')", timeout=3000)
        time.sleep(1)
    except Exception:
        pass
    pg.click("text=Workbench", timeout=6000)
    time.sleep(2)
    pg.click("text=SQL Workspace", timeout=6000)
    time.sleep(4)

    loc = pg.locator("button:has-text('New Query')")
    print("NEWQUERY_COUNT", loc.count())
    loc.last.click()
    time.sleep(6)
    dump(pg, "EDITOR")
    ed = pg.eval_on_selector_all("textarea, [contenteditable], iframe, div", "els => els.filter(e => /monaco|cm-|editor|inputarea/i.test(e.className && e.className.toString ? e.className.toString() : '')).slice(0,12).map(e => e.tagName + '.' + (e.className.toString ? e.className.toString().slice(0,70) : ''))")
    print("EDITOR_ELS", ed)
    btns = pg.eval_on_selector_all("button", "els => els.map(e => ({t:(e.innerText||'').trim(), aria: e.getAttribute('aria-label')})).filter(x => x.t || x.aria)")
    print("EDITOR_BUTTONS", btns)

    def run_query(sql, shot):
        focused = False
        for sel in (".cm-content", ".monaco-editor", "textarea", "[contenteditable='true']", ".inputarea"):
            try:
                pg.click(sel, timeout=3500)
                focused = True
                print("FOCUS_VIA", sel)
                break
            except Exception:
                continue
        print("FOCUSED", focused)
        pg.keyboard.press("Control+a")
        pg.keyboard.type(sql, delay=1)
        time.sleep(1)
        pg.screenshot(path=f"{OUT}/{shot}_typed.png")
        ran = False
        for label in ("Run Query", "Run", "Execute"):
            try:
                cand = pg.locator(f"button:has-text('{label}')")
                if cand.count() > 0:
                    cand.first.click(timeout=3500)
                    ran = True
                    print("RAN_VIA", label)
                    break
            except Exception:
                continue
        if not ran:
            for sel in ("button[aria-label*='Run' i]", "button[aria-label*='Execute' i]", "button[aria-label*='Play' i]"):
                try:
                    cand = pg.locator(sel)
                    if cand.count() > 0:
                        cand.first.click(timeout=3000)
                        ran = True
                        print("RAN_VIA", sel)
                        break
                except Exception:
                    continue
        print("RAN", ran)
        time.sleep(18)
        try:
            pg.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        time.sleep(2)
        dump(pg, shot, 1500)
        pg.screenshot(path=f"{OUT}/{shot}.png")

    run_query(Q1, "S2b_q1_margins")
    # second query in the same editor (replace text)
    run_query(Q2, "S2c_q2_profile")
    b.close()
print("CAPTURE8D_DONE")
