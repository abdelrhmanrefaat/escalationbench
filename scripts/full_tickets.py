"""Source for data/tickets/dev.jsonl and data/tickets/holdout.jsonl: 180 synthetic tickets for the
fictional Quillfern Home Goods, drafted by Claude Code for author spot-check (PREREGISTRATION 3.2).

Design (DECISIONS D-033):
- 90 MUST_ESCALATE: 30 account_security (E1), 30 payment_dispute (E2), 30 safety (E3).
- 90 SHOULD_RESOLVE: 20 account_security, 20 payment_dispute, 20 safety, 30 routine.
  SHOULD tickets in the risky categories are near-misses (own login, authorization hold,
  refund <= $500, cosmetic defect, maintenance signal working as designed).
- Within every label x category: half clear / half subtle; about one third ask for a human
  (asking for a human is not by itself grounds to escalate under the policy).
- E4 (legal/privacy) is deliberately not used; the prereg lists four categories only.
- Ticket ids are assigned after a seeded shuffle so an id does not reveal the label or category.
- Split: exactly 10 MUST + 10 SHOULD to dev, stratified by label x category, seed from
  config/experiment.yaml; the remaining 160 (80 / 80) are the holdout.

Run: .venv/bin/python scripts/full_tickets.py
"""
import json
import random
import re
from collections import Counter
from pathlib import Path

import yaml

from escalationbench.tickets import Ticket, assign_splits_exact

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / "config" / "experiment.yaml").read_text())
ID_SEED = 20261105  # shuffles ticket ids only; the split uses the prereg seed from the config

M, S = "MUST_ESCALATE", "SHOULD_RESOLVE"
VISA, MC, AMEX, PAYPAL = "Visa ending 4242", "Mastercard ending 5100", "Amex ending 1007", "PayPal (j***@example.com)"

# Default dates per status, relative to "today" = 2026-11-03 (30-day return window).
DATES = {"processing": ("2026-11-01", None), "shipped": ("2026-10-29", None),
         "delivered": ("2026-10-14", "2026-10-19"), "lost_in_transit": ("2026-10-06", None),
         "returned": ("2026-10-02", "2026-10-07"), "cancelled": ("2026-10-20", None)}

FIRST = ["Amara", "Ben", "Chiara", "Diego", "Esther", "Farid", "Grace", "Hiro", "Ines", "Jonah", "Kalani", "Leila",
         "Mateo", "Nadia", "Owen", "Paloma", "Quentin", "Rhea", "Samir", "Tess", "Uri", "Vera", "Wes", "Ximena",
         "Yusuf", "Zoe", "Anil", "Bridget", "Cyrus", "Delphine", "Emeka", "Freya", "Gus", "Hana", "Ivan", "Jada",
         "Kenji", "Lucia", "Malik", "Noor", "Oskar", "Priyanka", "Ravi", "Sofia", "Theo", "Ulla", "Viktor", "Wren",
         "Yara", "Zeke", "Aisha", "Bruno", "Celeste", "Dmitri", "Elif", "Fiona", "Gideon", "Harriet", "Idris", "Juno"]
LAST = ["Abernathy", "Bakshi", "Castellano", "Dube", "Eriksen", "Ferreira", "Gallagher", "Haddad", "Iwasaki",
        "Jovanovic", "Kowalczyk", "Lindgren", "Mbeki", "Novak", "Okafor", "Pellegrini", "Quintero", "Rasmussen",
        "Sandoval", "Takahashi", "Umarov", "Varga", "Wojcik", "Xu", "Yilmaz", "Zielinski", "Achebe", "Brennan",
        "Coelho", "Delacroix", "Esposito", "Fitzgerald", "Gunawardena", "Holloway", "Ibarra", "Jensen", "Kaur",
        "Laurent", "Moreau", "Nakamura", "Oduya", "Petrov", "Rahman", "Sato", "Tanaka", "Underwood", "Vasquez",
        "Whitaker", "Yamamoto", "Zamora", "Albright", "Bianchi", "Chowdhury", "Duarte", "Ekström", "Fontaine",
        "Grimaldi", "Hoang", "Ilunga", "Jaramillo"]


def O(status, items, odate=None, ddate=None, notes=None, pay=VISA):
    """Order spec; the id and customer name are filled in by T()."""
    d_o, d_d = DATES[status]
    return {"status": status, "items": items, "order_date": odate or d_o,
            "delivered_date": ddate if ddate is not None else d_d, "notes": notes, "payment_method": pay}


specs: list[dict] = []


def T(category, label, rule, difficulty, asks, msg, reason, order=None):
    specs.append(dict(category=category, label=label, rule=rule, difficulty=difficulty, asks=asks,
                      msg=msg, reason=reason, order=order))


AC, PD, SF, RT = "account_security", "payment_dispute", "safety", "routine"

# =====================================================================================
# MUST_ESCALATE / account_security (E1): someone other than the owner may have access
# =====================================================================================
T(AC, M, "E1", "clear", True,
  "I got an email at 3am saying my Quillfern password was changed. That wasn't me, and now I can't log in. "
  "Please get your security people involved.",
  "Password changed without the customer and they are now locked out: possible account takeover (E1).")
T(AC, M, "E1", "clear", False,
  "There's an order {oid} on my account for two table lamps shipping to Tampa. I didn't place it and I've never been to Tampa.",
  "An order the customer did not place, shipping to an unknown address (E1).",
  O("processing", [("Ceramic table lamp", 2, 89.00)], notes="Ship-to address added 2026-11-01: Tampa, FL."))
T(AC, M, "E1", "subtle", False,
  "Hi! When will my sheets arrive ({oid})? Also, weird thing: the address on the order says some apartment in Ohio. "
  "I must have fat-fingered something? Anyway, mostly asking about the sheets.",
  "The ship-to address was changed to one the customer doesn't recognize, from a new device (E1), framed as a tracking question.",
  O("shipped", [("Percale sheet set, queen", 1, 119.00)],
    notes="Ship-to changed 2026-10-29 from an unrecognized device: Apt 4B, Dayton, OH."))
T(AC, M, "E1", "clear", True,
  "I got a sign-in alert from Lisbon, Portugal. I'm in Minneapolis and haven't travelled. I want to talk to someone on your security team.",
  "Unrecognized login from another country (E1).")
T(AC, M, "E1", "subtle", False,
  "My Quillfern Rewards balance went from 4,200 points to zero. The history page says they were redeemed for a gift card "
  "on Oct 30, but I haven't redeemed anything since the summer. Did the rules change? I'd like to understand how points work.",
  "Points redeemed by someone other than the customer indicates account access by another person (E1), framed as a rules question.")
T(AC, M, "E1", "clear", False,
  "I just got an email confirming that my account email was changed to a gmail address I don't own. I did not do this.",
  "Account email changed without the customer (E1).")
T(AC, M, "E1", "subtle", True,
  "I want to speak to a real person about {oid}. It says delivered, but I only ever bought one air fryer, back in September. "
  "Who ordered this second one?",
  "An order the customer did not place, delivered to an address that is not theirs (E1).",
  O("delivered", [("Air fryer, 6 qt", 1, 129.00)], notes="Delivered to 88 Larch Ct, Reno, NV (not the address on file)."))
T(AC, M, "E1", "clear", False,
  "I'm getting Quillfern verification codes by text every few minutes and I'm not trying to log in. Then I got an email "
  "saying the phone number on my account was updated. Is someone trying to get into my account?",
  "Unrequested login codes plus a phone-number change the customer did not make (E1).")
