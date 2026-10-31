#!/usr/bin/env python3
"""Phase 10 — S2a only: expand File Source & API, then SEC_DATA, so the
shot shows the investigation's real datasets (jury C3 tour-2 piece).
Zoom 0.8, same as phase 9. Output: /workspaces/whyline/shots9/S2a_sources.png"""
import os
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
OUT = "/workspaces/whyline/shots9"
os.makedirs(OUT, exist_ok=True)
lines = [l.strip() for l in open("/workspaces/zetaris-secrets/platform_admin.txt") if l.strip()]
username, password = lines[0], lines[1]

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
    pg.evaluate("document.body.style.zoom = '0.8'")
    time.sleep(1)
    # expand the File Source & API node in the Data Explorer
    for sel in ("text=File Source & API",):
        try:
            pg.click(sel, timeout=8000)
            print("EXPANDED_FSA")
            time.sleep(3)
        except Exception as e:
            print("FSA_FAIL", type(e).__name__)
    try:
        body = pg.inner_text("body")[:1100].replace("\n", " | ")
        print("AFTER_FSA", body)
    except Exception:
        pass
    # expand SEC_DATA itself (its tables/schemas are the investigation data)
    try:
        pg.click("text=SEC_DATA", timeout=8000)
        print("CLICKED_SEC_DATA")
        time.sleep(4)
    except Exception as e:
        print("SECDATA_FAIL", type(e).__name__)
    try:
        body = pg.inner_text("body")[:1600].replace("\n", " | ")
        print("AFTER_SECDATA", body)
    except Exception:
        pass
    pg.mouse.move(960, 1040)
    time.sleep(1)
    pg.screenshot(path=f"{OUT}/S2a_sources.png")
    b.close()
print("CAPTURE10_DONE")
