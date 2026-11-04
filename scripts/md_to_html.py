"""Tiny Markdown -> HTML renderer for the reading pack and labelling sheet (no extra dependencies).
Usage: python scripts/md_to_html.py IN.md OUT.html"""
import html
import re
import sys


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)\*", r"<i>\1</i>", s)
    return s


def render(lines):
    out, quote, table = [], [], []

    def flush():
        if quote:
            out.append("<blockquote>" + "<br>".join(inline(q) for q in quote) + "</blockquote>"); quote.clear()
        if table:
            rows = [r for r in table if not re.match(r"^\|[-| ]+\|$", r)]
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows]
            h = "".join(f"<th>{inline(c)}</th>" for c in cells[0])
            b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in cells[1:])
            out.append(f"<table><tr>{h}</tr>{b}</table>"); table.clear()

    for line in lines:
        if line.startswith(">"):
            quote.append(line[1:].lstrip()); continue
        if line.startswith("|"):
            table.append(line); continue
        flush()
        if line.startswith("<details") or line.startswith("</details"):
            out.append(line)
        elif line.startswith("### "):
            out.append(f"<h3>{inline(line[4:])}</h3>")
        elif line.startswith("## "):
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif line.startswith("# "):
            out.append(f"<h1>{inline(line[2:])}</h1>")
        elif line == "---":
            out.append("<hr>")
        elif line.startswith("- "):
            out.append(f"<li>{inline(line[2:])}</li>")
        elif line.startswith("*Your notes") or line.startswith("*Label for"):
            out.append(f'<div class="notes">✏️ {inline(line.strip("*"))}</div>')
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
    flush()
    return out


CSS = """body{font:16px/1.55 -apple-system,system-ui,sans-serif;max-width:760px;margin:0 auto;padding:24px 16px;background:#fbfaf7;color:#1f1f1f}
h2,h3{margin-top:8px;border-left:4px solid #d97757;padding-left:10px}
blockquote{background:#fff;border:1px solid #e3e0d8;border-radius:8px;margin:8px 0;padding:12px 14px}
li{margin:4px 0 4px 18px}code{background:#efece4;padding:1px 4px;border-radius:4px}
table{border-collapse:collapse;margin:8px 0;font-size:14px}td,th{border:1px solid #e3e0d8;padding:6px 8px;text-align:left;vertical-align:top}
details{background:#f3f1ec;border-radius:8px;padding:8px 12px;margin:10px 0 24px;font-size:14px}summary{cursor:pointer;font-weight:600}
.notes{background:#fff6d6;border-radius:8px;padding:10px 12px;margin:12px 0}
hr{border:0;border-top:2px dashed #d8d4ca;margin:28px 0}"""

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    title = open(src).readline().lstrip("# ").strip()
    body = "\n".join(render(open(src).read().split("\n")))
    open(dst, "w").write(f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><title>{html.escape(title)}</title><style>{CSS}</style>{body}")