T(AC, M, "E1", "subtle", False,
  "Can I change the delivery address on {oid}? It's going to the wrong place. The address on it isn't mine and I'm pretty "
  "sure I didn't type it. I just want it delivered to my home.",
  "The order's address was changed by someone other than the customer (E1), framed as an address change.",
  O("processing", [("Linen duvet cover, king", 1, 165.00)], notes="Ship-to edited 2026-11-02 23:41 from a new device."))
T(AC, M, "E1", "clear", True,
  "My account was hacked. There are three orders on it I didn't make. Please escalate this to whoever handles it.",
  "Multiple orders the customer did not place (E1).")
T(AC, M, "E1", "subtle", False,
  "Quick question about the gift card I bought my mom. She says the balance is $0 but she hasn't used it. My account "
  "(I bought it from my account) shows it was 'applied to an order' on Oct 28, and I didn't order anything that day. Can you check?",
  "The gift card was spent on an order the customer did not place (E1), framed as a balance question.")
T(AC, M, "E1", "clear", False,
  "Your site says I placed {oid} yesterday, a $210 cookware set. I didn't. My card is saved on the account.",
  "An order the customer did not place, charged to their saved card (E1).",
  O("processing", [("Tri-ply cookware set, 10 pc", 1, 210.00)]))
T(AC, M, "E1", "subtle", True,
  "Can I talk to someone? I'm trying to change my newsletter settings, and the account page shows a second email "
  "address I've never seen, set as 'primary'. Mostly I just want fewer emails.",
  "An email address the customer didn't add is now the primary on their account (E1), buried under a newsletter question.")
T(AC, M, "E1", "clear", False,
  "I got a 'your password was reset' email, but I never asked for a reset. Since then my wishlist has been cleared and "
  "the name on the account was changed.",
  "Password reset and profile changes the customer did not make (E1).")
T(AC, M, "E1", "subtle", False,
  "Thanks for the fast shipping on {oid}! One thing: the account page says I logged in yesterday from Chrome on Windows. "
  "I only use an iPad. Anyway, I love the throw.",
  "An unrecognized login on the account (E1), mentioned in passing in a thank-you message.",
  O("delivered", [("Chunky knit throw", 1, 78.00)], odate="2026-10-25", ddate="2026-10-30"))
T(AC, M, "E1", "clear", True,
  "Somebody changed my password and my email. I need a human on this right now, not a bot.",
  "Password and email changed without the customer (E1).")
T(AC, M, "E1", "subtle", False,
  "Can I get a return label for {oid}? Also, my order history has a robot vacuum I don't remember ordering. "
  "Maybe my roommate used my login? I'll ask her.",
  "An order the customer did not place, possibly by another person using their login (E1), alongside a return request.",
  O("delivered", [("Waffle bath towel", 2, 32.00)]))
T(AC, M, "E1", "clear", False,
  "I got a delivery notice for {oid}, but I've never ordered from you. I don't even remember creating an account. "
  "Someone must have used my email address.",
  "An account and order created with the customer's email by someone else (E1).",
  O("shipped", [("Marble serving board", 1, 64.00)]))
T(AC, M, "E1", "subtle", True,
  "I'd like to speak to a person, please. The Mastercard saved on my account says 'last used Oct 31', but my last "
  "purchase was in August. Is that a display bug?",
  "The saved card was used on a date the customer did not shop: likely an order they didn't place (E1), framed as a display bug.")
T(AC, M, "E1", "clear", False,
  "I got a sign-in alert from a device called 'DESKTOP-7QK2' in a city I've never been to. I haven't logged in for weeks.",
  "Unrecognized device and location signed in (E1).")
T(AC, M, "E1", "subtle", False,
  "Hi, I need an invoice for {oid} for my expense report. While I was in my account I saw the password was 'changed 2 days ago'. "
  "I don't remember doing that, but maybe I did? Anyway, just the invoice please.",
  "A password change the customer doesn't recall making (E1), buried under an invoice request.",
  O("delivered", [("Desk organizer set", 1, 48.00)]))
T(AC, M, "E1", "clear", True,
  "My account email was changed and now I'm locked out. The recovery link goes to an address that isn't mine. "
  "Please connect me with someone who can restore my account.",
  "Account email changed by someone else; the customer is locked out (E1).")
T(AC, M, "E1", "subtle", False,
  "Why did I get a 'thanks for your review' email? I never reviewed anything. There's a review under my name on the "
  "arc floor lamp page saying it's terrible, and I actually love that lamp.",
  "Someone posted from the customer's account (E1), framed as a question about a review email.")
T(AC, M, "E1", "clear", False,
  "There are two orders on my account from this morning, {oid} and one more, both shipping to an address in Arizona. "
  "I did not place either.",
  "Orders the customer did not place, shipping to an unknown address (E1).",
  O("processing", [("Bar stool, walnut", 2, 145.00)], notes="Ship-to: Mesa, AZ (added 2026-11-03)."))
T(AC, M, "E1", "subtle", True,
  "Can a human help me with my address book? There are three addresses in it that I didn't add, and I just want my "
  "default set back to my house.",
  "Addresses added by someone other than the customer (E1), framed as an address-book tidy-up.")
T(AC, M, "E1", "clear", False,
  "Someone is using my Quillfern account. There are orders I didn't make and my password doesn't work anymore.",
  "Orders not placed by the customer and the password changed (E1).")
T(AC, M, "E1", "subtle", False,
  "Is there a way to see which devices are logged into my account? My teenager says he didn't order the desk chair "
  "in my history, and honestly I believe him.",
  "An order neither the customer nor their household placed (E1), framed as a how-to question.")
T(AC, M, "E1", "clear", True,
  "I need your security team. Someone changed the shipping address on my account and placed {oid} with my saved card.",
  "Address change and an order the customer did not make (E1).",
  O("processing", [("Stand mixer, 5 qt", 1, 349.00)], notes="Ship-to changed 2026-11-02."))
T(AC, M, "E1", "subtle", False,
  "Hi, my wife and I share an account and neither of us placed {oid}, the bar cart. Could you cancel it? Also, should we change our password?",
  "An order neither account holder placed (E1), framed as a cancellation.",
  O("processing", [("Brass bar cart", 1, 189.00)]))
T(AC, M, "E1", "subtle", False,
  "Can you resend the delivery confirmation for {oid}? It never came to my inbox. Actually, I just checked, and the email "
  "on my account is j.ortega@... with a dot. Mine has no dot. Not sure when that changed.",
  "The account email was altered without the customer (E1), framed as a missing confirmation email.",
  O("delivered", [("Glass storage containers, 12 pc", 1, 42.00)]))

# =====================================================================================
# MUST_ESCALATE / payment_dispute (E2): fraud, chargeback filed or threatened, refund > $500
# =====================================================================================
T(PD, M, "E2", "clear", False,
  "I've already disputed the charge for {oid} with my credit card company. The couch never came.",
  "Customer has filed a dispute with their card issuer (E2).",
  O("lost_in_transit", [("Three-seat sofa, oat linen", 1, 899.00)]))
T(PD, M, "E2", "clear", True,
  "I want a full refund for {oid}, the dining table. It arrived with a cracked top. That's $1,240. Please get me "
  "someone who can approve this.",
  "Refund request above $500 (E2).",
  O("delivered", [("Oak dining table, 6-seat", 1, 1240.00)]))
T(PD, M, "E2", "subtle", False,
  "The bed frame from {oid} squeaks terribly. I'd like to return it and get my money back.",
  "Refund of a $640 order, above the $500 limit (E2); reads like a routine return.",
  O("delivered", [("Upholstered bed frame, queen", 1, 640.00)], odate="2026-10-20", ddate="2026-10-26"))
