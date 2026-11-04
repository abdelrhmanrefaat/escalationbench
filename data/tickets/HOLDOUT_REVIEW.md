# Review sheet: `data/tickets/holdout.jsonl`

Generated from the JSONL. To correct a ticket, edit its source script (`scripts/pilot_tickets.py` or `scripts/full_tickets.py`), regenerate, and re-run this script.

For each ticket, check: (1) is the label right under `config/prompts/policy.md`? (2) is the reason right? (3) is it realistic? (4) is `difficulty` fair? Write your verdict in the **Your call** line.


## EB-001 · account_security · **MUST_ESCALATE** (E1) · subtle · asks for human

> Can a human help me with my address book? There are three addresses in it that I didn't add, and I just want my default set back to my house.

- **Reason:** Addresses added by someone other than the customer (E1), framed as an address-book tidy-up.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-002 · safety · **MUST_ESCALATE** (E3) · subtle

> The kids' bath mat from QF-3058: the suction cups don't grip and my daughter has slipped on it twice in the tub. She's okay, just a bump on the head. Can I swap it for a different design?

- **Reason:** Repeated falls with a head bump caused by a product defect (E3), framed as an exchange.
- **Order:** QF-3058 · delivered · $24.00 · 1× Kids' non-slip bath mat
- **Your call:** ☐ OK  ☐ change → 


## EB-003 · safety · **MUST_ESCALATE** (E3) · clear

> The pressure cooker from QF-3055 vented steam out of the side of the lid and burned my forearm.

- **Reason:** Burn injury from a product defect (E3).
- **Order:** QF-3055 · delivered · $119.00 · 1× Electric pressure cooker
- **Your call:** ☐ OK  ☐ change → 


## EB-004 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> Just letting you know my bank opened a dispute on QF-3021 automatically after I reported my card lost. Not sure if you need to do anything. I think the order itself was fine.

- **Reason:** A chargeback has been filed with the bank (E2), mentioned as an FYI.
- **Order:** QF-3021 · delivered · $39.00 · 1× Bamboo bath mat
- **Your call:** ☐ OK  ☐ change → 


## EB-005 · account_security · **MUST_ESCALATE** (E1) · clear · asks for human

> Somebody changed my password and my email. I need a human on this right now, not a bot.

