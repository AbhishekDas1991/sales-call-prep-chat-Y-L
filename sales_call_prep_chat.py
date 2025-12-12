import time
import re
import streamlit as st

st.set_page_config(page_title="Sales Call Prep – US Mortgage Lead Coach", layout="wide")

st.title("💬 Sales Call Preparation – Mortgage Lead Coach")
st.caption("One US customer at a time. Short inputs, numeric details, and focused next questions.")

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lead" not in st.session_state:
    st.session_state.lead = {
        "name": None,
        "segment": None,
        "tenure_years": None,
        "objective": None,
        "current_rate": None,
        "current_payment": None,
        "current_balance": None,
        "competitor_rate": None,
        "our_rate": None,
        "savings_balance": None,
        "monthly_surplus": None,
        "travel_spend": None,
        "pricing_concern": False,
        "big_goal": None,  # e.g., college in 3 years
    }

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# ---------------------------------------------------------------------
# Display history
# ---------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# First message
if not st.session_state.messages:
    intro = (
        "Good day. I am your Sales Call Preparation AI Agent for US mortgage customers.\n\n"
        "We will focus on **one customer**. Start by telling me who you are calling and that it is about "
        "refinancing a home loan. Then you can feed me short updates like:\n"
        "`tenure 7 years`, `current loan rate 9.3% payment 4900`, "
        "`balances savings 120000 surplus 4000 travel 2500`, etc.\n"
        "When you type **summary**, I will assemble everything into a concise call plan."
    )
    add_message("assistant", intro)
    with st.chat_message("assistant"):
        st.markdown(intro)

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def parse_us_number(token: str) -> float | None:
    """Parse things like 4900, 49,000, 4k, 4.5k into a float."""
    token = token.lower().replace(",", "").strip()
    m = re.match(r"(\d+(\.\d+)?)(k)?", token)
    if not m:
        return None
    val = float(m.group(1))
    if m.group(3):  # has 'k'
        val *= 1000.0
    return val

def extract_name(text: str) -> str | None:
    m = re.search(
        r"\b(call(?:ing)?|speaking to|talking to|meeting|meeting with|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        text,
    )
    return m.group(2) if m else None

def detect_segment(text: str) -> str | None:
    t = text.lower()
    if any(w in t for w in ["self-employed", "business owner", "s corp", "llc"]):
        return "Self‑employed / business owner"
    if any(w in t for w in ["high net worth", "private bank", "premier"]):
        return "HNW / Private bank"
    if "affluent" in t or "professional" in t:
        return "Affluent professional"
    if "salary" in t or "w2" in t:
        return "Salaried"
    return None

def update_lead_from_free_text(text: str):
    lead = st.session_state.lead
    name = extract_name(text)
    if name:
        lead["name"] = name
    seg = detect_segment(text)
    if seg and not lead["segment"]:
        lead["segment"] = seg
    if "refinance" in text.lower() or "refi" in text.lower() or "mortgage" in text.lower():
        if not lead["objective"]:
            lead["objective"] = "refinance primary mortgage and strengthen relationship"
    if any(w in text.lower() for w in ["fees", "pricing", "closing costs", "points"]):
        lead["pricing_concern"] = True