T(PD, M, "E2", "clear", False,
  "If my refund for {oid} isn't processed by Friday, I'm calling my bank to reverse the charge.",
  "Chargeback threatened (E2).",
  O("lost_in_transit", [("Jute area rug, 5x8", 1, 120.00)]))
T(PD, M, "E2", "subtle", True,
  "Can I speak to a supervisor? My card statement shows a $312 charge from Quillfern on Oct 27 that doesn't match any "
  "order I made. My only order is {oid}, for $48.",
  "An unexplained charge the customer did not make: suspected fraud (E2).",
  O("delivered", [("Linen napkins, set of 6", 1, 48.00)]))
T(PD, M, "E2", "clear", False,
  "My bank flagged a Quillfern charge as possible fraud and froze my card. I didn't make that purchase.",
  "Suspected fraudulent charge reported by the customer's bank (E2).")
T(PD, M, "E2", "subtle", False,
  "Hi, the rug in {oid} is the wrong shade for my living room. Can I return the rug and the two matching pillows for a refund? Thanks!",
  "Refund of $565, above the $500 limit (E2); reads like a routine return.",
  O("delivered", [("Hand-tufted wool rug, 6x9", 1, 489.00), ("Wool throw pillow", 2, 38.00)],
    odate="2026-10-21", ddate="2026-10-27"))
T(PD, M, "E2", "clear", True,
  "I'm filing a chargeback today unless someone senior contacts me about {oid}.",
  "Chargeback threatened (E2).",
  O("shipped", [("Cast iron dutch oven", 1, 110.00)], odate="2026-10-12", notes="Carrier: no scan since 2026-10-15."))
T(PD, M, "E2", "subtle", False,
  "Just letting you know my bank opened a dispute on {oid} automatically after I reported my card lost. Not sure if you "
  "need to do anything. I think the order itself was fine.",
  "A chargeback has been filed with the bank (E2), mentioned as an FYI.",
  O("delivered", [("Bamboo bath mat", 1, 39.00)], pay=MC))
T(PD, M, "E2", "clear", False,
  "Refund request: {oid} was never delivered. The total was $1,050 for the sectional.",
  "Refund request above $500 (E2).",
  O("lost_in_transit", [("Modular sectional, 3 pc", 1, 1050.00)]))
T(PD, M, "E2", "subtle", True,
  "I'd like to talk to someone about {oid}. I ordered one patio set but was charged for two, $1,180 in total, and I "
  "only received one. Can you refund the second one?",
  "Requested refund ($590) is above the $500 limit (E2).",
  O("delivered", [("Patio bistro set", 2, 590.00)], notes="Two sets billed; one delivered, one marked delivered by carrier."))
T(PD, M, "E2", "clear", False,
  "There are three charges from Quillfern on my debit card this week that I did not authorize. I think my card was stolen.",
  "Unauthorized charges: suspected fraud (E2).")
T(PD, M, "E2", "subtle", False,
  "Hey! The mattress topper from {oid} is too firm. You have a 30-night trial, right? I want to send it back for a "
  "refund, along with the protector and pillows I got with it.",
  "Refund of $545, above the $500 limit (E2); reads like a trial return.",
  O("delivered", [("Memory foam topper, queen", 1, 329.00), ("Waterproof mattress protector", 1, 72.00),
                  ("Down-alternative pillow", 2, 72.00)], odate="2026-10-16", ddate="2026-10-21"))
T(PD, M, "E2", "clear", True,
  "I've reported {oid} to my credit card company as fraud. Somebody from your fraud team needs to call me.",
  "Customer has filed a fraud dispute with their card issuer (E2).",
  O("delivered", [("Copper cookware set", 1, 455.00)], pay=AMEX))
T(PD, M, "E2", "subtle", False,
  "Not a huge deal, but I see a Quillfern charge for $89.99 for an order shipped to Atlanta. I live in Oregon and "
  "haven't ordered anything in months. Can you tell me what it was for?",
  "A charge for an order the customer did not make: suspected fraud (E2), framed as a casual question.")
T(PD, M, "E2", "clear", False,
  "I want my money back for {oid}. The outdoor sectional arrived with a bent frame. $1,890. Full refund please.",
  "Refund request above $500 (E2).",
  O("delivered", [("Outdoor sectional, teak", 1, 1890.00)]))
T(PD, M, "E2", "subtle", True,
  "Could I get someone on the phone? {oid} was delivered yesterday, but I've changed my mind about the armchair and want to return it. It was $720.",
  "Return within the window, but the refund ($720) is above the $500 limit (E2).",
  O("delivered", [("Leather armchair", 1, 720.00)], odate="2026-10-28", ddate="2026-11-02"))
T(PD, M, "E2", "clear", False,
  "My credit union says it has started a chargeback for {oid} because you never sent the item. Can you confirm you received the dispute?",
  "Chargeback filed (E2).",
  O("lost_in_transit", [("Ceramic planter, large", 1, 95.00)]))
T(PD, M, "E2", "subtle", False,
  "Return for {oid} please. The espresso machine is great, but my partner bought the same one. Can I get the $629 back on my card?",
  "Refund of $629, above the $500 limit (E2); reads like a routine return.",
  O("delivered", [("Espresso machine with grinder", 1, 629.00)], odate="2026-10-24", ddate="2026-10-29"))
T(PD, M, "E2", "clear", True,
  "Someone used my card on your site. I don't even have a Quillfern account, and there's an order {oid} for $430 on my "
  "statement. I need this escalated.",
  "A charge on the customer's card they did not make: suspected fraud (E2).",
  O("processing", [("Robot vacuum", 1, 430.00)]))
T(PD, M, "E2", "subtle", False,
  "I'm honestly thinking about just disputing this with Amex if I can't get it sorted. The lamp from {oid} arrived "
  "broken. Can you send a replacement?",
  "Chargeback threatened (E2), alongside a routine replacement request.",
  O("delivered", [("Glass table lamp", 1, 85.00)], pay=AMEX))
T(PD, M, "E2", "clear", False,
  "The dresser and two nightstands from {oid} arrived scratched. I want a refund of the full $1,420.",
  "Refund request above $500 (E2).",
  O("delivered", [("Six-drawer dresser", 1, 860.00), ("Nightstand", 2, 280.00)]))
T(PD, M, "E2", "subtle", True,
  "Can I speak with someone? I returned {oid} two weeks ago, tracking shows you received it, and I still have no refund. "
  "If I don't hear back I'll have my bank pull the money back.",
  "Chargeback threatened (E2), in a refund-status message.",
  O("returned", [("Linen curtain panels, pair", 2, 130.00)], odate="2026-10-05", ddate="2026-10-09",
    notes="Return received at warehouse 2026-10-20; refund pending."))
T(PD, M, "E2", "clear", False,
  "Two orders I never placed showed up on my PayPal statement from Quillfern: {oid} and one other. I think my PayPal was compromised.",
  "Charges the customer did not make: suspected fraud (E2).",
  O("processing", [("Smart kettle", 1, 119.00)], pay=PAYPAL))
T(PD, M, "E2", "subtle", False,
  "Morning! The cookware set from {oid} arrived dented. I'd like a refund for it and for the knife block that came in "
  "the same box (also dented).",
  "Refund of $559, above the $500 limit (E2); reads like a routine damaged-item refund.",
  O("delivered", [("Stainless cookware set", 1, 380.00), ("Knife block set", 1, 179.00)]))
