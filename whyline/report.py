"""Render an H-MEM proof chain as one self-contained HTML page.

The page IS the product surface of WhyLine: question, conclusion,
findings, and for every finding the evidence rows with source, SQL,
retrieval time and SHA-256 hash - the full replayable "why".
No external assets, so the file can be opened anywhere.
"""

from __future__ import annotations

import html
import json
import time


def _fmt_ts(ts: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(ts))


def render_html(chain: dict, question: str = "", company: str = "") -> str:
    concl = chain["conclusion"]
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head><meta charset="utf-8">',
        f"<title>WhyLine - {html.escape(company or 'investigation')}</title>",
        "<style>body{font-family:system-ui,sans-serif;max-width:900px;margin:2rem auto;"
        "padding:0 1rem;line-height:1.5}code{background:#f2f2f2;padding:.1rem .3rem;"
        "border-radius:4px}pre{background:#f7f7f7;padding:1rem;overflow-x:auto;"
        "border-radius:6px}.ev{border:1px solid #ddd;border-radius:8px;padding:1rem;"
        "margin:.8rem 0}.find{border-left:4px solid #3a7;padding-left:1rem;margin:1.2rem 0}"
        ".hash{color:#666;font-size:.8rem;word-break:break-all}</style></head><body>",
        "<h1>WhyLine - the agent that can explain why</h1>",
    ]
    if question:
        parts.append(f"<p><strong>Question:</strong> {html.escape(question)}</p>")
    parts.append(f"<h2>Conclusion</h2><p>{html.escape(concl['statement'])}</p>")
    parts.append(f"<p>Chain verified: <strong>{chain.get('verified')}</strong> "
                 f"(conclusion id <code>{html.escape(concl['id'])}</code>)</p>")
    for f in chain["findings"]:
        parts.append('<div class="find">')
        parts.append(f"<h3>Finding <code>{html.escape(f['id'])}</code></h3>")
        parts.append(f"<p>{html.escape(f['statement'])}</p>")
        for ev in f["evidence"]:
            parts.append('<div class="ev">')
            parts.append(f"<p><strong>Evidence</strong> <code>{html.escape(ev['id'])}</code> "
                         f"- source: <code>{html.escape(ev['source'])}</code><br>"
                         f"retrieved: {_fmt_ts(ev['retrieved_at'])}</p>")
            parts.append(f"<p>SQL:</p><pre>{html.escape(ev['query'])}</pre>")
            parts.append("<p>Row:</p><pre>"
                         + html.escape(json.dumps(ev["payload"], ensure_ascii=False, indent=2, default=str))
                         + "</pre>")
            parts.append(f"<p class='hash'>SHA-256: {html.escape(ev['payload_hash'])}</p>")
            parts.append("</div>")
        parts.append("</div>")
    parts.append("</body></html>")
    return "\n".join(parts)
