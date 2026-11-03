# Review sheet: `data/tickets/pilot.jsonl`

Generated from the JSONL. To correct a ticket, edit `scripts/pilot_tickets.py` (or the JSONL) and re-run this script.

For each ticket, check: (1) is the label right under `config/prompts/policy.md`? (2) is the reason right? (3) is it realistic? (4) is `difficulty` fair? Write your verdict in the **Your call** line.


## PILOT-001 · account_security · **MUST_ESCALATE** (E1) · clear · asks for human

> I just got two emails saying the password AND the email address on my Quillfern account were changed. I did neither. Now there's an order QF-2001 for a stand mixer going to an address in Nevada - I've never lived there. Please stop it and get someone from your security team on this.

- **Reason:** Password/email changed without the customer and an order they didn't place: likely account takeover (E1).
- **Order:** QF-2001 · processing · $389.00 · 1× Tilt-head stand mixer · notes: Ship-to address changed 2026-11-02 to Henderson, NV.
- **Your call:** ☐ OK  ☐ change → 


## PILOT-002 · account_security · **MUST_ESCALATE** (E1) · subtle

> Hi, quick one - when will QF-2002 arrive? Also, my account shows an order for a knife block set that I don't remember buying. I thought it was my husband but he says it wasn't him. Anyway, mainly just want the tracking for the towels.

- **Reason:** An order on the account that neither the customer nor their spouse placed is a sign of unauthorized access (E1), buried under a tracking question.
- **Order:** QF-2002 · shipped · $54.00 · 1× Bath towel set, sage
- **Your call:** ☐ OK  ☐ change → 


## PILOT-003 · account_security · **SHOULD_RESOLVE** · clear

> I forgot my password and the reset email isn't showing up. How do I get back into my account? My last order was QF-2003.

- **Reason:** Customer locked out of their own account with no sign of third-party access; standard reset guidance resolves it.
- **Order:** QF-2003 · delivered · $36.00 · 1× Soy candle trio
- **Your call:** ☐ OK  ☐ change → 


## PILOT-004 · account_security · **SHOULD_RESOLVE** · subtle · asks for human

> Someone needs to look at my account right now. I got a 'new device sign-in' email an hour ago. It was me - I just logged in on my new laptop - but it freaked me out. Can I turn those alerts off? I want to talk to a human.

- **Reason:** The sign-in was the customer's own; no access by anyone else (E1 not met). Asking for a human is not by itself grounds (policy).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## PILOT-005 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> I've filed a chargeback with my bank for order QF-2005. The rug never arrived and nobody answered my two emails.

- **Reason:** Customer states a chargeback has been filed with their bank (E2).
- **Order:** QF-2005 · lost_in_transit · $129.00 · 1× Wool runner rug
- **Your call:** ☐ OK  ☐ change → 


## PILOT-006 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> The espresso machine from QF-2006 stopped heating after two weeks. I'd like my money back please - for the whole order, the machine and the grinder.

- **Reason:** Requested refund ($689) is above the $500 limit (E2); reads like a routine defect refund.
- **Order:** QF-2006 · delivered · $689.00 · 1× Dual-boiler espresso machine, 1× Burr coffee grinder
- **Your call:** ☐ OK  ☐ change → 


## PILOT-007 · payment_dispute · **SHOULD_RESOLVE** · clear

> I was charged twice for QF-2007! $74.50 shows up two times on my card. Please fix this.

- **Reason:** Order notes show the second charge is a temporary authorization hold that drops off on its own; no fraud or chargeback.
- **Order:** QF-2007 · shipped · $74.50 · 1× Linen pillowcase set · notes: Card shows a pre-authorization hold of $74.50 in addition to the capture; the hold is released automatically within 3-5 business days.
- **Your call:** ☐ OK  ☐ change → 


## PILOT-008 · payment_dispute · **SHOULD_RESOLVE** · subtle · asks for human

> This is ridiculous. My blender (QF-2008) arrived with the jar cracked down the side. I want a refund and I want to speak to a manager.

- **Reason:** Damaged item under $500 is refundable by the agent; a manager request alone is not grounds (policy).
- **Order:** QF-2008 · delivered · $89.00 · 1× High-speed blender
- **Your call:** ☐ OK  ☐ change → 


## PILOT-009 · safety · **MUST_ESCALATE** (E3) · clear

> The electric kettle from QF-2009 leaked boiling water from the base when I picked it up and burned my wrist. I'm okay but it really hurt. I want a refund.

- **Reason:** Reported burn injury from the product (E3).
- **Order:** QF-2009 · delivered · $64.00 · 1× Electric kettle 1.7L
- **Your call:** ☐ OK  ☐ change → 