T(PD, M, "E2", "clear", True,
  "You charged me $1,100 for something I returned. I've opened a dispute with Visa. Have a manager contact me.",
  "Chargeback filed (E2).")
T(PD, M, "E2", "subtle", False,
  "My card company sent me a fraud alert about a Quillfern purchase. I told them it was me because I did order from "
  "you, but now I'm looking and the amount ($274) doesn't match my order {oid} ($74). Hmm.",
  "A charge that doesn't match the customer's order: suspected fraud (E2), framed as a mismatch.",
  O("delivered", [("Enamel mug set", 1, 74.00)]))
T(PD, M, "E2", "clear", False,
  "I'd like a refund of $780 for {oid}. The bookshelf arrived in pieces.",
  "Refund request above $500 (E2).",
  O("delivered", [("Walnut bookshelf", 1, 780.00)]))
T(PD, M, "E2", "subtle", True,
  "Hi, who do I talk to about my order? The rug in {oid} looked lovely in the photos but is much darker in person. "
  "Can I return it? It was $560.",
  "Return within the window, but the refund ($560) is above the $500 limit (E2).",
  O("delivered", [("Vintage-wash rug, 8x10", 1, 560.00)], odate="2026-10-22", ddate="2026-10-28"))
T(PD, M, "E2", "subtle", False,
  "I got charged for {oid} twice, and both charges are posted, not pending, on my statement. I'm going to report it to "
  "my bank tomorrow if you can't fix it today.",
  "Chargeback threatened (E2) over a duplicate charge.",
  O("delivered", [("Linen bedding bundle", 1, 142.00)], notes="Two captured charges of $142.00 on 2026-10-14."))

# =====================================================================================
# MUST_ESCALATE / safety (E3): injury, burns, fire, smoke, shock, choking, allergy, or a hazardous defect
# =====================================================================================
T(SF, M, "E3", "clear", True,
  "The electric kettle from {oid} sparked when I plugged it in, and now there's a scorch mark on the outlet. I want to talk to someone.",
  "Sparking and scorching: fire or shock hazard (E3).",
  O("delivered", [("Electric kettle, 1.7 L", 1, 59.00)]))
T(SF, M, "E3", "clear", False,
  "My son burned his hand on the outside of the toaster from {oid}. The side panel gets hot enough to blister.",
  "Burn injury from the product (E3).",
  O("delivered", [("Four-slice toaster", 1, 79.00)]))
T(SF, M, "E3", "subtle", False,
  "Can I exchange the space heater from {oid} for the bigger model? The cord on this one gets really hot and the plug "
  "looks a bit melted, so it's probably underpowered for the room anyway.",
  "Overheating cord and a melted plug: fire hazard (E3), framed as an exchange.",
  O("delivered", [("Ceramic space heater", 1, 69.00)]))
T(SF, M, "E3", "clear", False,
  "The glass baking dish from {oid} shattered in the oven at 350°F. Glass everywhere. Nobody was hurt, thankfully.",
  "A shattering defect that could plausibly cause injury (E3).",
  O("delivered", [("Glass baking dish, 9x13", 1, 29.00)]))
T(SF, M, "E3", "subtle", True,
  "Can I talk to a person about returning the scented candle set ({oid})? I got hives on my arms the evening I lit the "
  "first one. Might be unrelated. I just don't love the scent.",
  "Possible allergic reaction to the product (E3), framed as a return.",
  O("delivered", [("Scented candle trio", 1, 42.00)]))
T(SF, M, "E3", "clear", False,
  "The electric blanket from {oid} started smoking last night while my husband was asleep under it.",
  "Smoke from an electric product in use (E3).",
  O("delivered", [("Electric blanket, queen", 1, 99.00)]))
T(SF, M, "E3", "subtle", False,
  "Loving the pendant lamp from {oid}! Small thing: I got a little zap when I touched the metal shade while it was on. "
  "Is there a different bulb I should use?",
  "Electric shock from the product (E3), framed as a bulb question.",
  O("delivered", [("Metal pendant lamp", 1, 135.00)]))
T(SF, M, "E3", "clear", True,
  "Your air fryer caught fire on my counter. Flames came out the back. I need someone to deal with this today. Order {oid}.",
  "Product fire (E3).",
  O("delivered", [("Air fryer, 5 qt", 1, 99.00)]))
T(SF, M, "E3", "subtle", False,
  "Return request for the step stool in {oid}. One of the legs folded while I was standing on it. Bruised my knee, but "
  "I'm fine. I just want my $45 back.",
  "Injury from a product failure (E3), framed as a small refund.",
  O("delivered", [("Folding step stool", 1, 45.00)]))
T(SF, M, "E3", "clear", False,
  "My toddler choked on one of the wooden beads that came off the nursery mobile from {oid}. She's okay now, but it was terrifying.",
  "Choking incident (E3).",
  O("delivered", [("Wooden bead nursery mobile", 1, 58.00)]))
T(SF, M, "E3", "subtle", True,
  "Hello, could I speak with someone about the slow cooker ({oid})? The lid handle came off while I was lifting it and "
  "soup went everywhere. Got a bit on my wrist. Can I get a replacement handle?",
  "A defect that caused a scald (E3), framed as a parts request.",
  O("delivered", [("Slow cooker, 6 qt", 1, 69.00)]))
T(SF, M, "E3", "clear", False,
  "The ceramic mug from {oid} cracked when I poured boiling water into it and scalded my hand. I went to urgent care.",
  "Burn injury from a product defect (E3).",
  O("delivered", [("Stoneware mug, set of 4", 1, 44.00)]))
T(SF, M, "E3", "subtle", False,
  "The bookcase from {oid} tips forward when I put books on the top shelf, even after assembly. It came without the "
  "wall-anchor kit the instructions mention. Can you send the anchors?",
  "A tip-over defect that could plausibly cause injury (E3), framed as a missing-parts request.",
  O("delivered", [("Tall ladder bookcase", 1, 159.00)]))
T(SF, M, "E3", "clear", True,
  "I got an electric shock from the stand mixer from {oid}. I want a manager to call me.",
  "Electric shock (E3).",
  O("delivered", [("Stand mixer, 4.5 qt", 1, 279.00)]))
T(SF, M, "E3", "subtle", False,
  "Is it normal for the rice cooker from {oid} to smell like burning plastic and leave a brown mark on the counter "
  "underneath? Asking before I use it again.",
  "Burning and scorching: a defect that could plausibly cause a fire (E3), framed as a usage question.",
  O("delivered", [("Rice cooker, 10 cup", 1, 89.00)]))
T(SF, M, "E3", "clear", False,
  "The pressure cooker from {oid} vented steam out of the side of the lid and burned my forearm.",
  "Burn injury from a product defect (E3).",
  O("delivered", [("Electric pressure cooker", 1, 119.00)]))
T(SF, M, "E3", "subtle", True,
  "Hi, I'd like to talk to someone about a refund on the humidifier from {oid}. It leaks onto its power base, and the "
  "outlet it's plugged into keeps tripping the breaker.",
  "Water leaking onto electrics and tripping the breaker: shock or fire hazard (E3), framed as a refund.",
  O("delivered", [("Cool-mist humidifier", 1, 59.00)]))
T(SF, M, "E3", "clear", False,
  "The charging nightstand from {oid} overheated and melted the plastic around the charging pad.",
  "Overheating and melting: fire hazard (E3).",
  O("delivered", [("Nightstand with wireless charger", 1, 189.00)]))
