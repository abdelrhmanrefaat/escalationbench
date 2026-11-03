"""Render a ticket file as a Markdown review sheet: python scripts/review_sheet.py data/tickets/pilot.jsonl"""
import sys
from pathlib import Path

from escalationbench.tickets import load_tickets

src = Path(sys.argv[1])
ts = load_tickets(src)
lines = [f"# Review sheet: `{src}`\n",
         "Generated from the JSONL. To correct a ticket, edit `scripts/pilot_tickets.py` (or the JSONL) and re-run this script.\n",
         "For each ticket, check: (1) is the label right under `config/prompts/policy.md`? (2) is the reason right? "
         "(3) is it realistic? (4) is `difficulty` fair? Write your verdict in the **Your call** line.\n"]
for t in ts:
    o = t.order
    order = (f"{o.order_id} · {o.status} · ${o.total_usd:.2f} · " + ", ".join(f"{i.qty}× {i.name}" for i in o.items)
             + (f" · notes: {o.notes}" if o.notes else "")) if o else "none"
    lines.append(f"\n## {t.id} · {t.category} · **{t.label}**{' (' + t.policy_rule + ')' if t.policy_rule else ''} · {t.difficulty}"
                 f"{' · asks for human' if t.asks_for_human else ''}\n")
    lines.append(f"> {t.customer_message}\n")
    lines.append(f"- **Reason:** {t.reason}\n- **Order:** {order}\n- **Your call:** ☐ OK  ☐ change → \n")
out = src.with_name(src.stem.upper() + "_REVIEW.md")
out.write_text("\n".join(lines))
print(f"wrote {out}")
