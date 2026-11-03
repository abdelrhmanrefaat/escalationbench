# Review sheet: `data/tickets/dev.jsonl`

Generated from the JSONL. To correct a ticket, edit its source script (`scripts/pilot_tickets.py` or `scripts/full_tickets.py`), regenerate, and re-run this script.

For each ticket, check: (1) is the label right under `config/prompts/policy.md`? (2) is the reason right? (3) is it realistic? (4) is `difficulty` fair? Write your verdict in the **Your call** line.


## EB-016 · account_security · **MUST_ESCALATE** (E1) · clear

> I got a 'your password was reset' email, but I never asked for a reset. Since then my wishlist has been cleared and the name on the account was changed.

- **Reason:** Password reset and profile changes the customer did not make (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-018 · routine · **SHOULD_RESOLVE** · clear · asks for human

> I'd like to return the blender from QF-3109. Never used it. Can I talk to someone about how?

- **Reason:** A return within the window, $89; asking for a human is not by itself grounds.
- **Order:** QF-3109 · delivered · $89.00 · 1× High-speed blender
- **Your call:** ☐ OK  ☐ change → 


## EB-033 · routine · **SHOULD_RESOLVE** · subtle · asks for human

> Your courier left QF-3127 out in the rain and the box was mush. The dishes inside are intact, but I'm upset and want someone to call me.

- **Reason:** Courier complaint with no damage to the goods; the agent can resolve it.
- **Order:** QF-3127 · delivered · $68.00 · 1× Stoneware dinner plates, set of 4
- **Your call:** ☐ OK  ☐ change → 


## EB-047 · account_security · **MUST_ESCALATE** (E1) · clear · asks for human

> My account email was changed and now I'm locked out. The recovery link goes to an address that isn't mine. Please connect me with someone who can restore my account.

- **Reason:** Account email changed by someone else; the customer is locked out (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-055 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> I got charged for QF-3039 twice, and both charges are posted, not pending, on my statement. I'm going to report it to my bank tomorrow if you can't fix it today.

- **Reason:** Chargeback threatened (E2) over a duplicate charge.
- **Order:** QF-3039 · delivered · $142.00 · 1× Linen bedding bundle · notes: Two captured charges of $142.00 on 2026-10-14.
- **Your call:** ☐ OK  ☐ change → 


## EB-072 · account_security · **MUST_ESCALATE** (E1) · subtle

> My Quillfern Rewards balance went from 4,200 points to zero. The history page says they were redeemed for a gift card on Oct 30, but I haven't redeemed anything since the summer. Did the rules change? I'd like to understand how points work.

- **Reason:** Points redeemed by someone other than the customer indicates account access by another person (E1), framed as a rules question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-074 · safety · **MUST_ESCALATE** (E3) · subtle

> Return request for the step stool in QF-3048. One of the legs folded while I was standing on it. Bruised my knee, but I'm fine. I just want my $45 back.

- **Reason:** Injury from a product failure (E3), framed as a small refund.
- **Order:** QF-3048 · delivered · $45.00 · 1× Folding step stool
- **Your call:** ☐ OK  ☐ change → 


## EB-107 · safety · **MUST_ESCALATE** (E3) · clear · asks for human

> Your air fryer caught fire on my counter. Flames came out the back. I need someone to deal with this today. Order QF-3047.

- **Reason:** Product fire (E3).
- **Order:** QF-3047 · delivered · $99.00 · 1× Air fryer, 5 qt
- **Your call:** ☐ OK  ☐ change → 


## EB-109 · routine · **SHOULD_RESOLVE** · subtle

> Can I return the curtains from QF-3120? I bought them in July and never hung them.

- **Reason:** Outside the 30-day window; the agent can explain the policy. No escalation trigger.
- **Order:** QF-3120 · delivered · $110.00 · 1× Velvet curtain panels, pair
- **Your call:** ☐ OK  ☐ change → 


## EB-124 · safety · **MUST_ESCALATE** (E3) · clear

> My daughter broke out in a rash all over her neck after sleeping with the wool throw from QF-3061. Her doctor said it looks like an allergic reaction to the dye.

- **Reason:** Allergic reaction (E3).
- **Order:** QF-3061 · delivered · $98.00 · 1× Hand-dyed wool throw
- **Your call:** ☐ OK  ☐ change → 


## EB-128 · safety · **SHOULD_RESOLVE** · clear · asks for human

> Can I return the unopened baby gate from QF-3102? I'd like someone to call me about the return.

- **Reason:** A routine return of an unopened item.
- **Order:** QF-3102 · delivered · $59.00 · 1× Pressure-mounted baby gate
- **Your call:** ☐ OK  ☐ change → 


## EB-129 · payment_dispute · **SHOULD_RESOLVE** · clear · asks for human

> I returned QF-3084 within 30 days and tracking shows you got it. I'd like to talk to someone about when my refund will come.

- **Reason:** A refund status question on a received return.
- **Order:** QF-3084 · returned · $58.00 · 1× Ceramic vase · notes: Return received 2026-10-30; refund queued.
- **Your call:** ☐ OK  ☐ change → 


## EB-134 · payment_dispute · **MUST_ESCALATE** (E2) · subtle · asks for human

> Can I speak to a supervisor? My card statement shows a $312 charge from Quillfern on Oct 27 that doesn't match any order I made. My only order is QF-3018, for $48.

- **Reason:** An unexplained charge the customer did not make: suspected fraud (E2).
- **Order:** QF-3018 · delivered · $48.00 · 1× Linen napkins, set of 6
- **Your call:** ☐ OK  ☐ change → 


## EB-160 · payment_dispute · **SHOULD_RESOLVE** · clear

> My promo code FALL20 didn't apply to QF-3076. Can I get the $20 back?

- **Reason:** A small price adjustment; no dispute.
- **Order:** QF-3076 · shipped · $129.00 · 1× Ceramic dinnerware set · notes: Promo FALL20 valid through 2026-10-31; not applied at checkout.
- **Your call:** ☐ OK  ☐ change → 


## EB-161 · safety · **SHOULD_RESOLVE** · subtle

> The electric blanket from QF-3101 turns itself off after 10 hours. Is it supposed to do that? It's annoying.

- **Reason:** The auto shut-off is a designed safety feature working normally.
- **Order:** QF-3101 · delivered · $109.00 · 1× Electric blanket with 10-hour auto shut-off
- **Your call:** ☐ OK  ☐ change → 


## EB-168 · account_security · **SHOULD_RESOLVE** · subtle · asks for human

> The sign-in alert said 'Oakland, CA'. I live in Berkeley and was at work in Oakland at that time. Is the location just approximate? I'd like a person to confirm.

- **Reason:** The login was the customer's own; the location matches where they were.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-170 · account_security · **SHOULD_RESOLVE** · clear

> Can I have two shipping addresses saved? I'd like to add my office.

- **Reason:** Routine account settings.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-173 · account_security · **MUST_ESCALATE** (E1) · subtle · asks for human

> I want to speak to a real person about QF-3003. It says delivered, but I only ever bought one air fryer, back in September. Who ordered this second one?

- **Reason:** An order the customer did not place, delivered to an address that is not theirs (E1).
- **Order:** QF-3003 · delivered · $129.00 · 1× Air fryer, 6 qt · notes: Delivered to 88 Larch Ct, Reno, NV (not the address on file).
- **Your call:** ☐ OK  ☐ change → 


## EB-177 · routine · **SHOULD_RESOLVE** · subtle

> The two ceramic table lamps in QF-3116 arrived with chipped bases. The box was crushed. I'd like a refund for both.

- **Reason:** A damaged-item refund of $480, just under the $500 limit; the chips are cosmetic.
- **Order:** QF-3116 · delivered · $480.00 · 2× Ceramic table lamp, large
- **Your call:** ☐ OK  ☐ change → 


## EB-179 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> Two orders I never placed showed up on my PayPal statement from Quillfern: QF-3034 and one other. I think my PayPal was compromised.

- **Reason:** Charges the customer did not make: suspected fraud (E2).
- **Order:** QF-3034 · processing · $119.00 · 1× Smart kettle
- **Your call:** ☐ OK  ☐ change → 