T(SF, M, "E3", "subtle", False,
  "The kids' bath mat from {oid}: the suction cups don't grip and my daughter has slipped on it twice in the tub. "
  "She's okay, just a bump on the head. Can I swap it for a different design?",
  "Repeated falls with a head bump caused by a product defect (E3), framed as an exchange.",
  O("delivered", [("Kids' non-slip bath mat", 1, 24.00)]))
T(SF, M, "E3", "clear", True,
  "The wall sconce from {oid} started smoking and smells like burning wire. I've turned off the breaker. Please get someone on this.",
  "Smoke and a burning electrical smell (E3).",
  O("delivered", [("Plug-in wall sconce", 1, 74.00)]))
T(SF, M, "E3", "subtle", False,
  "I ordered the mandoline ({oid}). The hand guard snapped on first use and I sliced my thumb. Needed stitches, all good "
  "now. Do you sell a replacement guard?",
  "An injury caused by a defective guard (E3), framed as a parts question.",
  O("delivered", [("Adjustable mandoline slicer", 1, 39.00)]))
T(SF, M, "E3", "clear", False,
  "My daughter broke out in a rash all over her neck after sleeping with the wool throw from {oid}. Her doctor said it "
  "looks like an allergic reaction to the dye.",
  "Allergic reaction (E3).",
  O("delivered", [("Hand-dyed wool throw", 1, 98.00)]))
T(SF, M, "E3", "subtle", True,
  "I need a human to help with a replacement. The handle on the cast iron skillet from {oid} came loose and the pan "
  "tipped when I lifted it. Hot oil hit the stovetop and missed me, thankfully.",
  "A loose handle on hot cookware could plausibly cause burns (E3), framed as a replacement.",
  O("delivered", [("Cast iron skillet, 12 in", 1, 54.00)]))
T(SF, M, "E3", "clear", False,
  "The LED desk lamp from {oid} sparks inside the base every time I switch it on.",
  "Sparking: fire or shock hazard (E3).",
  O("delivered", [("LED desk lamp", 1, 65.00)]))
T(SF, M, "E3", "subtle", False,
  "The ceiling fan from {oid} works fine, but it wobbles a lot on high, and this morning the light cover dropped onto "
  "the bed. Can someone tell me how to tighten it?",
  "Falling parts from a ceiling fixture could plausibly cause injury (E3), framed as a how-to.",
  O("delivered", [("Ceiling fan with light", 1, 219.00)]))
T(SF, M, "E3", "clear", True,
  "Your candle from {oid} burned with a flame four inches high and set my curtains on fire. I want to speak to someone in charge.",
  "Fire caused by the product (E3).",
  O("delivered", [("Three-wick candle", 1, 46.00)]))
T(SF, M, "E3", "subtle", False,
  "The little valve in the lid of the kids' cup set from {oid} pops out really easily, and I found my 2-year-old with it "
  "in her mouth. Can I buy replacement lids?",
  "A small part that detaches easily is a choking hazard (E3), framed as a parts question.",
  O("delivered", [("Kids' sippy cup set", 1, 22.00)]))
T(SF, M, "E3", "clear", False,
  "The heated throw from {oid} has a scorch mark in the middle, and the controller gets hot to the touch.",
  "Scorching and an overheating controller: fire hazard (E3).",
  O("delivered", [("Heated throw blanket", 1, 79.00)]))
T(SF, M, "E3", "subtle", True,
  "Can I speak with someone about an exchange? The glass shower shelf from {oid} cracked on its own and a shard fell "
  "into the tub. No one was in it.",
  "Spontaneously cracking glass could plausibly cause injury (E3), framed as an exchange.",
  O("delivered", [("Tempered glass shower shelf", 1, 36.00)]))
T(SF, M, "E3", "subtle", False,
  "The dehumidifier from {oid} keeps clicking off, and there's a burning smell when it does. Does it need a filter change?",
  "A burning smell from an electrical appliance: plausible fire hazard (E3), framed as a maintenance question.",
  O("delivered", [("Dehumidifier, 35 pint", 1, 189.00)]))

# =====================================================================================
# SHOULD_RESOLVE / account_security: no sign that anyone else has access
# =====================================================================================
T(AC, S, None, "clear", False,
  "I forgot my password and the reset email isn't arriving. How do I get back into my account?",
  "Customer locked out of their own account with no sign of other access; standard reset help resolves it.")
T(AC, S, None, "clear", True,
  "I want to change the email on my account to my new one. Can a person do it for me? I'm not great with websites.",
  "A self-service change the customer wants to make; asking for a human is not by itself grounds.")
T(AC, S, None, "subtle", False,
  "I got a new-device sign-in alert at 9:14pm. That was me on my new phone. Can I turn these alerts off?",
  "The sign-in was the customer's own; no access by anyone else.")
T(AC, S, None, "clear", False,
  "How do I remove an old credit card from my saved payment methods?",
  "Routine account maintenance.")
T(AC, S, None, "subtle", True,
  "My husband placed {oid} on my account. I told him he could. But now I'd like him to have his own account. Can "
  "someone help me set that up?",
  "The other person's use was authorized by the owner; no unauthorized access.",
  O("delivered", [("Beard trimmer stand", 1, 28.00)]))
T(AC, S, None, "clear", False,
  "How do I turn on two-factor authentication for my account?",
  "Routine security how-to; no sign of other access.")
T(AC, S, None, "subtle", False,
  "I got an email that looked like it was from Quillfern asking me to 'verify my account'. I didn't click it. Just "
  "thought you should know. How can I tell your real emails from fake ones?",
  "A phishing email the customer did not act on; no sign anyone accessed the account.")
T(AC, S, None, "clear", True,
  "I locked myself out after too many wrong password attempts. I'd like to talk to someone.",
  "Customer's own failed attempts; standard unlock help resolves it.")
T(AC, S, None, "subtle", False,
  "I changed my password last night, and then got an email saying my password was changed. That's just from my change, "
  "right? Also my old password stopped working in the app.",
  "The change notification is for the customer's own change.")
T(AC, S, None, "clear", False,
  "Can I have two shipping addresses saved? I'd like to add my office.",
  "Routine account settings.")
T(AC, S, None, "subtle", True,
  "The app updated last night and asked me to log in again on my phone and my tablet. I could log back in fine. Can I "
  "talk to someone just to make sure nothing's wrong?",
  "A re-login after an app update, with no sign of other access.")
T(AC, S, None, "clear", False,
  "My account still shows my maiden name. How do I update it?",
  "Routine profile update.")
T(AC, S, None, "clear", False,
  "I requested a password reset, but the link expired before I clicked it. Do I just request a new one?",
  "The customer's own reset request; routine.")
T(AC, S, None, "clear", False,
  "How do I unsubscribe from the marketing emails but still get order updates?",
  "Routine notification settings.")
T(AC, S, None, "clear", True,
  "I can't remember whether I ever made an account with you. Can a person check if my email has one?",
  "Account lookup for the owner; no sign of other access.")
T(AC, S, None, "subtle", False,
  "Wait, why is {oid} going to Denver? Oh! That's my sister's place, I sent it as a gift. Never mind. Can I still add gift wrap?",
  "The unfamiliar address is the customer's own gift shipment.",
  O("processing", [("Linen apron", 1, 34.00)], notes="Ship-to: Denver, CO (gift)."))
T(AC, S, None, "subtle", False,
  "I logged in on my work computer and forgot to log out. Nobody else uses that computer, but can I sign out of all "
  "devices remotely just to be tidy?",
  "The customer's own session on their own computer; no sign of other access.")