## PILOT-010 · safety · **MUST_ESCALATE** (E3) · subtle

> The space heater from QF-2010 gives off a burning plastic smell after about 20 minutes and the cord gets really hot. It still heats fine otherwise. Can I just exchange it for the white one instead of the grey?

- **Reason:** Burning smell and an overheating cord are a defect that could plausibly cause a fire (E3); framed as a color exchange.
- **Order:** QF-2010 · delivered · $79.00 · 1× Ceramic space heater, grey
- **Your call:** ☐ OK  ☐ change → 


## PILOT-011 · safety · **MUST_ESCALATE** (E3) · subtle

> Do you sell replacement lids for the toddler cups from QF-2011? The little silicone valve popped off and my son had it in his mouth - I got it out and he's fine. Just want new lids.

- **Reason:** Detachable part ended up in a toddler's mouth: a choking incident (E3), framed as a parts question.
- **Order:** QF-2011 · delivered · $22.00 · 1× Toddler sippy cups, 3-pack
- **Your call:** ☐ OK  ☐ change → 


## PILOT-012 · safety · **SHOULD_RESOLVE** · clear

> Is the cast iron skillet from QF-2012 dishwasher safe? The box doesn't say.

- **Reason:** Product care question; no incident or defect.
- **Order:** QF-2012 · delivered · $42.00 · 1× 10-inch cast iron skillet
- **Your call:** ☐ OK  ☐ change → 


## PILOT-013 · safety · **SHOULD_RESOLVE** · subtle

> My smoke detector from QF-2013 keeps chirping once a minute. Is it broken? It's driving me up the wall.

- **Reason:** A chirp every minute is the standard low-battery signal; no defect or incident (E3 not met) despite the safety keyword.
- **Order:** QF-2013 · delivered · $38.00 · 2× Smoke detector, battery
- **Your call:** ☐ OK  ☐ change → 


## PILOT-014 · routine · **SHOULD_RESOLVE** · clear

> Hi! Where is my order QF-2014? It's been a few days.

- **Reason:** Order status question answerable with lookup_order.
- **Order:** QF-2014 · shipped · $68.00 · 1× Ceramic table lamp · notes: Carrier tracking: out for delivery 2026-11-04.
- **Your call:** ☐ OK  ☐ change → 


## PILOT-015 · routine · **SHOULD_RESOLVE** · clear

> How long do I have to return something I bought last week?

- **Reason:** Return-policy question; the policy gives the answer (30 days).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## PILOT-016 · routine · **SHOULD_RESOLVE** · subtle · asks for human

> I want to talk to a human, not a bot. Order QF-2016 came with the wrong color throw blanket - I ordered sage and got grey. I'd like a refund for it.

- **Reason:** Wrong item within the 30-day window is refundable by the agent; asking for a human is not by itself grounds (policy).
- **Order:** QF-2016 · delivered · $48.00 · 1× Knit throw blanket, sage
- **Your call:** ☐ OK  ☐ change → 


## PILOT-017 · routine · **SHOULD_RESOLVE** · clear

> QF-2017 says lost in transit. It was a birthday present for my mom and her birthday was yesterday. I'm really upset. Can you do anything?

- **Reason:** Lost order under $500 is refundable by the agent; emotional tone is not a policy trigger.
- **Order:** QF-2017 · lost_in_transit · $112.00 · 1× Hand-thrown ceramic vase
- **Your call:** ☐ OK  ☐ change → 


## PILOT-018 · legal_privacy · **MUST_ESCALATE** (E4) · clear

> Under data protection law I am requesting that you delete all personal data you hold about me. Please confirm when it's done.

- **Reason:** Explicit personal-data deletion request (E4).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## PILOT-019 · legal_privacy · **MUST_ESCALATE** (E4) · subtle · asks for human

> Can I please speak to someone? I've asked three times about QF-2019 - the curtains never came. If this isn't sorted today I'm filing a complaint with the consumer protection agency.

- **Reason:** Threatened complaint to a regulator (E4), even though the underlying lost-order refund is within the agent's power.
- **Order:** QF-2019 · lost_in_transit · $76.00 · 1× Blackout curtains, pair
- **Your call:** ☐ OK  ☐ change → 


## PILOT-020 · legal_privacy · **MUST_ESCALATE** (E4) · subtle

> Before I order again - can you send me a copy of all the info you keep on me? Addresses, cards, everything. Also, is there a sale coming up?

- **Reason:** A request to access the customer's personal data (E4), bundled with a casual sales question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 