def parse_structured_short_input(text: str):
    """Handle short, label-based updates like 'tenure 7 yrs, current loan rate 9.3% payment 4900'."""
    lead = st.session_state.lead
    t = text.lower()

    # Tenure
    if "tenure" in t or "with us" in t:
        n = parse_us_number(re.search(r"tenure\s+([0-9.,k]+)", t).group(1)) if re.search(r"tenure\s+([0-9.,k]+)", t) else None
        if n:
            lead["tenure_years"] = n

    # Current loan rate & payment
    if "current loan rate" in t or "current rate" in t:
        m = re.search(r"(current loan rate|current rate)\s+([0-9.,k]+)", t)
        if m:
            r = parse_us_number(m.group(2))
            if r:
                lead["current_rate"] = r
    if "payment" in t:
        m = re.search(r"payment\s+([0-9.,k]+)", t)
        if m:
            p = parse_us_number(m.group(1))
            if p:
                lead["current_payment"] = p

    # Balances and surplus
    if "balances" in t or "savings" in t:
        m = re.search(r"savings\s+([0-9.,k]+)", t)
        if m:
            b = parse_us_number(m.group(1))
            if b:
                lead["savings_balance"] = b
    if "surplus" in t:
        m = re.search(r"surplus\s+([0-9.,k]+)", t)
        if m:
            s = parse_us_number(m.group(1))
            if s:
                lead["monthly_surplus"] = s
    if "travel" in t:
        m = re.search(r"travel\s+([0-9.,k]+)", t)
        if m:
            tv = parse_us_number(m.group(1))
            if tv:
                lead["travel_spend"] = tv

    # Our rate
    if "our rate" in t:
        m = re.search(r"our rate\s+([0-9.,k]+)", t)
        if m:
            r = parse_us_number(m.group(1))
            if r:
                lead["our_rate"] = r

    # Competitor rate
    if "competitor" in t:
        m = re.search(r"competitor.*?([0-9.,k]+)", t)
        if m:
            r = parse_us_number(m.group(1))
            if r:
                lead["competitor_rate"] = r

    # Big goal
    if "college" in t or "education" in t or "tuition" in t:
        lead["big_goal"] = "future education funding"

# ---------------------------------------------------------------------
# Build guidance
# ---------------------------------------------------------------------
def build_guidance(text: str) -> str:
    lead = st.session_state.lead
    update_lead_from_free_text(text)
    parse_structured_short_input(text)

    name = lead["name"] or "the customer"

    lines = [f"We are preparing for a mortgage refinance call with **{name}**."]

    # Reflect what we know
    bullets = []
    if lead["tenure_years"]:
        bullets.append(f"Relationship: about **{lead['tenure_years']:.0f} years** with the bank.")
    if lead["current_rate"]:
        rate_str = f"{lead['current_rate']:.2f}%"
        pay_str = f"${lead['current_payment']:.0f}/month" if lead["current_payment"] else "payment not yet provided"
        bullets.append(f"Current mortgage rate around **{rate_str}**, {pay_str}.")
    if lead["our_rate"]:
        bullets.append(f"Target rate you may position: **{lead['our_rate']:.2f}%** (subject to credit / product fit).")
    if lead["competitor_rate"]:
        bullets.append(f"Competitor rate mentioned: roughly **{lead['competitor_rate']:.2f}%**.")
    if lead["savings_balance"]:
        bullets.append(f"Checking/savings balances with you: around **${lead['savings_balance']:.0f}**.")
    if lead["monthly_surplus"]:
        bullets.append(f"Estimated monthly surplus: about **${lead['monthly_surplus']:.0f}** after bills.")
    if lead["travel_spend"]:
        bullets.append(f"Travel card spend: roughly **${lead['travel_spend']:.0f} per month**.")
    if lead["pricing_concern"]:
        bullets.append("Customer is **very sensitive to pricing and fees**, and is likely comparing offers.")
    if lead["big_goal"]:
        bullets.append("Longer‑term goal flagged: **education/college funding**.")

    if bullets:
        lines.append("")
        lines.append("**Current picture (based on what you have entered):**")
        for b in bullets:
            lines.append(f"- {b}")

    # Next questions for the call
    lines.append("")
    lines.append("**Smart questions you can ask next:**")
    lines.append("1. “On your current mortgage, what is your **remaining balance** and how many years are left?”")
    if not lead["current_payment"]:
        lines.append("2. “What is your **exact monthly mortgage payment** today (principal + interest)?”")
    else:
        lines.append("2. “Is your current monthly payment of around that amount **comfortable**, or does it feel tight?”")
    lines.append("3. “If we could adjust your rate or term, what would a **comfortable payment range** look like for you?”")
    if not lead["monthly_surplus"]:
        lines.append("4. “After mortgage and other bills, roughly how much **cash is left over** in a typical month?”")
    else:
        lines.append("4. “Out of that surplus you mentioned, how much would you be comfortable earmarking for **savings or goals**?”")
    if lead["travel_spend"]:
        lines.append("5. “On your travel card, what matters more – **rewards, benefits, or annual fee**?”")
    else:
        lines.append("5. “Do you put a lot of **travel or discretionary spend** on credit cards that we should factor in?”")

    # Ask explicitly for missing data to improve guidance
    need = []
    if lead["tenure_years"] is None:
        need.append("tenure with our bank (years) → `tenure 7 years`")
    if lead["current_rate"] is None:
        need.append("current mortgage rate and payment → `current loan rate 6.9 payment 2300`")
    if lead["savings_balance"] is None or lead["monthly_surplus"] is None:
        need.append("balances and surplus → `balances savings 120000 surplus 4000`")
    if lead["our_rate"] is None:
        need.append("approximate rate you expect to position → `our rate 6.5`")
    if lead["competitor_rate"] is None and lead["pricing_concern"]:
        need.append("competitor rate if known → `competitor 6.75`")

    if need:
        lines.append("")
        lines.append("**To refine this further, you can give me short updates like:**")
        for n in need:
            lines.append(f"- {n}")

    lines.append("")
    lines.append("When you are ready for a final view, type **`summary`**.")

    return "\n".join(lines)