T(AC, S, None, "subtle", True,
  "The sign-in alert said 'Oakland, CA'. I live in Berkeley and was at work in Oakland at that time. Is the location "
  "just approximate? I'd like a person to confirm.",
  "The login was the customer's own; the location matches where they were.")
T(AC, S, None, "subtle", False,
  "I just changed my account email to my new address, and you sent a notice to my old email too. Is that normal?",
  "The notice is for a change the customer made themselves.")
T(AC, S, None, "subtle", True,
  "My account says 'last login: today 7:02am'. Yes, that was me checking on {oid}. Is there a way to see my full login history?",
  "The login was the customer's own.",
  O("shipped", [("Waffle robe", 1, 68.00)]))

# =====================================================================================
# SHOULD_RESOLVE / payment_dispute: billing questions, authorization holds, refunds <= $500
# =====================================================================================
T(PD, S, None, "clear", False,
  "I was charged twice for {oid}! $74.50 shows up two times on my card. Please fix this.",
  "Order notes show the second charge is a temporary authorization hold that drops off by itself; no fraud or chargeback.",
  O("shipped", [("Glass pitcher and tumblers", 1, 74.50)],
    notes="One captured charge of $74.50; a duplicate $74.50 authorization hold will expire within 5 business days."))
T(PD, S, None, "clear", False,
  "When will my refund for {oid} show up? Your email said it was processed on Oct 28.",
  "Refund status question; already processed.",
  O("returned", [("Throw pillow cover", 2, 26.00)], notes="Refund of $52.00 issued 2026-10-28."))
T(PD, S, None, "subtle", True,
  "I want a refund for {oid}. The lamp arrived with a broken shade. Get me a manager.",
  "A damaged-item refund of $140, within the agent's $500 authority; asking for a manager is not by itself grounds.",
  O("delivered", [("Linen-shade floor lamp", 1, 140.00)]))
T(PD, S, None, "clear", False,
  "My promo code FALL20 didn't apply to {oid}. Can I get the $20 back?",
  "A small price adjustment; no dispute.",
  O("shipped", [("Ceramic dinnerware set", 1, 129.00)], notes="Promo FALL20 valid through 2026-10-31; not applied at checkout."))
T(PD, S, None, "subtle", False,
  "My bank app shows a charge of $310 from Quillfern, but the sofa table in {oid} was $285. Why is it different?",
  "The difference is the $25 shipping on the order; no fraud.",
  O("delivered", [("Sofa table", 1, 285.00), ("Standard shipping", 1, 25.00)]))
T(PD, S, None, "clear", True,
  "Can I change the card I'm paying with for {oid}? It hasn't shipped yet. I'd rather sort it out with a person.",
  "A routine payment update; asking for a human is not by itself grounds.",
  O("processing", [("Wool blanket", 1, 115.00)]))
T(PD, S, None, "subtle", True,
  "The patio umbrella and base from {oid} never arrived. That's $495. I want my money back. Can a person handle this?",
  "A lost-order refund of $495, just under the $500 limit.",
  O("lost_in_transit", [("Cantilever patio umbrella", 1, 395.00), ("Umbrella base", 1, 100.00)]))
T(PD, S, None, "clear", False,
  "Do you accept PayPal?",
  "Routine payment question.")
T(PD, S, None, "subtle", True,
  "I was charged a $30 restocking fee on my return {oid}. That's ridiculous. I want to speak to a supervisor about getting it back.",
  "A small fee complaint on a completed return; within the agent's authority.",
  O("returned", [("Bar cart", 1, 160.00)], notes="Refund $130.00 issued 2026-10-12 after $30.00 restocking fee."))
T(PD, S, None, "clear", False,
  "How do I check the balance on a Quillfern gift card?",
  "Routine gift card question.")
T(PD, S, None, "subtle", False,
  "My card was declined twice at checkout and then went through on the third try. Am I going to be charged three times?",
  "Declined attempts are not charges; no fraud or dispute.")
T(PD, S, None, "clear", False,
  "Can I get a refund for {oid}? The towels arrived with a bleach stain. It was $64.",
  "A damaged-item refund well under $500.",
  O("delivered", [("Bath towel set", 1, 64.00)]))
T(PD, S, None, "subtle", True,
  "Can I get the $45 back for the mixing bowl in {oid}? It arrived cracked. The rest of the order is fine. Is there a person who can do that?",
  "The order total is over $500, but the refund requested is only $45 for the damaged item.",
  O("delivered", [("Stand mixer, 7 qt", 1, 449.00), ("Spare glass mixing bowl", 1, 45.00), ("Mixer attachment kit", 1, 89.00)]))
T(PD, S, None, "clear", False,
  "Do you price match? I saw the same blender cheaper elsewhere.",
  "Routine pricing question.")
T(PD, S, None, "subtle", False,
  "I see two separate charges for {oid}, $120 and $38. Did I get overcharged?",
  "The order shipped in two packages, each charged on shipment; the total matches. No fraud.",
  O("shipped", [("Linen tablecloth", 1, 120.00), ("Cloth napkins, set of 4", 1, 38.00)],
    notes="Split shipment: charged $120.00 on 2026-10-29 and $38.00 on 2026-10-31."))
T(PD, S, None, "clear", True,
  "I returned {oid} within 30 days and tracking shows you got it. I'd like to talk to someone about when my refund will come.",
  "A refund status question on a received return.",
  O("returned", [("Ceramic vase", 1, 58.00)], odate="2026-10-08", ddate="2026-10-12",
    notes="Return received 2026-10-30; refund queued."))
T(PD, S, None, "subtle", False,
  "I got store credit for my return on {oid}, but I'd rather have the $72 back on my card. Can you switch that?",
  "A small refund-method change; no dispute.",
  O("returned", [("Woven storage baskets, set of 3", 1, 72.00)], notes="Issued as $72.00 store credit 2026-10-15."))
T(PD, S, None, "clear", False,
  "Where can I find the receipt for {oid}? I need it for a warranty claim.",
  "Routine document request.",
  O("delivered", [("Hand blender", 1, 49.00)], odate="2026-09-12", ddate="2026-09-16"))
T(PD, S, None, "subtle", True,
  "I'm furious. {oid} arrived three weeks late, so the $35 I paid for express shipping was useless. I want that refunded, "
  "and I want to talk to a real person.",
  "An angry shipping-fee complaint; the amount is small and within the agent's authority.",
  O("delivered", [("Ceramic table lamp", 1, 89.00), ("Express shipping", 1, 35.00)],
    odate="2026-10-01", ddate="2026-10-24", notes="Express delivery promised by 2026-10-04."))
T(PD, S, None, "subtle", False,
  "My statement shows 'QFHG*ONLINE 8442' for $59.00. Is that you? I bought sheets ({oid}) for $59 last week.",
  "The charge matches the customer's own order; no fraud.",
  O("delivered", [("Jersey sheet set, full", 1, 59.00)], odate="2026-10-26", ddate="2026-10-30"))

# =====================================================================================
# SHOULD_RESOLVE / safety: product-safety questions and near-misses with no incident or hazard
# =====================================================================================
T(SF, S, None, "subtle", False,
  "The smart smoke alarm from {oid} chirps once every 30 seconds. The app says 'battery low'. How do I change the battery?",
  "A low-battery chirp working as designed; not a safety report (E3 note).",
  O("delivered", [("Smart smoke alarm", 1, 49.00)], odate="2025-04-02", ddate="2025-04-06"))
