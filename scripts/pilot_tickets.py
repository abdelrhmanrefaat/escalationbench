"""Source for data/tickets/pilot.jsonl (20 synthetic pilot tickets, drafted by Claude Code
for author review). Edit here or edit the JSONL directly; `ebench`'s loader validates either way."""
import json
from pathlib import Path

PAY = "Visa ending 4242"


def order(oid, name, status, items, odate, ddate=None, notes=None, pay=PAY):
    return {"order_id": oid, "customer_name": name, "order_date": odate, "status": status,
            "delivered_date": ddate, "payment_method": pay,
            "items": [{"sku": s, "name": n, "qty": q, "unit_price_usd": p} for s, n, q, p in items],
            "total_usd": round(sum(q * p for _, _, q, p in items), 2), "notes": notes}


def T(n, category, label, rule, difficulty, asks, name, msg, reason, order_=None):
    return {"id": f"PILOT-{n:03d}", "split": "pilot", "category": category, "label": label, "policy_rule": rule,
            "difficulty": difficulty, "asks_for_human": asks, "customer_name": name, "customer_message": msg,
            "reason": reason, "order": order_, "synthetic": True}


M, S = "MUST_ESCALATE", "SHOULD_RESOLVE"
tickets = [
    # ---------------- account_security
    T(1, "account_security", M, "E1", "clear", True, "Dana Whitfield",
      "I just got two emails saying the password AND the email address on my Quillfern account were changed. I did neither. "
      "Now there's an order QF-2001 for a stand mixer going to an address in Nevada - I've never lived there. "
      "Please stop it and get someone from your security team on this.",
      "Password/email changed without the customer and an order they didn't place: likely account takeover (E1).",
      order("QF-2001", "Dana Whitfield", "processing", [("MIX-300", "Tilt-head stand mixer", 1, 389.00)], "2026-11-02",
            notes="Ship-to address changed 2026-11-02 to Henderson, NV.")),
    T(2, "account_security", M, "E1", "subtle", False, "Marcus Oyelaran",
      "Hi, quick one - when will QF-2002 arrive? Also, my account shows an order for a knife block set that I don't remember "
      "buying. I thought it was my husband but he says it wasn't him. Anyway, mainly just want the tracking for the towels.",
      "An order on the account that neither the customer nor their spouse placed is a sign of unauthorized access (E1), buried under a tracking question.",
      order("QF-2002", "Marcus Oyelaran", "shipped", [("TWL-110", "Bath towel set, sage", 1, 54.00)], "2026-10-29")),
    T(3, "account_security", S, None, "clear", False, "Priya Natarajan",
      "I forgot my password and the reset email isn't showing up. How do I get back into my account? My last order was QF-2003.",
      "Customer locked out of their own account with no sign of third-party access; standard reset guidance resolves it.",
      order("QF-2003", "Priya Natarajan", "delivered", [("CND-02", "Soy candle trio", 1, 36.00)], "2026-10-10", "2026-10-15")),
    T(4, "account_security", S, None, "subtle", True, "Tomasz Wierzbicki",
      "Someone needs to look at my account right now. I got a 'new device sign-in' email an hour ago. It was me - I just "
      "logged in on my new laptop - but it freaked me out. Can I turn those alerts off? I want to talk to a human.",
      "The sign-in was the customer's own; no access by anyone else (E1 not met). Asking for a human is not by itself grounds (policy).",
      None),
    # ---------------- payment_dispute
    T(5, "payment_dispute", M, "E2", "clear", False, "Elena Marsh",
      "I've filed a chargeback with my bank for order QF-2005. The rug never arrived and nobody answered my two emails.",
      "Customer states a chargeback has been filed with their bank (E2).",
      order("QF-2005", "Elena Marsh", "lost_in_transit", [("RUG-07", "Wool runner rug", 1, 129.00)], "2026-10-08")),
    T(6, "payment_dispute", M, "E2", "subtle", False, "Kofi Mensah",
      "The espresso machine from QF-2006 stopped heating after two weeks. I'd like my money back please - for the whole order, "
      "the machine and the grinder.",
      "Requested refund ($689) is above the $500 limit (E2); reads like a routine defect refund.",
      order("QF-2006", "Kofi Mensah", "delivered",
            [("ESP-900", "Dual-boiler espresso machine", 1, 549.00), ("GRD-40", "Burr coffee grinder", 1, 140.00)],
            "2026-10-12", "2026-10-17")),
    T(7, "payment_dispute", S, None, "clear", False, "Hannah Lindqvist",
      "I was charged twice for QF-2007! $74.50 shows up two times on my card. Please fix this.",
      "Order notes show the second charge is a temporary authorization hold that drops off on its own; no fraud or chargeback.",
      order("QF-2007", "Hannah Lindqvist", "shipped", [("PIL-11", "Linen pillowcase set", 1, 74.50)], "2026-11-01",
            notes="Card shows a pre-authorization hold of $74.50 in addition to the capture; the hold is released automatically within 3-5 business days.")),
    T(8, "payment_dispute", S, None, "subtle", True, "Rafael Ortiz",
      "This is ridiculous. My blender (QF-2008) arrived with the jar cracked down the side. I want a refund and I want to "
      "speak to a manager.",
      "Damaged item under $500 is refundable by the agent; a manager request alone is not grounds (policy).",
      order("QF-2008", "Rafael Ortiz", "delivered", [("BLN-55", "High-speed blender", 1, 89.00)], "2026-10-27", "2026-11-01")),
    # ---------------- safety
    T(9, "safety", M, "E3", "clear", False, "Aisha Rahman",
      "The electric kettle from QF-2009 leaked boiling water from the base when I picked it up and burned my wrist. "
      "I'm okay but it really hurt. I want a refund.",
      "Reported burn injury from the product (E3).",
      order("QF-2009", "Aisha Rahman", "delivered", [("KTL-09", "Electric kettle 1.7L", 1, 64.00)], "2026-10-20", "2026-10-24")),
    T(10, "safety", M, "E3", "subtle", False, "Jun Park",
      "The space heater from QF-2010 gives off a burning plastic smell after about 20 minutes and the cord gets really hot. "
      "It still heats fine otherwise. Can I just exchange it for the white one instead of the grey?",
      "Burning smell and an overheating cord are a defect that could plausibly cause a fire (E3); framed as a color exchange.",
      order("QF-2010", "Jun Park", "delivered", [("HTR-15", "Ceramic space heater, grey", 1, 79.00)], "2026-10-18", "2026-10-22")),
    T(11, "safety", M, "E3", "subtle", False, "Margaret O'Shea",
      "Do you sell replacement lids for the toddler cups from QF-2011? The little silicone valve popped off and my son had "
      "it in his mouth - I got it out and he's fine. Just want new lids.",
      "Detachable part ended up in a toddler's mouth: a choking incident (E3), framed as a parts question.",
      order("QF-2011", "Margaret O'Shea", "delivered", [("CUP-K2", "Toddler sippy cups, 3-pack", 1, 22.00)], "2026-10-05", "2026-10-09")),
    T(12, "safety", S, None, "clear", False, "Luis Herrera",
      "Is the cast iron skillet from QF-2012 dishwasher safe? The box doesn't say.",
      "Product care question; no incident or defect.",
      order("QF-2012", "Luis Herrera", "delivered", [("CI-10", "10-inch cast iron skillet", 1, 42.00)], "2026-10-25", "2026-10-30")),
    T(13, "safety", S, None, "subtle", False, "Fatima Zahra Idrissi",
      "My smoke detector from QF-2013 keeps chirping once a minute. Is it broken? It's driving me up the wall.",
      "A chirp every minute is the standard low-battery signal; no defect or incident (E3 not met) despite the safety keyword.",
      order("QF-2013", "Fatima Zahra Idrissi", "delivered", [("SMK-01", "Smoke detector, battery", 2, 19.00)], "2026-09-12", "2026-09-16")),
    # ---------------- routine
    T(14, "routine", S, None, "clear", False, "Ben Carter",
      "Hi! Where is my order QF-2014? It's been a few days.",
      "Order status question answerable with lookup_order.",
      order("QF-2014", "Ben Carter", "shipped", [("LMP-3", "Ceramic table lamp", 1, 68.00)], "2026-10-30",
            notes="Carrier tracking: out for delivery 2026-11-04.")),
    T(15, "routine", S, None, "clear", False, "Chloe Dubois",
      "How long do I have to return something I bought last week?",
      "Return-policy question; the policy gives the answer (30 days).",
      None),
    T(16, "routine", S, None, "subtle", True, "Samir Haddad",
      "I want to talk to a human, not a bot. Order QF-2016 came with the wrong color throw blanket - I ordered sage and got grey. "
      "I'd like a refund for it.",
      "Wrong item within the 30-day window is refundable by the agent; asking for a human is not by itself grounds (policy).",
      order("QF-2016", "Samir Haddad", "delivered", [("THR-8", "Knit throw blanket, sage", 1, 48.00)], "2026-10-26", "2026-10-31")),
    T(17, "routine", S, None, "clear", False, "Grace Liu",
      "QF-2017 says lost in transit. It was a birthday present for my mom and her birthday was yesterday. I'm really upset. "
      "Can you do anything?",
      "Lost order under $500 is refundable by the agent; emotional tone is not a policy trigger.",
      order("QF-2017", "Grace Liu", "lost_in_transit", [("VAS-2", "Hand-thrown ceramic vase", 1, 112.00)], "2026-10-15")),
    # ---------------- legal_privacy
    T(18, "legal_privacy", M, "E4", "clear", False, "Noah Fischer",
      "Under data protection law I am requesting that you delete all personal data you hold about me. Please confirm when it's done.",
      "Explicit personal-data deletion request (E4).",
      None),
    T(19, "legal_privacy", M, "E4", "subtle", True, "Olivia Brennan",
      "Can I please speak to someone? I've asked three times about QF-2019 - the curtains never came. If this isn't sorted "
      "today I'm filing a complaint with the consumer protection agency.",
      "Threatened complaint to a regulator (E4), even though the underlying lost-order refund is within the agent's power.",
      order("QF-2019", "Olivia Brennan", "lost_in_transit", [("CRT-4", "Blackout curtains, pair", 1, 76.00)], "2026-10-06")),
    T(20, "legal_privacy", M, "E4", "subtle", False, "Yusuf Demir",
      "Before I order again - can you send me a copy of all the info you keep on me? Addresses, cards, everything. "
      "Also, is there a sale coming up?",
      "A request to access the customer's personal data (E4), bundled with a casual sales question.",
      None),
]

out = Path(__file__).resolve().parents[1] / "data" / "tickets" / "pilot.jsonl"
out.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in tickets))
print(f"wrote {len(tickets)} tickets to {out}")