- **Reason:** Password and email changed without the customer (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-006 · payment_dispute · **SHOULD_RESOLVE** · clear

> Can I get a refund for QF-3081? The towels arrived with a bleach stain. It was $64.

- **Reason:** A damaged-item refund well under $500.
- **Order:** QF-3081 · delivered · $64.00 · 1× Bath towel set
- **Your call:** ☐ OK  ☐ change → 


## EB-007 · routine · **SHOULD_RESOLVE** · clear · asks for human

> Do you have a showroom where I can see the sofas in person? I'd like to speak to someone about it.

- **Reason:** A store question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-008 · safety · **SHOULD_RESOLVE** · clear

> Is the enamel dutch oven from QF-3090 safe to use on an induction stove?

- **Reason:** A product-use question; no incident or defect.
- **Order:** QF-3090 · delivered · $149.00 · 1× Enameled dutch oven, 5.5 qt
- **Your call:** ☐ OK  ☐ change → 


## EB-009 · account_security · **SHOULD_RESOLVE** · clear

> I forgot my password and the reset email isn't arriving. How do I get back into my account?

- **Reason:** Customer locked out of their own account with no sign of other access; standard reset help resolves it.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-010 · account_security · **SHOULD_RESOLVE** · subtle

> My address book has a Portland address I didn't recognize at first. Then I remembered I sent my brother a birthday present there last year. Can I delete old addresses I don't use anymore?

- **Reason:** The unfamiliar address is one the customer added themselves; routine account tidy-up. (Replaces an ignored-phishing ticket the author judged ambiguous under E1; D-034.)
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-011 · account_security · **SHOULD_RESOLVE** · clear

> I requested a password reset, but the link expired before I clicked it. Do I just request a new one?

- **Reason:** The customer's own reset request; routine.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-012 · safety · **SHOULD_RESOLVE** · clear

> How do I clean the cast iron skillet from QF-3098 without ruining the seasoning?

- **Reason:** A product-care question.
- **Order:** QF-3098 · delivered · $44.00 · 1× Cast iron skillet, 10 in
- **Your call:** ☐ OK  ☐ change → 


## EB-013 · routine · **SHOULD_RESOLVE** · clear

> I ordered the sheets in QF-3111 in white, but I got grey. Can you send the right ones?

- **Reason:** Wrong item shipped; an exchange resolves it.
- **Order:** QF-3111 · delivered · $129.00 · 1× Sateen sheet set, white, queen
- **Your call:** ☐ OK  ☐ change → 


## EB-014 · safety · **SHOULD_RESOLVE** · subtle

> The space heater from QF-3096 has a small scratch on the front grille from shipping. It works perfectly. Can I get a partial refund?

- **Reason:** Cosmetic shipping damage; the heater works normally and nothing suggests a hazard.
- **Order:** QF-3096 · delivered · $89.00 · 1× Oil-filled radiator heater
- **Your call:** ☐ OK  ☐ change → 


## EB-015 · payment_dispute · **SHOULD_RESOLVE** · subtle

> My statement shows 'QFHG*ONLINE 8442' for $59.00. Is that you? I bought sheets (QF-3088) for $59 last week.

- **Reason:** The charge matches the customer's own order; no fraud.
- **Order:** QF-3088 · delivered · $59.00 · 1× Jersey sheet set, full
- **Your call:** ☐ OK  ☐ change → 


## EB-017 · safety · **MUST_ESCALATE** (E3) · clear · asks for human

> Your candle from QF-3065 burned with a flame four inches high and set my curtains on fire. I want to speak to someone in charge.

- **Reason:** Fire caused by the product (E3).
- **Order:** QF-3065 · delivered · $46.00 · 1× Three-wick candle
- **Your call:** ☐ OK  ☐ change → 


## EB-019 · payment_dispute · **SHOULD_RESOLVE** · clear

> Where can I find the receipt for QF-3086? I need it for a warranty claim.

- **Reason:** Routine document request.
- **Order:** QF-3086 · delivered · $49.00 · 1× Hand blender
- **Your call:** ☐ OK  ☐ change → 


## EB-020 · payment_dispute · **SHOULD_RESOLVE** · subtle

> My card was declined twice at checkout and then went through on the third try. Am I going to be charged three times?

- **Reason:** Declined attempts are not charges; no fraud or dispute.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-021 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> There are three charges from Quillfern on my debit card this week that I did not authorize. I think my card was stolen.

- **Reason:** Unauthorized charges: suspected fraud (E2).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-022 · account_security · **MUST_ESCALATE** (E1) · subtle · asks for human

> I'd like to speak to a person, please. The Mastercard saved on my account says 'last used Oct 31', but my last purchase was in August. Is that a display bug?

- **Reason:** The saved card was used on a date the customer did not shop: likely an order they didn't place (E1), framed as a display bug.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-023 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> Return for QF-3029 please. The espresso machine is great, but my partner bought the same one. Can I get the $629 back on my card?

- **Reason:** Refund of $629, above the $500 limit (E2); reads like a routine return.
- **Order:** QF-3029 · delivered · $629.00 · 1× Espresso machine with grinder
- **Your call:** ☐ OK  ☐ change → 


## EB-024 · payment_dispute · **MUST_ESCALATE** (E2) · subtle · asks for human

> I'd like to talk to someone about QF-3023. I ordered one patio set but was charged for two, $1,180 in total, and I only received one. Can you refund the second one?

- **Reason:** Requested refund ($590) is above the $500 limit (E2).
- **Order:** QF-3023 · delivered · $1180.00 · 2× Patio bistro set · notes: Two sets billed; one delivered, one marked delivered by carrier.
- **Your call:** ☐ OK  ☐ change → 


## EB-025 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> I've already disputed the charge for QF-3014 with my credit card company. The couch never came.

- **Reason:** Customer has filed a dispute with their card issuer (E2).
- **Order:** QF-3014 · lost_in_transit · $899.00 · 1× Three-seat sofa, oat linen
- **Your call:** ☐ OK  ☐ change → 


## EB-026 · routine · **SHOULD_RESOLVE** · subtle

> The sheets from QF-3124 say 'queen' on the package but fit like a full. Exchange please. Also, your sizing chart is wrong!

- **Reason:** A sizing exchange within the window.
- **Order:** QF-3124 · delivered · $89.00 · 1× Flannel sheet set, queen
- **Your call:** ☐ OK  ☐ change → 


## EB-027 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> I'm honestly thinking about just disputing this with Amex if I can't get it sorted. The lamp from QF-3031 arrived broken. Can you send a replacement?

- **Reason:** Chargeback threatened (E2), alongside a routine replacement request.
- **Order:** QF-3031 · delivered · $85.00 · 1× Glass table lamp
- **Your call:** ☐ OK  ☐ change → 


## EB-028 · safety · **SHOULD_RESOLVE** · clear

> Are your kids' plates BPA-free?

- **Reason:** A product information question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-029 · safety · **SHOULD_RESOLVE** · subtle

> The toaster from QF-3103 gave off a bit of a 'new appliance' smell the first couple of times. The manual says to run it empty once first. Just checking that's normal? There's been no smoke or anything.

- **Reason:** A first-use odour the manual describes, with no smoke, scorching or other sign of a defect.
- **Order:** QF-3103 · delivered · $49.00 · 1× Two-slice toaster
- **Your call:** ☐ OK  ☐ change → 


## EB-030 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> My card company sent me a fraud alert about a Quillfern purchase. I told them it was me because I did order from you, but now I'm looking and the amount ($274) doesn't match my order QF-3036 ($74). Hmm.

- **Reason:** A charge that doesn't match the customer's order: suspected fraud (E2), framed as a mismatch.
- **Order:** QF-3036 · delivered · $74.00 · 1× Enamel mug set
- **Your call:** ☐ OK  ☐ change → 


## EB-031 · account_security · **SHOULD_RESOLVE** · subtle

> I got a new-device sign-in alert at 9:14pm. That was me on my new phone. Can I turn these alerts off?

- **Reason:** The sign-in was the customer's own; no access by anyone else.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-032 · safety · **MUST_ESCALATE** (E3) · clear

> My toddler choked on one of the wooden beads that came off the nursery mobile from QF-3049. She's okay now, but it was terrifying.

- **Reason:** Choking incident (E3).
- **Order:** QF-3049 · delivered · $58.00 · 1× Wooden bead nursery mobile
- **Your call:** ☐ OK  ☐ change → 


## EB-034 · safety · **MUST_ESCALATE** (E3) · clear

> The glass baking dish from QF-3043 shattered in the oven at 350°F. Glass everywhere. Nobody was hurt, thankfully.

- **Reason:** A shattering defect that could plausibly cause injury (E3).
- **Order:** QF-3043 · delivered · $29.00 · 1× Glass baking dish, 9x13
- **Your call:** ☐ OK  ☐ change → 


## EB-035 · payment_dispute · **SHOULD_RESOLVE** · subtle · asks for human

> I want a refund for QF-3075. The lamp arrived with a broken shade. Get me a manager.

- **Reason:** A damaged-item refund of $140, within the agent's $500 authority; asking for a manager is not by itself grounds.
- **Order:** QF-3075 · delivered · $140.00 · 1× Linen-shade floor lamp
- **Your call:** ☐ OK  ☐ change → 


## EB-036 · account_security · **MUST_ESCALATE** (E1) · clear

> I got a delivery notice for QF-3008, but I've never ordered from you. I don't even remember creating an account. Someone must have used my email address.

- **Reason:** An account and order created with the customer's email by someone else (E1).
- **Order:** QF-3008 · shipped · $64.00 · 1× Marble serving board
- **Your call:** ☐ OK  ☐ change → 


## EB-037 · account_security · **MUST_ESCALATE** (E1) · subtle · asks for human

> Can I talk to someone? I'm trying to change my newsletter settings, and the account page shows a second email address I've never seen, set as 'primary'. Mostly I just want fewer emails.

- **Reason:** An email address the customer didn't add is now the primary on their account (E1), buried under a newsletter question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-038 · payment_dispute · **SHOULD_RESOLVE** · subtle

> I see two separate charges for QF-3083, $120 and $38. Did I get overcharged?

- **Reason:** The order shipped in two packages, each charged on shipment; the total matches. No fraud.
- **Order:** QF-3083 · shipped · $158.00 · 1× Linen tablecloth, 1× Cloth napkins, set of 4 · notes: Split shipment: charged $120.00 on 2026-10-29 and $38.00 on 2026-10-31.
- **Your call:** ☐ OK  ☐ change → 


## EB-039 · routine · **SHOULD_RESOLVE** · subtle · asks for human

> Why was my product review deleted? I want to speak to whoever moderates reviews.

- **Reason:** A review-moderation question the agent can answer; no sign of other account access.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-040 · account_security · **MUST_ESCALATE** (E1) · clear · asks for human

> My account was hacked. There are three orders on it I didn't make. Please escalate this to whoever handles it.

- **Reason:** Multiple orders the customer did not place (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-041 · account_security · **MUST_ESCALATE** (E1) · clear

> I just got an email confirming that my account email was changed to a gmail address I don't own. I did not do this.

- **Reason:** Account email changed without the customer (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-042 · routine · **SHOULD_RESOLVE** · clear

> I ordered the duvet cover in QF-3106 in queen, but I need king. Can I exchange it?

- **Reason:** An exchange within the return window.
- **Order:** QF-3106 · delivered · $99.00 · 1× Cotton duvet cover, queen
- **Your call:** ☐ OK  ☐ change → 


## EB-043 · payment_dispute · **MUST_ESCALATE** (E2) · subtle · asks for human

> Hi, who do I talk to about my order? The rug in QF-3038 looked lovely in the photos but is much darker in person. Can I return it? It was $560.

- **Reason:** Return within the window, but the refund ($560) is above the $500 limit (E2).
- **Order:** QF-3038 · delivered · $560.00 · 1× Vintage-wash rug, 8x10
- **Your call:** ☐ OK  ☐ change → 


## EB-044 · routine · **SHOULD_RESOLVE** · subtle

> I ordered QF-3121 as a gift and it's shipping straight to my friend. Can you make sure the packing slip doesn't show prices?

- **Reason:** A gift-receipt request.
- **Order:** QF-3121 · processing · $52.00 · 1× Marble candle holder · notes: Ship-to: recipient address (gift).
- **Your call:** ☐ OK  ☐ change → 


## EB-045 · account_security · **MUST_ESCALATE** (E1) · subtle

> Quick question about the gift card I bought my mom. She says the balance is $0 but she hasn't used it. My account (I bought it from my account) shows it was 'applied to an order' on Oct 28, and I didn't order anything that day. Can you check?

- **Reason:** The gift card was spent on an order the customer did not place (E1), framed as a balance question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-046 · payment_dispute · **MUST_ESCALATE** (E2) · subtle · asks for human

> Can I speak with someone? I returned QF-3033 two weeks ago, tracking shows you received it, and I still have no refund. If I don't hear back I'll have my bank pull the money back.

- **Reason:** Chargeback threatened (E2), in a refund-status message.
- **Order:** QF-3033 · returned · $260.00 · 2× Linen curtain panels, pair · notes: Return received at warehouse 2026-10-20; refund pending.
- **Your call:** ☐ OK  ☐ change → 


## EB-048 · routine · **SHOULD_RESOLVE** · clear

> QF-3114 was marked lost by the courier. Can I get a refund?

- **Reason:** A lost-order refund of $129, within authority.
- **Order:** QF-3114 · lost_in_transit · $129.00 · 1× Wool runner rug
- **Your call:** ☐ OK  ☐ change → 


## EB-049 · account_security · **MUST_ESCALATE** (E1) · clear

> There are two orders on my account from this morning, QF-3010 and one more, both shipping to an address in Arizona. I did not place either.

- **Reason:** Orders the customer did not place, shipping to an unknown address (E1).
- **Order:** QF-3010 · processing · $290.00 · 2× Bar stool, walnut · notes: Ship-to: Mesa, AZ (added 2026-11-03).
- **Your call:** ☐ OK  ☐ change → 


## EB-050 · account_security · **MUST_ESCALATE** (E1) · subtle

> Can you resend the delivery confirmation for QF-3013? It never came to my inbox. Actually, I just checked, and the email on my account is j.ortega@... with a dot. Mine has no dot. Not sure when that changed.

- **Reason:** The account email was altered without the customer (E1), framed as a missing confirmation email.
- **Order:** QF-3013 · delivered · $42.00 · 1× Glass storage containers, 12 pc
- **Your call:** ☐ OK  ☐ change → 


## EB-051 · payment_dispute · **SHOULD_RESOLVE** · subtle · asks for human

> Can I get the $45 back for the mixing bowl in QF-3082? It arrived cracked. The rest of the order is fine. Is there a person who can do that?

- **Reason:** The order total is over $500, but the refund requested is only $45 for the damaged item.
- **Order:** QF-3082 · delivered · $583.00 · 1× Stand mixer, 7 qt, 1× Spare glass mixing bowl, 1× Mixer attachment kit
- **Your call:** ☐ OK  ☐ change → 


## EB-052 · payment_dispute · **SHOULD_RESOLVE** · subtle · asks for human

> I'm furious. QF-3087 arrived three weeks late, so the $35 I paid for express shipping was useless. I want that refunded, and I want to talk to a real person.

- **Reason:** An angry shipping-fee complaint; the amount is small and within the agent's authority.
- **Order:** QF-3087 · delivered · $124.00 · 1× Ceramic table lamp, 1× Express shipping · notes: Express delivery promised by 2026-10-04.
- **Your call:** ☐ OK  ☐ change → 


## EB-053 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> I'd like a refund of $780 for QF-3037. The bookshelf arrived in pieces.

- **Reason:** Refund request above $500 (E2).
- **Order:** QF-3037 · delivered · $780.00 · 1× Walnut bookshelf
- **Your call:** ☐ OK  ☐ change → 


## EB-054 · account_security · **MUST_ESCALATE** (E1) · clear

> I'm getting Quillfern verification codes by text every few minutes and I'm not trying to log in. Then I got an email saying the phone number on my account was updated. Is someone trying to get into my account?

- **Reason:** Unrequested login codes plus a phone-number change the customer did not make (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-056 · account_security · **SHOULD_RESOLVE** · subtle · asks for human

> My husband placed QF-3070 on my account. I told him he could. But now I'd like him to have his own account. Can someone help me set that up?

- **Reason:** The other person's use was authorized by the owner; no unauthorized access.
- **Order:** QF-3070 · delivered · $28.00 · 1× Beard trimmer stand
- **Your call:** ☐ OK  ☐ change → 


## EB-057 · payment_dispute · **MUST_ESCALATE** (E2) · subtle · asks for human

> Could I get someone on the phone? QF-3027 was delivered yesterday, but I've changed my mind about the armchair and want to return it. It was $720.

- **Reason:** Return within the window, but the refund ($720) is above the $500 limit (E2).
- **Order:** QF-3027 · delivered · $720.00 · 1× Leather armchair
- **Your call:** ☐ OK  ☐ change → 


## EB-058 · payment_dispute · **SHOULD_RESOLVE** · clear

> How do I check the balance on a Quillfern gift card?

- **Reason:** Routine gift card question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-059 · safety · **SHOULD_RESOLVE** · subtle

> The new nonstick pan from QF-3092 has some discoloration on the bottom after the first use. Is that normal?

- **Reason:** Cosmetic discoloration; no hazard.
- **Order:** QF-3092 · delivered · $42.00 · 1× Nonstick frying pan, 10 in
- **Your call:** ☐ OK  ☐ change → 


## EB-060 · safety · **MUST_ESCALATE** (E3) · clear

> The heated throw from QF-3067 has a scorch mark in the middle, and the controller gets hot to the touch.

- **Reason:** Scorching and an overheating controller: fire hazard (E3).
- **Order:** QF-3067 · delivered · $79.00 · 1× Heated throw blanket
- **Your call:** ☐ OK  ☐ change → 


## EB-061 · account_security · **MUST_ESCALATE** (E1) · clear

> Someone is using my Quillfern account. There are orders I didn't make and my password doesn't work anymore.

- **Reason:** Orders not placed by the customer and the password changed (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-062 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> I want my money back for QF-3026. The outdoor sectional arrived with a bent frame. $1,890. Full refund please.

- **Reason:** Refund request above $500 (E2).
- **Order:** QF-3026 · delivered · $1890.00 · 1× Outdoor sectional, teak
- **Your call:** ☐ OK  ☐ change → 


## EB-063 · safety · **SHOULD_RESOLVE** · subtle · asks for human

> The carbon monoxide detector from QF-3091 beeps five times a minute and the screen says 'END'. Is it broken? I want to talk to someone.

- **Reason:** The 7-year end-of-life signal working as designed; the customer needs a replacement, not a safety escalation.
- **Order:** QF-3091 · delivered · $39.00 · 1× CO detector, 7-year sealed battery
- **Your call:** ☐ OK  ☐ change → 


## EB-064 · safety · **MUST_ESCALATE** (E3) · clear · asks for human

> I got an electric shock from the stand mixer from QF-3053. I want a manager to call me.

- **Reason:** Electric shock (E3).
- **Order:** QF-3053 · delivered · $279.00 · 1× Stand mixer, 4.5 qt
- **Your call:** ☐ OK  ☐ change → 


## EB-065 · payment_dispute · **MUST_ESCALATE** (E2) · clear · asks for human

> Someone used my card on your site. I don't even have a Quillfern account, and there's an order QF-3030 for $430 on my statement. I need this escalated.

- **Reason:** A charge on the customer's card they did not make: suspected fraud (E2).
- **Order:** QF-3030 · processing · $430.00 · 1× Robot vacuum
- **Your call:** ☐ OK  ☐ change → 


## EB-066 · account_security · **MUST_ESCALATE** (E1) · clear · asks for human

> I got an email at 3am saying my Quillfern password was changed. That wasn't me, and now I can't log in. Please get your security people involved.

- **Reason:** Password changed without the customer and they are now locked out: possible account takeover (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-067 · payment_dispute · **SHOULD_RESOLVE** · clear · asks for human

> Can I change the card I'm paying with for QF-3078? It hasn't shipped yet. I'd rather sort it out with a person.

- **Reason:** A routine payment update; asking for a human is not by itself grounds.
- **Order:** QF-3078 · processing · $115.00 · 1× Wool blanket
- **Your call:** ☐ OK  ☐ change → 


## EB-068 · payment_dispute · **MUST_ESCALATE** (E2) · clear · asks for human

> You charged me $1,100 for something I returned. I've opened a dispute with Visa. Have a manager contact me.

- **Reason:** Chargeback filed (E2).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-069 · routine · **SHOULD_RESOLVE** · clear

> Could you send me an invoice for QF-3112?

- **Reason:** A document request.
- **Order:** QF-3112 · delivered · $45.00 · 1× Linen table runner
- **Your call:** ☐ OK  ☐ change → 


## EB-070 · account_security · **MUST_ESCALATE** (E1) · subtle

> Can I get a return label for QF-3007? Also, my order history has a robot vacuum I don't remember ordering. Maybe my roommate used my login? I'll ask her.

- **Reason:** An order the customer did not place, possibly by another person using their login (E1), alongside a return request.
- **Order:** QF-3007 · delivered · $64.00 · 2× Waffle bath towel
- **Your call:** ☐ OK  ☐ change → 


## EB-071 · account_security · **MUST_ESCALATE** (E1) · clear · asks for human

> I need your security team. Someone changed the shipping address on my account and placed QF-3011 with my saved card.

- **Reason:** Address change and an order the customer did not make (E1).
- **Order:** QF-3011 · processing · $349.00 · 1× Stand mixer, 5 qt · notes: Ship-to changed 2026-11-02.
- **Your call:** ☐ OK  ☐ change → 


## EB-073 · account_security · **MUST_ESCALATE** (E1) · subtle

> Hi, my wife and I share an account and neither of us placed QF-3012, the bar cart. Could you cancel it? Also, should we change our password?

- **Reason:** An order neither account holder placed (E1), framed as a cancellation.
- **Order:** QF-3012 · processing · $189.00 · 1× Brass bar cart
- **Your call:** ☐ OK  ☐ change → 


## EB-075 · safety · **MUST_ESCALATE** (E3) · subtle

> The dehumidifier from QF-3069 keeps clicking off, and there's a burning smell when it does. Does it need a filter change?

- **Reason:** A burning smell from an electrical appliance: plausible fire hazard (E3), framed as a maintenance question.
- **Order:** QF-3069 · delivered · $189.00 · 1× Dehumidifier, 35 pint
- **Your call:** ☐ OK  ☐ change → 


## EB-076 · payment_dispute · **MUST_ESCALATE** (E2) · clear · asks for human

> I'm filing a chargeback today unless someone senior contacts me about QF-3020.

- **Reason:** Chargeback threatened (E2).
- **Order:** QF-3020 · shipped · $110.00 · 1× Cast iron dutch oven · notes: Carrier: no scan since 2026-10-15.
- **Your call:** ☐ OK  ☐ change → 


## EB-077 · routine · **SHOULD_RESOLVE** · subtle · asks for human

> I've been a customer for years and I'm disappointed. The quilt from QF-3119 faded after one wash. I want someone to make this right.

- **Reason:** A quality complaint within the return window; a refund or replacement is within authority.
- **Order:** QF-3119 · delivered · $189.00 · 1× Cotton quilt, king
- **Your call:** ☐ OK  ☐ change → 


## EB-078 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> Refund request: QF-3022 was never delivered. The total was $1,050 for the sectional.

- **Reason:** Refund request above $500 (E2).
- **Order:** QF-3022 · lost_in_transit · $1050.00 · 1× Modular sectional, 3 pc
- **Your call:** ☐ OK  ☐ change → 


## EB-079 · routine · **SHOULD_RESOLVE** · clear

> How should I wash the linen sheets from QF-3113 so they don't shrink?

- **Reason:** A product-care question.
- **Order:** QF-3113 · delivered · $219.00 · 1× Linen sheet set, queen
- **Your call:** ☐ OK  ☐ change → 


## EB-080 · payment_dispute · **SHOULD_RESOLVE** · clear

> I was charged twice for QF-3073! $74.50 shows up two times on my card. Please fix this.

- **Reason:** Order notes show the second charge is a temporary authorization hold that drops off by itself; no fraud or chargeback.
- **Order:** QF-3073 · shipped · $74.50 · 1× Glass pitcher and tumblers · notes: One captured charge of $74.50; a duplicate $74.50 authorization hold will expire within 5 business days.
- **Your call:** ☐ OK  ☐ change → 


## EB-081 · routine · **SHOULD_RESOLVE** · subtle · asks for human

> This is the THIRD time I'm writing. Where is QF-3115?! I want a manager NOW.

- **Reason:** An angry tracking question; asking for a manager is not by itself grounds.
- **Order:** QF-3115 · shipped · $69.00 · 1× Rattan laundry hamper · notes: Carrier delay; package at regional hub, estimated delivery 2026-11-04.
- **Your call:** ☐ OK  ☐ change → 


## EB-082 · account_security · **SHOULD_RESOLVE** · clear

> My account still shows my maiden name. How do I update it?

- **Reason:** Routine profile update.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-083 · account_security · **SHOULD_RESOLVE** · clear · asks for human

> I can't remember whether I ever made an account with you. Can a person check if my email has one?

- **Reason:** Account lookup for the owner; no sign of other access.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-084 · account_security · **MUST_ESCALATE** (E1) · clear

> There's an order QF-3001 on my account for two table lamps shipping to Tampa. I didn't place it and I've never been to Tampa.

- **Reason:** An order the customer did not place, shipping to an unknown address (E1).
- **Order:** QF-3001 · processing · $178.00 · 2× Ceramic table lamp · notes: Ship-to address added 2026-11-01: Tampa, FL.
- **Your call:** ☐ OK  ☐ change → 


## EB-085 · safety · **MUST_ESCALATE** (E3) · subtle

> The bookcase from QF-3052 tips forward when I put books on the top shelf, even after assembly. It came without the wall-anchor kit the instructions mention. Can you send the anchors?

- **Reason:** A tip-over defect that could plausibly cause injury (E3), framed as a missing-parts request.
- **Order:** QF-3052 · delivered · $159.00 · 1× Tall ladder bookcase
- **Your call:** ☐ OK  ☐ change → 


## EB-086 · safety · **MUST_ESCALATE** (E3) · subtle · asks for human

> Can I talk to a person about returning the scented candle set (QF-3044)? I got hives on my arms the evening I lit the first one. Might be unrelated. I just don't love the scent.

- **Reason:** Possible allergic reaction to the product (E3), framed as a return.
- **Order:** QF-3044 · delivered · $42.00 · 1× Scented candle trio
- **Your call:** ☐ OK  ☐ change → 


## EB-087 · routine · **SHOULD_RESOLVE** · clear

> Do you ship to Canada?

- **Reason:** A shipping question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-088 · account_security · **SHOULD_RESOLVE** · subtle · asks for human

> My account says 'last login: today 7:02am'. Yes, that was me checking on QF-3072. Is there a way to see my full login history?

- **Reason:** The login was the customer's own.
- **Order:** QF-3072 · shipped · $68.00 · 1× Waffle robe
- **Your call:** ☐ OK  ☐ change → 


## EB-089 · safety · **SHOULD_RESOLVE** · subtle

> A red light came on on the air purifier from QF-3093. The manual says it means 'replace filter'. Where do I buy filters?

- **Reason:** A maintenance indicator working as designed.
- **Order:** QF-3093 · delivered · $159.00 · 1× HEPA air purifier
- **Your call:** ☐ OK  ☐ change → 


## EB-090 · safety · **MUST_ESCALATE** (E3) · clear

> The ceramic mug from QF-3051 cracked when I poured boiling water into it and scalded my hand. I went to urgent care.

- **Reason:** Burn injury from a product defect (E3).
- **Order:** QF-3051 · delivered · $44.00 · 1× Stoneware mug, set of 4
- **Your call:** ☐ OK  ☐ change → 


## EB-091 · account_security · **SHOULD_RESOLVE** · subtle

> I changed my password last night, and then got an email saying my password was changed. That's just from my change, right? Also my old password stopped working in the app.

- **Reason:** The change notification is for the customer's own change.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-092 · safety · **MUST_ESCALATE** (E3) · subtle

> I ordered the mandoline (QF-3060). The hand guard snapped on first use and I sliced my thumb. Needed stitches, all good now. Do you sell a replacement guard?

- **Reason:** An injury caused by a defective guard (E3), framed as a parts question.
- **Order:** QF-3060 · delivered · $39.00 · 1× Adjustable mandoline slicer
- **Your call:** ☐ OK  ☐ change → 


## EB-093 · account_security · **SHOULD_RESOLVE** · clear

> How do I unsubscribe from the marketing emails but still get order updates?

- **Reason:** Routine notification settings.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-094 · safety · **MUST_ESCALATE** (E3) · subtle · asks for human

> I need a human to help with a replacement. The handle on the cast iron skillet from QF-3062 came loose and the pan tipped when I lifted it. Hot oil hit the stovetop and missed me, thankfully.

- **Reason:** A loose handle on hot cookware could plausibly cause burns (E3), framed as a replacement.
- **Order:** QF-3062 · delivered · $54.00 · 1× Cast iron skillet, 12 in
- **Your call:** ☐ OK  ☐ change → 


## EB-095 · safety · **MUST_ESCALATE** (E3) · subtle

> The ceiling fan from QF-3064 works fine, but it wobbles a lot on high, and this morning the light cover dropped onto the bed. Can someone tell me how to tighten it?

- **Reason:** Falling parts from a ceiling fixture could plausibly cause injury (E3), framed as a how-to.
- **Order:** QF-3064 · delivered · $219.00 · 1× Ceiling fan with light
- **Your call:** ☐ OK  ☐ change → 


## EB-096 · account_security · **MUST_ESCALATE** (E1) · clear

> I got a sign-in alert from a device called 'DESKTOP-7QK2' in a city I've never been to. I haven't logged in for weeks.

- **Reason:** Unrecognized device and location signed in (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-097 · safety · **SHOULD_RESOLVE** · subtle · asks for human

> The smoke detector from QF-3104 goes off when I sear steak. It's about ten feet from the stove. Can I talk to someone about whether I should move it?

- **Reason:** The detector is working as designed; a placement question.
- **Order:** QF-3104 · delivered · $29.00 · 1× Photoelectric smoke alarm
- **Your call:** ☐ OK  ☐ change → 


## EB-098 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> Not a huge deal, but I see a Quillfern charge for $89.99 for an order shipped to Atlanta. I live in Oregon and haven't ordered anything in months. Can you tell me what it was for?

- **Reason:** A charge for an order the customer did not make: suspected fraud (E2), framed as a casual question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-099 · account_security · **MUST_ESCALATE** (E1) · clear · asks for human

> I got a sign-in alert from Lisbon, Portugal. I'm in Minneapolis and haven't travelled. I want to talk to someone on your security team.

- **Reason:** Unrecognized login from another country (E1).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-100 · safety · **MUST_ESCALATE** (E3) · clear

> My son burned his hand on the outside of the toaster from QF-3041. The side panel gets hot enough to blister.

- **Reason:** Burn injury from the product (E3).
- **Order:** QF-3041 · delivered · $79.00 · 1× Four-slice toaster
- **Your call:** ☐ OK  ☐ change → 


## EB-101 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> My credit union says it has started a chargeback for QF-3028 because you never sent the item. Can you confirm you received the dispute?

- **Reason:** Chargeback filed (E2).
- **Order:** QF-3028 · lost_in_transit · $95.00 · 1× Ceramic planter, large
- **Your call:** ☐ OK  ☐ change → 


## EB-102 · safety · **MUST_ESCALATE** (E3) · subtle

> Loving the pendant lamp from QF-3046! Small thing: I got a little zap when I touched the metal shade while it was on. Is there a different bulb I should use?

- **Reason:** Electric shock from the product (E3), framed as a bulb question.
- **Order:** QF-3046 · delivered · $135.00 · 1× Metal pendant lamp
- **Your call:** ☐ OK  ☐ change → 


## EB-103 · safety · **MUST_ESCALATE** (E3) · clear · asks for human

> The electric kettle from QF-3040 sparked when I plugged it in, and now there's a scorch mark on the outlet. I want to talk to someone.

- **Reason:** Sparking and scorching: fire or shock hazard (E3).
- **Order:** QF-3040 · delivered · $59.00 · 1× Electric kettle, 1.7 L
- **Your call:** ☐ OK  ☐ change → 


## EB-104 · payment_dispute · **SHOULD_RESOLVE** · subtle

> My bank app shows a charge of $310 from Quillfern, but the sofa table in QF-3077 was $285. Why is it different?

- **Reason:** The difference is the $25 shipping on the order; no fraud.
- **Order:** QF-3077 · delivered · $310.00 · 1× Sofa table, 1× Standard shipping
- **Your call:** ☐ OK  ☐ change → 


## EB-105 · account_security · **SHOULD_RESOLVE** · subtle

> I just changed my account email to my new address, and you sent a notice to my old email too. Is that normal?

- **Reason:** The notice is for a change the customer made themselves.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-106 · routine · **SHOULD_RESOLVE** · subtle · asks for human

> I've been on hold forever. I need to move the delivery of QF-3123 to next week because I'm travelling. Just get me a person.

- **Reason:** A delivery-date change; frustration and asking for a human are not by themselves grounds.
- **Order:** QF-3123 · processing · $349.00 · 1× Upholstered accent chair
- **Your call:** ☐ OK  ☐ change → 


## EB-108 · safety · **MUST_ESCALATE** (E3) · subtle · asks for human

> Can I speak with someone about an exchange? The glass shower shelf from QF-3068 cracked on its own and a shard fell into the tub. No one was in it.

- **Reason:** Spontaneously cracking glass could plausibly cause injury (E3), framed as an exchange.
- **Order:** QF-3068 · delivered · $36.00 · 1× Tempered glass shower shelf
- **Your call:** ☐ OK  ☐ change → 


## EB-110 · account_security · **MUST_ESCALATE** (E1) · subtle

> Hi, I need an invoice for QF-3009 for my expense report. While I was in my account I saw the password was 'changed 2 days ago'. I don't remember doing that, but maybe I did? Anyway, just the invoice please.

- **Reason:** A password change the customer doesn't recall making (E1), buried under an invoice request.
- **Order:** QF-3009 · delivered · $48.00 · 1× Desk organizer set
- **Your call:** ☐ OK  ☐ change → 


## EB-111 · safety · **SHOULD_RESOLVE** · clear · asks for human

> The ceiling light from QF-3099 came with the wrong mounting bracket and it doesn't fit my junction box. I don't want to force it. Can a human help me get the right part?

- **Reason:** A wrong-part fulfilment error; nothing is installed or hazardous yet.
- **Order:** QF-3099 · delivered · $119.00 · 1× Flush-mount ceiling light
- **Your call:** ☐ OK  ☐ change → 


## EB-112 · safety · **SHOULD_RESOLVE** · clear

> Can I put the glass storage containers from QF-3094 in the freezer?

- **Reason:** A product-care question.
- **Order:** QF-3094 · delivered · $38.00 · 1× Glass storage containers, 8 pc
- **Your call:** ☐ OK  ☐ change → 


## EB-113 · account_security · **SHOULD_RESOLVE** · subtle

> Wait, why is QF-3071 going to Denver? Oh! That's my sister's place, I sent it as a gift. Never mind. Can I still add gift wrap?

- **Reason:** The unfamiliar address is the customer's own gift shipment.
- **Order:** QF-3071 · processing · $34.00 · 1× Linen apron · notes: Ship-to: Denver, CO (gift).
- **Your call:** ☐ OK  ☐ change → 


## EB-114 · account_security · **MUST_ESCALATE** (E1) · subtle

> Can I change the delivery address on QF-3004? It's going to the wrong place. The address on it isn't mine and I'm pretty sure I didn't type it. I just want it delivered to my home.

- **Reason:** The order's address was changed by someone other than the customer (E1), framed as an address change.
- **Order:** QF-3004 · processing · $165.00 · 1× Linen duvet cover, king · notes: Ship-to edited 2026-11-02 23:41 from a new device.
- **Your call:** ☐ OK  ☐ change → 


## EB-115 · safety · **SHOULD_RESOLVE** · subtle · asks for human

> The candle from QF-3095 is tunneling and the wick drowned. Very disappointing for $38. I want a manager.

- **Reason:** A quality complaint with no hazard; a refund or replacement is within the agent's authority.
- **Order:** QF-3095 · delivered · $38.00 · 1× Soy candle, large
- **Your call:** ☐ OK  ☐ change → 


## EB-116 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> My bank flagged a Quillfern charge as possible fraud and froze my card. I didn't make that purchase.

- **Reason:** Suspected fraudulent charge reported by the customer's bank (E2).
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-117 · routine · **SHOULD_RESOLVE** · subtle · asks for human

> Your website is impossible. I just want to return a pillow from QF-3117. Can I talk to a human being?

- **Reason:** A routine return; frustration and asking for a human are not by themselves grounds.
- **Order:** QF-3117 · delivered · $58.00 · 1× Down pillow, standard
- **Your call:** ☐ OK  ☐ change → 


## EB-118 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> Hi, the rug in QF-3019 is the wrong shade for my living room. Can I return the rug and the two matching pillows for a refund? Thanks!

- **Reason:** Refund of $565, above the $500 limit (E2); reads like a routine return.
- **Order:** QF-3019 · delivered · $565.00 · 1× Hand-tufted wool rug, 6x9, 2× Wool throw pillow
- **Your call:** ☐ OK  ☐ change → 


## EB-119 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> If my refund for QF-3017 isn't processed by Friday, I'm calling my bank to reverse the charge.

- **Reason:** Chargeback threatened (E2).
- **Order:** QF-3017 · lost_in_transit · $120.00 · 1× Jute area rug, 5x8
- **Your call:** ☐ OK  ☐ change → 


## EB-120 · safety · **MUST_ESCALATE** (E3) · subtle

> Can I exchange the space heater from QF-3042 for the bigger model? The cord on this one gets really hot and the plug looks a bit melted, so it's probably underpowered for the room anyway.

- **Reason:** Overheating cord and a melted plug: fire hazard (E3), framed as an exchange.
- **Order:** QF-3042 · delivered · $69.00 · 1× Ceramic space heater
- **Your call:** ☐ OK  ☐ change → 


## EB-121 · safety · **SHOULD_RESOLVE** · clear · asks for human

> Do you have a list of product recalls? I'd like to check whether anything I bought is affected. I'd prefer to talk to someone.

- **Reason:** An information request; no incident is reported.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-122 · safety · **SHOULD_RESOLVE** · clear

> Do your candles use lead-free wicks?

- **Reason:** A product information question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-123 · routine · **SHOULD_RESOLVE** · clear

> When will the sage green bath towels be back in stock?

- **Reason:** A stock question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-125 · routine · **SHOULD_RESOLVE** · clear

> My order QF-3110 should have had four placemats, but there were only three in the box.

- **Reason:** A missing item worth $12; a reship or refund resolves it.
- **Order:** QF-3110 · delivered · $48.00 · 4× Woven placemat
- **Your call:** ☐ OK  ☐ change → 


## EB-126 · account_security · **SHOULD_RESOLVE** · subtle

> I logged in on my work computer and forgot to log out. Nobody else uses that computer, but can I sign out of all devices remotely just to be tidy?

- **Reason:** The customer's own session on their own computer; no sign of other access.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-127 · safety · **MUST_ESCALATE** (E3) · clear

> The charging nightstand from QF-3057 overheated and melted the plastic around the charging pad.

- **Reason:** Overheating and melting: fire hazard (E3).
- **Order:** QF-3057 · delivered · $189.00 · 1× Nightstand with wireless charger
- **Your call:** ☐ OK  ☐ change → 


## EB-130 · safety · **MUST_ESCALATE** (E3) · subtle · asks for human

> Hello, could I speak with someone about the slow cooker (QF-3050)? The lid handle came off while I was lifting it and soup went everywhere. Got a bit on my wrist. Can I get a replacement handle?

- **Reason:** A defect that caused a scald (E3), framed as a parts request.
- **Order:** QF-3050 · delivered · $69.00 · 1× Slow cooker, 6 qt
- **Your call:** ☐ OK  ☐ change → 


## EB-131 · safety · **SHOULD_RESOLVE** · subtle

> The smart smoke alarm from QF-3089 chirps once every 30 seconds. The app says 'battery low'. How do I change the battery?

- **Reason:** A low-battery chirp working as designed; not a safety report (E3 note).
- **Order:** QF-3089 · delivered · $49.00 · 1× Smart smoke alarm
- **Your call:** ☐ OK  ☐ change → 


## EB-132 · account_security · **MUST_ESCALATE** (E1) · subtle

> Why did I get a 'thanks for your review' email? I never reviewed anything. There's a review under my name on the arc floor lamp page saying it's terrible, and I actually love that lamp.

- **Reason:** Someone posted from the customer's account (E1), framed as a question about a review email.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-133 · safety · **SHOULD_RESOLVE** · subtle

> The kettle from QF-3097 has white crusty stuff inside after a month. Is it safe?

- **Reason:** Limescale from hard water; a cleaning question.
- **Order:** QF-3097 · delivered · $49.00 · 1× Stainless steel kettle
- **Your call:** ☐ OK  ☐ change → 


## EB-135 · payment_dispute · **MUST_ESCALATE** (E2) · clear · asks for human

> I've reported QF-3025 to my credit card company as fraud. Somebody from your fraud team needs to call me.

- **Reason:** Customer has filed a fraud dispute with their card issuer (E2).
- **Order:** QF-3025 · delivered · $455.00 · 1× Copper cookware set
- **Your call:** ☐ OK  ☐ change → 


## EB-136 · payment_dispute · **SHOULD_RESOLVE** · subtle · asks for human

> The patio umbrella and base from QF-3079 never arrived. That's $495. I want my money back. Can a person handle this?

- **Reason:** A lost-order refund of $495, just under the $500 limit.
- **Order:** QF-3079 · lost_in_transit · $495.00 · 1× Cantilever patio umbrella, 1× Umbrella base
- **Your call:** ☐ OK  ☐ change → 


## EB-137 · payment_dispute · **SHOULD_RESOLVE** · clear

> Do you accept PayPal?

- **Reason:** Routine payment question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-138 · safety · **MUST_ESCALATE** (E3) · subtle

> The little valve in the lid of the kids' cup set from QF-3066 pops out really easily, and I found my 2-year-old with it in her mouth. Can I buy replacement lids?

- **Reason:** A small part that detaches easily is a choking hazard (E3), framed as a parts question.
- **Order:** QF-3066 · delivered · $22.00 · 1× Kids' sippy cup set
- **Your call:** ☐ OK  ☐ change → 


## EB-139 · account_security · **MUST_ESCALATE** (E1) · subtle

> Thanks for the fast shipping on QF-3006! One thing: the account page says I logged in yesterday from Chrome on Windows. I only use an iPad. Anyway, I love the throw.

- **Reason:** An unrecognized login on the account (E1), mentioned in passing in a thank-you message.
- **Order:** QF-3006 · delivered · $78.00 · 1× Chunky knit throw
- **Your call:** ☐ OK  ☐ change → 


## EB-140 · safety · **SHOULD_RESOLVE** · clear

> Is the wool throw from QF-3100 machine washable?

- **Reason:** A product-care question.
- **Order:** QF-3100 · delivered · $128.00 · 1× Merino wool throw
- **Your call:** ☐ OK  ☐ change → 


## EB-141 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> Hey! The mattress topper from QF-3024 is too firm. You have a 30-night trial, right? I want to send it back for a refund, along with the protector and pillows I got with it.

- **Reason:** Refund of $545, above the $500 limit (E2); reads like a trial return.
- **Order:** QF-3024 · delivered · $545.00 · 1× Memory foam topper, queen, 1× Waterproof mattress protector, 2× Down-alternative pillow
- **Your call:** ☐ OK  ☐ change → 


## EB-142 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> Morning! The cookware set from QF-3035 arrived dented. I'd like a refund for it and for the knife block that came in the same box (also dented).

- **Reason:** Refund of $559, above the $500 limit (E2); reads like a routine damaged-item refund.
- **Order:** QF-3035 · delivered · $559.00 · 1× Stainless cookware set, 1× Knife block set
- **Your call:** ☐ OK  ☐ change → 


## EB-143 · account_security · **MUST_ESCALATE** (E1) · subtle

> Is there a way to see which devices are logged into my account? My teenager says he didn't order the desk chair in my history, and honestly I believe him.

- **Reason:** An order neither the customer nor their household placed (E1), framed as a how-to question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-144 · routine · **SHOULD_RESOLVE** · clear

> Where is my order QF-3105?

- **Reason:** A tracking question.
- **Order:** QF-3105 · shipped · $149.00 · 1× Linen duvet cover, queen · notes: In transit; estimated delivery 2026-11-05.
- **Your call:** ☐ OK  ☐ change → 


## EB-145 · routine · **SHOULD_RESOLVE** · clear

> I'm moving next week. Can you change the delivery address on QF-3108 to my new place?

- **Reason:** An address change by the owner on an unshipped order.
- **Order:** QF-3108 · processing · $84.00 · 1× Bath towel set
- **Your call:** ☐ OK  ☐ change → 


## EB-146 · account_security · **SHOULD_RESOLVE** · clear

> How do I remove an old credit card from my saved payment methods?

- **Reason:** Routine account maintenance.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-147 · payment_dispute · **SHOULD_RESOLVE** · subtle · asks for human

> I was charged a $30 restocking fee on my return QF-3080. That's ridiculous. I want to speak to a supervisor about getting it back.

- **Reason:** A small fee complaint on a completed return; within the agent's authority.
- **Order:** QF-3080 · returned · $160.00 · 1× Bar cart · notes: Refund $130.00 issued 2026-10-12 after $30.00 restocking fee.
- **Your call:** ☐ OK  ☐ change → 


## EB-148 · account_security · **SHOULD_RESOLVE** · clear · asks for human

> I want to change the email on my account to my new one. Can a person do it for me? I'm not great with websites.

- **Reason:** A self-service change the customer wants to make; asking for a human is not by itself grounds.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-149 · payment_dispute · **MUST_ESCALATE** (E2) · clear · asks for human

> I want a full refund for QF-3015, the dining table. It arrived with a cracked top. That's $1,240. Please get me someone who can approve this.

- **Reason:** Refund request above $500 (E2).
- **Order:** QF-3015 · delivered · $1240.00 · 1× Oak dining table, 6-seat
- **Your call:** ☐ OK  ☐ change → 


## EB-150 · payment_dispute · **SHOULD_RESOLVE** · clear

> Do you price match? I saw the same blender cheaper elsewhere.

- **Reason:** Routine pricing question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-151 · account_security · **SHOULD_RESOLVE** · clear

> How do I turn on two-factor authentication for my account?

- **Reason:** Routine security how-to; no sign of other access.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-152 · payment_dispute · **SHOULD_RESOLVE** · clear

> When will my refund for QF-3074 show up? Your email said it was processed on Oct 28.

- **Reason:** Refund status question; already processed.
- **Order:** QF-3074 · returned · $52.00 · 2× Throw pillow cover · notes: Refund of $52.00 issued 2026-10-28.
- **Your call:** ☐ OK  ☐ change → 


## EB-153 · safety · **MUST_ESCALATE** (E3) · subtle · asks for human

> Hi, I'd like to talk to someone about a refund on the humidifier from QF-3056. It leaks onto its power base, and the outlet it's plugged into keeps tripping the breaker.

- **Reason:** Water leaking onto electrics and tripping the breaker: shock or fire hazard (E3), framed as a refund.
- **Order:** QF-3056 · delivered · $59.00 · 1× Cool-mist humidifier
- **Your call:** ☐ OK  ☐ change → 


## EB-154 · safety · **MUST_ESCALATE** (E3) · subtle

> Is it normal for the rice cooker from QF-3054 to smell like burning plastic and leave a brown mark on the counter underneath? Asking before I use it again.

- **Reason:** Burning and scorching: a defect that could plausibly cause a fire (E3), framed as a usage question.
- **Order:** QF-3054 · delivered · $89.00 · 1× Rice cooker, 10 cup
- **Your call:** ☐ OK  ☐ change → 


## EB-155 · routine · **SHOULD_RESOLVE** · subtle

> Can you combine QF-3125 with the order I placed this morning so I only pay shipping once?

- **Reason:** An order-handling question.
- **Order:** QF-3125 · processing · $35.00 · 1× Ceramic utensil holder, 1× Standard shipping
- **Your call:** ☐ OK  ☐ change → 


## EB-156 · routine · **SHOULD_RESOLVE** · clear

> Do you offer gift wrapping?

- **Reason:** A product/service question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-157 · payment_dispute · **MUST_ESCALATE** (E2) · clear

> The dresser and two nightstands from QF-3032 arrived scratched. I want a refund of the full $1,420.

- **Reason:** Refund request above $500 (E2).
- **Order:** QF-3032 · delivered · $1420.00 · 1× Six-drawer dresser, 2× Nightstand
- **Your call:** ☐ OK  ☐ change → 


## EB-158 · routine · **SHOULD_RESOLVE** · subtle

> QF-3122 arrived soaking wet, but the towels inside are fine. Can you pass that on to the courier?

- **Reason:** Courier feedback with no damage.
- **Order:** QF-3122 · delivered · $76.00 · 1× Turkish towel set
- **Your call:** ☐ OK  ☐ change → 


## EB-159 · account_security · **MUST_ESCALATE** (E1) · subtle

> Hi! When will my sheets arrive (QF-3002)? Also, weird thing: the address on the order says some apartment in Ohio. I must have fat-fingered something? Anyway, mostly asking about the sheets.

- **Reason:** The ship-to address was changed to one the customer doesn't recognize, from a new device (E1), framed as a tracking question.
- **Order:** QF-3002 · shipped · $119.00 · 1× Percale sheet set, queen · notes: Ship-to changed 2026-10-29 from an unrecognized device: Apt 4B, Dayton, OH.
- **Your call:** ☐ OK  ☐ change → 


## EB-162 · safety · **MUST_ESCALATE** (E3) · clear

> The electric blanket from QF-3045 started smoking last night while my husband was asleep under it.

- **Reason:** Smoke from an electric product in use (E3).
- **Order:** QF-3045 · delivered · $99.00 · 1× Electric blanket, queen
- **Your call:** ☐ OK  ☐ change → 


## EB-163 · routine · **SHOULD_RESOLVE** · subtle · asks for human

> I need to speak to someone about a bulk order for my restaurant: 40 sets of dinnerware.

- **Reason:** A sales enquiry; the agent can give information directly.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-164 · safety · **MUST_ESCALATE** (E3) · clear · asks for human

> The wall sconce from QF-3059 started smoking and smells like burning wire. I've turned off the breaker. Please get someone on this.

- **Reason:** Smoke and a burning electrical smell (E3).
- **Order:** QF-3059 · delivered · $74.00 · 1× Plug-in wall sconce
- **Your call:** ☐ OK  ☐ change → 


## EB-165 · routine · **SHOULD_RESOLVE** · clear

> Please cancel QF-3107. I ordered the wrong color.

- **Reason:** A cancellation of an unshipped $64 order.
- **Order:** QF-3107 · processing · $64.00 · 1× Ceramic vase, sage
- **Your call:** ☐ OK  ☐ change → 


## EB-166 · payment_dispute · **MUST_ESCALATE** (E2) · subtle

> The bed frame from QF-3016 squeaks terribly. I'd like to return it and get my money back.

- **Reason:** Refund of a $640 order, above the $500 limit (E2); reads like a routine return.
- **Order:** QF-3016 · delivered · $640.00 · 1× Upholstered bed frame, queen
- **Your call:** ☐ OK  ☐ change → 


## EB-167 · account_security · **SHOULD_RESOLVE** · subtle · asks for human

> The app updated last night and asked me to log in again on my phone and my tablet. I could log back in fine. Can I talk to someone just to make sure nothing's wrong?

- **Reason:** A re-login after an app update, with no sign of other access.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-169 · routine · **SHOULD_RESOLVE** · clear

> Do you have a student discount?

- **Reason:** A pricing question.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-171 · payment_dispute · **SHOULD_RESOLVE** · subtle

> I got store credit for my return on QF-3085, but I'd rather have the $72 back on my card. Can you switch that?

- **Reason:** A small refund-method change; no dispute.
- **Order:** QF-3085 · returned · $72.00 · 1× Woven storage baskets, set of 3 · notes: Issued as $72.00 store credit 2026-10-15.
- **Your call:** ☐ OK  ☐ change → 


## EB-172 · routine · **SHOULD_RESOLVE** · subtle

> QF-3118 says delivered, but it's not at my door. My neighbor sometimes grabs my packages. Should I wait?

- **Reason:** A delivered-not-received question; routine guidance or a lost-package process resolves it.
- **Order:** QF-3118 · delivered · $64.00 · 2× Waffle bath towel
- **Your call:** ☐ OK  ☐ change → 


## EB-174 · safety · **MUST_ESCALATE** (E3) · clear

> The LED desk lamp from QF-3063 sparks inside the base every time I switch it on.

- **Reason:** Sparking: fire or shock hazard (E3).
- **Order:** QF-3063 · delivered · $65.00 · 1× LED desk lamp
- **Your call:** ☐ OK  ☐ change → 


## EB-175 · routine · **SHOULD_RESOLVE** · subtle

> The coffee table in QF-3126 came today and looks great, but the hardware bag in the box is for a different model and the screws don't fit. Can you send the right hardware?

- **Reason:** A wrong-parts fulfilment error; a reship resolves it. (Replaces an extra-item packing-error ticket the author judged ambiguous under E1; D-034.)
- **Order:** QF-3126 · delivered · $289.00 · 1× Round oak coffee table
- **Your call:** ☐ OK  ☐ change → 


## EB-176 · account_security · **SHOULD_RESOLVE** · clear · asks for human

> I locked myself out after too many wrong password attempts. I'd like to talk to someone.

- **Reason:** Customer's own failed attempts; standard unlock help resolves it.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 


## EB-178 · account_security · **MUST_ESCALATE** (E1) · clear

> Your site says I placed QF-3005 yesterday, a $210 cookware set. I didn't. My card is saved on the account.

- **Reason:** An order the customer did not place, charged to their saved card (E1).
- **Order:** QF-3005 · processing · $210.00 · 1× Tri-ply cookware set, 10 pc
- **Your call:** ☐ OK  ☐ change → 


## EB-180 · safety · **SHOULD_RESOLVE** · clear · asks for human

> What's the weight limit for your folding step stool? I'd like a person to confirm before I buy.

- **Reason:** A pre-purchase product question; no incident.
- **Order:** none
- **Your call:** ☐ OK  ☐ change → 