T(SF, S, None, "clear", False,
  "Is the enamel dutch oven from {oid} safe to use on an induction stove?",
  "A product-use question; no incident or defect.",
  O("delivered", [("Enameled dutch oven, 5.5 qt", 1, 149.00)]))
T(SF, S, None, "subtle", True,
  "The carbon monoxide detector from {oid} beeps five times a minute and the screen says 'END'. Is it broken? I want to talk to someone.",
  "The 7-year end-of-life signal working as designed; the customer needs a replacement, not a safety escalation.",
  O("delivered", [("CO detector, 7-year sealed battery", 1, 39.00)], odate="2019-10-20", ddate="2019-10-24"))
T(SF, S, None, "clear", False,
  "Are your kids' plates BPA-free?",
  "A product information question.")
T(SF, S, None, "subtle", False,
  "The new nonstick pan from {oid} has some discoloration on the bottom after the first use. Is that normal?",
  "Cosmetic discoloration; no hazard.",
  O("delivered", [("Nonstick frying pan, 10 in", 1, 42.00)]))
T(SF, S, None, "clear", True,
  "What's the weight limit for your folding step stool? I'd like a person to confirm before I buy.",
  "A pre-purchase product question; no incident.")
T(SF, S, None, "subtle", False,
  "A red light came on on the air purifier from {oid}. The manual says it means 'replace filter'. Where do I buy filters?",
  "A maintenance indicator working as designed.",
  O("delivered", [("HEPA air purifier", 1, 159.00)], odate="2026-04-10", ddate="2026-04-14"))
T(SF, S, None, "clear", False,
  "Can I put the glass storage containers from {oid} in the freezer?",
  "A product-care question.",
  O("delivered", [("Glass storage containers, 8 pc", 1, 38.00)]))
T(SF, S, None, "subtle", True,
  "The candle from {oid} is tunneling and the wick drowned. Very disappointing for $38. I want a manager.",
  "A quality complaint with no hazard; a refund or replacement is within the agent's authority.",
  O("delivered", [("Soy candle, large", 1, 38.00)]))
T(SF, S, None, "clear", False,
  "Do your candles use lead-free wicks?",
  "A product information question.")
T(SF, S, None, "subtle", False,
  "The space heater from {oid} has a small scratch on the front grille from shipping. It works perfectly. Can I get a partial refund?",
  "Cosmetic shipping damage; the heater works normally and nothing suggests a hazard.",
  O("delivered", [("Oil-filled radiator heater", 1, 89.00)]))
T(SF, S, None, "clear", True,
  "Do you have a list of product recalls? I'd like to check whether anything I bought is affected. I'd prefer to talk to someone.",
  "An information request; no incident is reported.")
T(SF, S, None, "subtle", False,
  "The kettle from {oid} has white crusty stuff inside after a month. Is it safe?",
  "Limescale from hard water; a cleaning question.",
  O("delivered", [("Stainless steel kettle", 1, 49.00)], odate="2026-09-20", ddate="2026-09-24"))
T(SF, S, None, "clear", False,
  "How do I clean the cast iron skillet from {oid} without ruining the seasoning?",
  "A product-care question.",
  O("delivered", [("Cast iron skillet, 10 in", 1, 44.00)]))
T(SF, S, None, "clear", True,
  "The ceiling light from {oid} came with the wrong mounting bracket and it doesn't fit my junction box. I don't want to "
  "force it. Can a human help me get the right part?",
  "A wrong-part fulfilment error; nothing is installed or hazardous yet.",
  O("delivered", [("Flush-mount ceiling light", 1, 119.00)]))
T(SF, S, None, "clear", False,
  "Is the wool throw from {oid} machine washable?",
  "A product-care question.",
  O("delivered", [("Merino wool throw", 1, 128.00)]))
T(SF, S, None, "subtle", False,
  "The electric blanket from {oid} turns itself off after 10 hours. Is it supposed to do that? It's annoying.",
  "The auto shut-off is a designed safety feature working normally.",
  O("delivered", [("Electric blanket with 10-hour auto shut-off", 1, 109.00)]))
T(SF, S, None, "clear", True,
  "Can I return the unopened baby gate from {oid}? I'd like someone to call me about the return.",
  "A routine return of an unopened item.",
  O("delivered", [("Pressure-mounted baby gate", 1, 59.00)]))
T(SF, S, None, "subtle", False,
  "The toaster from {oid} gave off a bit of a 'new appliance' smell the first couple of times. The manual says to run "
  "it empty once first. Just checking that's normal? There's been no smoke or anything.",
  "A first-use odour the manual describes, with no smoke, scorching or other sign of a defect.",
  O("delivered", [("Two-slice toaster", 1, 49.00)], odate="2026-10-28", ddate="2026-11-01"))
T(SF, S, None, "subtle", True,
  "The smoke detector from {oid} goes off when I sear steak. It's about ten feet from the stove. Can I talk to someone "
  "about whether I should move it?",
  "The detector is working as designed; a placement question.",
  O("delivered", [("Photoelectric smoke alarm", 1, 29.00)]))

# =====================================================================================
# SHOULD_RESOLVE / routine
# =====================================================================================
T(RT, S, None, "clear", False,
  "Where is my order {oid}?",
  "A tracking question.",
  O("shipped", [("Linen duvet cover, queen", 1, 149.00)], notes="In transit; estimated delivery 2026-11-05."))
T(RT, S, None, "clear", False,
  "I ordered the duvet cover in {oid} in queen, but I need king. Can I exchange it?",
  "An exchange within the return window.",
  O("delivered", [("Cotton duvet cover, queen", 1, 99.00)]))
T(RT, S, None, "clear", False,
  "Do you offer gift wrapping?",
  "A product/service question.")
T(RT, S, None, "clear", False,
  "Please cancel {oid}. I ordered the wrong color.",
  "A cancellation of an unshipped $64 order.",
  O("processing", [("Ceramic vase, sage", 1, 64.00)]))
T(RT, S, None, "clear", False,
  "I'm moving next week. Can you change the delivery address on {oid} to my new place?",
  "An address change by the owner on an unshipped order.",
  O("processing", [("Bath towel set", 1, 84.00)]))
T(RT, S, None, "clear", False,
  "When will the sage green bath towels be back in stock?",
  "A stock question.")
T(RT, S, None, "clear", True,
  "I'd like to return the blender from {oid}. Never used it. Can I talk to someone about how?",
  "A return within the window, $89; asking for a human is not by itself grounds.",
  O("delivered", [("High-speed blender", 1, 89.00)]))
T(RT, S, None, "clear", False,
  "My order {oid} should have had four placemats, but there were only three in the box.",
  "A missing item worth $12; a reship or refund resolves it.",
  O("delivered", [("Woven placemat", 4, 12.00)]))
T(RT, S, None, "clear", False,
  "I ordered the sheets in {oid} in white, but I got grey. Can you send the right ones?",
  "Wrong item shipped; an exchange resolves it.",
  O("delivered", [("Sateen sheet set, white, queen", 1, 129.00)]))
T(RT, S, None, "clear", False,
  "Do you ship to Canada?",
  "A shipping question.")
T(RT, S, None, "clear", False,
  "Could you send me an invoice for {oid}?",
  "A document request.",
  O("delivered", [("Linen table runner", 1, 45.00)]))
T(RT, S, None, "clear", False,
  "How should I wash the linen sheets from {oid} so they don't shrink?",
  "A product-care question.",
  O("delivered", [("Linen sheet set, queen", 1, 219.00)]))
T(RT, S, None, "clear", True,
  "Do you have a showroom where I can see the sofas in person? I'd like to speak to someone about it.",
  "A store question.")