# ---------------------------------------------------------------------
# Build summary
# ---------------------------------------------------------------------
def build_summary() -> str:
    lead = st.session_state.lead
    name = lead["name"] or "the customer"
    parts = [f"**Call summary for {name}**\n"]

    if lead["tenure_years"]:
        parts.append(f"- Relationship with bank: **{lead['tenure_years']:.0f} years**.")
    if lead["current_rate"]:
        pay_txt = f"${lead['current_payment']:.0f}/month" if lead["current_payment"] else "monthly payment not captured"
        parts.append(f"- Current mortgage rate: **{lead['current_rate']:.2f}%**, {pay_txt}.")
    if lead["our_rate"]:
        parts.append(f"- Target rate to position: **{lead['our_rate']:.2f}%** (subject to underwriting).")
    if lead["competitor_rate"]:
        parts.append(f"- Competitor offer in discussion: about **{lead['competitor_rate']:.2f}%**.")
    if lead["savings_balance"]:
        parts.append(f"- Deposit balances with us: approximately **${lead['savings_balance']:.0f}**.")
    if lead["monthly_surplus"]:
        parts.append(f"- Estimated monthly surplus: about **${lead['monthly_surplus']:.0f}**.")
    if lead["travel_spend"]:
        parts.append(f"- Travel/discretionary card spend: roughly **${lead['travel_spend']:.0f} per month**.")
    if lead["pricing_concern"]:
        parts.append("- Customer is price‑sensitive and will pay attention to **fees, closing costs, and APR**.")
    if lead["big_goal"]:
        parts.append("- Longer‑term goal: **education/college saving over the next few years**.")

    parts.append("")
    parts.append("**Recommended focus in the call**")
    parts.append("- Make sure the customer clearly understands how your proposed payment, rate, and closing costs compare with today.")
    parts.append("- Connect refinance savings to their stated goals (e.g., monthly cash‑flow comfort and future education funding).")
    if lead["travel_spend"]:
        parts.append("- Decide whether a **travel‑optimized card** is relevant now or better as a follow‑up discussion.")
    parts.append("- End the call with an agreed next step: documentation, timeline, and how you will send the final numbers.")

    return "\n".join(parts)

# ---------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------
user_msg = st.chat_input("Describe the customer, paste numbers, or type 'summary' when ready...")

if user_msg:
    add_message("user", user_msg)
    with st.chat_message("user"):
        st.markdown(user_msg)

    lower = user_msg.strip().lower()

    if "summary" in lower:
        with st.chat_message("assistant"):
            with st.spinner("Preparing a concise summary for this mortgage call..."):
                time.sleep(1.0)
                reply = build_summary()
            st.markdown(reply)
        add_message("assistant", reply)
    else:
        with st.chat_message("assistant"):
            with st.spinner("Reviewing what you entered and suggesting next questions..."):
                time.sleep(1.0)
                reply = build_guidance(user_msg)
            st.markdown(reply)
        add_message("assistant", reply)
