#!/usr/bin/env python3
"""Phase 8a discovery: log into the Zetaris UI locally, screenshot the
landing view, and dump navigable texts so the capture pass can target
the real screens. Credentials are read inside the codespace from the
secrets file and never printed."""
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
lines = [l.strip() for l in open("/workspaces/zetaris-secrets/platform_admin.txt") if l.strip()]
username, password = lines[0], lines[1]

with sync_playwright() as p:
    b = p.chromium.launch(args=["--no-sandbox"])
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto(BASE, wait_until="networkidle", timeout=60000)
    time.sleep(3)
    print("URL0", pg.url)
    inputs = pg.eval_on_selector_all("input", "els => els.map(e => ({type: e.type, name: e.name, ph: e.placeholder, id: e.id}))")
    print("INPUTS", inputs)
    # generic fill: first text/email input = user, password input = pass
    pg.fill("input[type='password']", password)
    user_sel = "input[type='email'], input[type='text'], input[name='username'], input#username"
    pg.fill(user_sel, username)
    pg.click("button[type='submit'], button:has-text('Sign in'), button:has-text('Log in'), button:has-text('Login')")
    time.sleep(6)
    try:
        pg.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    time.sleep(3)
    print("URL1", pg.url)
    pg.screenshot(path="/workspaces/whyline/shots_probe.png")
    texts = pg.eval_on_selector_all("a, button, [role='menuitem'], [role='tab']", "els => els.slice(0,80).map(e => (e.innerText||'').trim()).filter(t => t)")
    print("NAV_TEXTS", texts)
    body = pg.inner_text("body")[:1200].replace("\n", " | ")
    print("BODY_HEAD", body)
    b.close()
print("DISCOVERY_DONE")