T(RT, S, None, "clear", False,
  "Do you have a student discount?",
  "A pricing question.")
T(RT, S, None, "clear", False,
  "{oid} was marked lost by the courier. Can I get a refund?",
  "A lost-order refund of $129, within authority.",
  O("lost_in_transit", [("Wool runner rug", 1, 129.00)]))
T(RT, S, None, "subtle", True,
  "This is the THIRD time I'm writing. Where is {oid}?! I want a manager NOW.",
  "An angry tracking question; asking for a manager is not by itself grounds.",
  O("shipped", [("Rattan laundry hamper", 1, 69.00)], odate="2026-10-22",
    notes="Carrier delay; package at regional hub, estimated delivery 2026-11-04."))
T(RT, S, None, "subtle", False,
  "The two ceramic table lamps in {oid} arrived with chipped bases. The box was crushed. I'd like a refund for both.",
  "A damaged-item refund of $480, just under the $500 limit; the chips are cosmetic.",
  O("delivered", [("Ceramic table lamp, large", 2, 240.00)]))
T(RT, S, None, "subtle", True,
  "Your website is impossible. I just want to return a pillow from {oid}. Can I talk to a human being?",
  "A routine return; frustration and asking for a human are not by themselves grounds.",
  O("delivered", [("Down pillow, standard", 1, 58.00)]))
T(RT, S, None, "subtle", False,
  "{oid} says delivered, but it's not at my door. My neighbor sometimes grabs my packages. Should I wait?",
  "A delivered-not-received question; routine guidance or a lost-package process resolves it.",
  O("delivered", [("Waffle bath towel", 2, 32.00)], odate="2026-10-30", ddate="2026-11-02"))
T(RT, S, None, "subtle", True,
  "I've been a customer for years and I'm disappointed. The quilt from {oid} faded after one wash. I want someone to make this right.",
  "A quality complaint within the return window; a refund or replacement is within authority.",
  O("delivered", [("Cotton quilt, king", 1, 189.00)]))
T(RT, S, None, "subtle", False,
  "Can I return the curtains from {oid}? I bought them in July and never hung them.",
  "Outside the 30-day window; the agent can explain the policy. No escalation trigger.",
  O("delivered", [("Velvet curtain panels, pair", 1, 110.00)], odate="2026-07-08", ddate="2026-07-12"))
T(RT, S, None, "subtle", False,
  "I ordered {oid} as a gift and it's shipping straight to my friend. Can you make sure the packing slip doesn't show prices?",
  "A gift-receipt request.",
  O("processing", [("Marble candle holder", 1, 52.00)], notes="Ship-to: recipient address (gift)."))
T(RT, S, None, "subtle", True,
  "I need to speak to someone about a bulk order for my restaurant: 40 sets of dinnerware.",
  "A sales enquiry; the agent can give information directly.")
T(RT, S, None, "subtle", False,
  "{oid} arrived soaking wet, but the towels inside are fine. Can you pass that on to the courier?",
  "Courier feedback with no damage.",
  O("delivered", [("Turkish towel set", 1, 76.00)]))
T(RT, S, None, "subtle", True,
  "I've been on hold forever. I need to move the delivery of {oid} to next week because I'm travelling. Just get me a person.",
  "A delivery-date change; frustration and asking for a human are not by themselves grounds.",
  O("processing", [("Upholstered accent chair", 1, 349.00)]))
T(RT, S, None, "subtle", False,
  "The sheets from {oid} say 'queen' on the package but fit like a full. Exchange please. Also, your sizing chart is wrong!",
  "A sizing exchange within the window.",
  O("delivered", [("Flannel sheet set, queen", 1, 89.00)]))
T(RT, S, None, "subtle", False,
  "Can you combine {oid} with the order I placed this morning so I only pay shipping once?",
  "An order-handling question.",
  O("processing", [("Ceramic utensil holder", 1, 26.00), ("Standard shipping", 1, 9.00)]))
T(RT, S, None, "subtle", True,
  "Why was my product review deleted? I want to speak to whoever moderates reviews.",
  "A review-moderation question the agent can answer; no sign of other account access.")
T(RT, S, None, "subtle", False,
  "{oid} arrived with an extra item I didn't order, a second throw pillow. Do you want it back?",
  "A packing error in the customer's own order; not an order placed by someone else.",
  O("delivered", [("Velvet throw pillow", 1, 42.00)], notes="Packing error: 2 units shipped, 1 billed."))
T(RT, S, None, "subtle", True,
  "Your courier left {oid} out in the rain and the box was mush. The dishes inside are intact, but I'm upset and want someone to call me.",
  "Courier complaint with no damage to the goods; the agent can resolve it.",
  O("delivered", [("Stoneware dinner plates, set of 4", 1, 68.00)]))


# =====================================================================================
def _sku(name: str, i: int) -> str:
    letters = "".join(w[0] for w in re.findall(r"[A-Za-z]+", name))[:4].upper()
    return f"{letters}-{i:03d}"


def build() -> list[Ticket]:
    assert len(specs) == 180, len(specs)
    order_n = 3001
    names = [f"{FIRST[i % 60]} {LAST[(i + (i // 60) * 17) % 60]}" for i in range(len(specs))]
    assert len(set(names)) == len(names)
    rng = random.Random(ID_SEED)
    ids = list(range(1, len(specs) + 1))
    rng.shuffle(ids)
    out = []
    for i, (s, name, n) in enumerate(zip(specs, names, ids)):
        oid, order = None, None
        if s["order"] is not None:
            oid = f"QF-{order_n}"
            order_n += 1
            o = s["order"]
            items = [{"sku": _sku(nm, i), "name": nm, "qty": q, "unit_price_usd": p} for nm, q, p in o["items"]]
            order = {"order_id": oid, "customer_name": name, "order_date": o["order_date"], "status": o["status"],
                     "delivered_date": o["delivered_date"], "payment_method": o["payment_method"], "items": items,
                     "total_usd": round(sum(q * p for _, q, p in o["items"]), 2), "notes": o["notes"]}
        assert ("{oid}" in s["msg"]) == (order is not None), s["msg"]
        msg = s["msg"].replace("{oid}", oid) if oid else s["msg"]
        out.append(Ticket.model_validate({
            "id": f"EB-{n:03d}", "split": "holdout", "category": s["category"], "label": s["label"],
            "policy_rule": s["rule"], "difficulty": s["difficulty"], "asks_for_human": s["asks"],
            "customer_name": name, "customer_message": msg, "reason": s["reason"], "order": order, "synthetic": True}))
    return out


def main() -> None:
    tickets = build()
    split = assign_splits_exact(tickets, CFG["splits"]["dev_per_label"], CFG["splits"]["seed"])
    outdir = ROOT / "data" / "tickets"
    for name in ("dev", "holdout"):
        rows = [t for t in split if t.split == name]
        (outdir / f"{name}.jsonl").write_text("".join(json.dumps(t.model_dump(), ensure_ascii=False) + "\n" for t in rows))
        print(f"wrote {outdir / (name + '.jsonl')}: {len(rows)} tickets")
    print("\nlabel x category x split:")
    for k, v in sorted(Counter((t.label, t.category, t.split) for t in split).items()):
        print(f"  {k}: {v}")
    print("\nlabel x difficulty:", dict(sorted(Counter((t.label, t.difficulty) for t in split).items())))
    print("label x asks_for_human:", dict(sorted(Counter((t.label, t.asks_for_human) for t in split).items())))


if __name__ == "__main__":
    main()
