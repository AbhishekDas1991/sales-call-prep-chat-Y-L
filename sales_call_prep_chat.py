import time
import re
import streamlit as st

st.set_page_config(page_title="Sales Call Prep – US Mortgage Coach", layout="wide")

st.title("💬 Sales Call Preparation – US Mortgage Coach")
st.caption("One refinance lead at a time. Short RM inputs, clear next questions, and a concise summary.")

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lead" not in st.session_state:
    st.session_state.lead = {
        "name": None,
        "state": None,
        "segment": None,
        "tenure_years": None,
        "objective": None,
        "current_rate": None,
        "current_payment": None,
        "remaining_term_years": None,
        "remaining_balance": None,
        "competitor_rate": None,
        "our_rate": None,
        "savings_balance": None,
        "monthly_surplus": None,
        "travel_spend": None,
        "pricing_concern": False,
        "big_goal": None,
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
        "We will focus on **one refinance lead**. Start by telling me who you are calling "
        "and that it is about refinancing their mortgage.\n\n"
        "Then you can send short updates such as:\n"
        "- `tenure 6 yrs, rate 9.5, pay 5200`\n"
        "- `bal 320k, term 24 yrs`\n"
        "- `dep 120k, surplus 4k, travel 2.5k`\n"
        "- `offer 8.4, competitor 8.7, borrower worried about fees`\n\n"
        "When you type **summary**, I will assemble everything into a concise call plan."
    )
    add_message("assistant", intro)
    with st.chat_message("assistant"):
        st.markdown(intro)

# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def parse_us_number(token: str) -> float | None:
    token = token.lower().replace(",", "").strip()
    m = re.match(r"(\d+(\.\d+)?)(k)?", token)
    if not m:
        return None
    val = float(m.group(1))
    if m.group(3):
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
    if any(w in t for w in ["self-employed", "business owner", "1099"]):
        return "Self‑employed / business owner"
    if any(w in t for w in ["high net worth", "private bank", "premier"]):
        return "HNW / private banking"
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

    m_state = re.search(r"in\s+([A-Z][a-z]+)", text)
    if m_state and not lead["state"]:
        lead["state"] = m_state.group(1)

    seg = detect_segment(text)
    if seg and not lead["segment"]:
        lead["segment"] = seg

    low = text.lower()
    if any(w in low for w in ["refinance", "refi", "mortgage"]):
        if not lead["objective"]:
            lead["objective"] = "refinance existing mortgage and improve cash flow"
    if any(w in low for w in ["fees", "pricing", "closing costs", "points", "worried about fees"]):
        lead["pricing_concern"] = True
    if any(w in low for w in ["college", "education", "tuition", "daughter college"]):
        lead["big_goal"] = "college / education funding"


def parse_structured_short_input(text: str):
    lead = st.session_state.lead
    t = text.lower()

    # tenure
    m = re.search(r"tenure\s+([0-9.,k]+)", t)
    if m:
        n = parse_us_number(m.group(1))
        if n:
            lead["tenure_years"] = n

    # rate / pay (allow 'rate' or 'current rate')
    m = re.search(r"(current loan rate|current rate|rate)\s+([0-9.,k]+)", t)
    if m:
        r = parse_us_number(m.group(2))
        if r:
            lead["current_rate"] = r
    m = re.search(r"(payment|pay)\s+([0-9.,k]+)", t)
    if m:
        p = parse_us_number(m.group(2))
        if p:
            lead["current_payment"] = p

    # term / balance (allow 'bal' / 'balance')
    m = re.search(r"(term)\s+([0-9.,k]+)", t)
    if m:
        n = parse_us_number(m.group(2))
        if n:
            lead["remaining_term_years"] = n
    m = re.search(r"(bal|balance)\s+([0-9.,k]+)", t)
    if m:
        b = parse_us_number(m.group(2))
        if b:
            lead["remaining_balance"] = b

    # deposits / surplus / travel (allow 'dep')
    m = re.search(r"(dep|savings)\s+([0-9.,k]+)", t)
    if m:
        b = parse_us_number(m.group(2))
        if b:
            lead["savings_balance"] = b
    m = re.search(r"surplus\s+([0-9.,k]+)", t)
    if m:
        s = parse_us_number(m.group(1))
        if s:
            lead["monthly_surplus"] = s
    m = re.search(r"travel\s+([0-9.,k]+)", t)
    if m:
        tv = parse_us_number(m.group(1))
        if tv:
            lead["travel_spend"] = tv

    # our rate / competitor (allow 'offer')
    m = re.search(r"(our rate|offer)\s+([0-9.,k]+)", t)
    if m:
        r = parse_us_number(m.group(2))
        if r:
            lead["our_rate"] = r
    m = re.search(r"competitor.*?([0-9.,k]+)", t)
    if m:
        r = parse_us_number(m.group(1))
        if r:
            lead["competitor_rate"] = r


# ---------------------------------------------------------------------
# Guidance builder
# ---------------------------------------------------------------------
def build_guidance(text: str) -> str:
    lead = st.session_state.lead
    update_lead_from_free_text(text)
    parse_structured_short_input(text)

    name = lead["name"] or "the customer"
    state = f" in {lead['state']}" if lead["state"] else ""
    lines: list[str] = []

    # 1) Ask the customer now – driven by gaps
    lines.append(f"**Ask {name}{state} now:**")

    if lead["remaining_balance"] is None:
        lines.append("1. “Roughly how much do you still owe and how many years are left on the mortgage?”")
    else:
        lines.append("1. “Do you expect to stay in this home for most of the remaining term, or might you move sooner?”")

    if lead["current_payment"] is None:
        lines.append("2. “What is your current monthly mortgage payment (principal + interest)?”")
    else:
        lines.append("2. “Does that monthly payment feel comfortable, or does it strain your budget?”")

    lines.append("3. “If we refinance, what would a comfortable monthly payment range look like for you?”")

    if lead["monthly_surplus"] is None:
        lines.append("4. “After the mortgage and other bills, about how much cash is left over each month?”")
    else:
        lines.append("4. “From that leftover cash, how much would you be comfortable directing toward savings or goals?”")

    if lead["travel_spend"] is not None:
        lines.append("5. “On your main credit card, do you care more about rewards, travel perks, or a lower annual fee?”")
    elif lead["pricing_concern"]:
        lines.append("5. “When you think about closing costs and fees, which items bother you the most?”")
    else:
        lines.append("5. “Besides the interest rate, what else will matter most in choosing who you refinance with?”")

    # 2) Snapshot below
    lines.append("")
    lines.append(f"**Snapshot so far – {name}{state}:**")
    snapshot = []
    if lead["tenure_years"] is not None:
        snapshot.append(f"- Relationship: **{lead['tenure_years']:.0f} yrs** with your bank.")
    if lead["current_rate"] is not None:
        pay_txt = f"${lead['current_payment']:.0f}/mo" if lead["current_payment"] else "payment not captured yet"
        snapshot.append(f"- Current mortgage: **{lead['current_rate']:.2f}%**, {pay_txt}.")
    if lead["remaining_balance"] is not None:
        bal_txt = f"${lead['remaining_balance']:.0f}"
        yrs_txt = f"{lead['remaining_term_years']:.0f} yrs left" if lead["remaining_term_years"] else "term not captured"
        snapshot.append(f"- Remaining balance: **{bal_txt}**, {yrs_txt}.")
    if lead["our_rate"] is not None:
        snapshot.append(f"- Rate you are considering: **{lead['our_rate']:.2f}%** (subject to approval).")
    if lead["competitor_rate"] is not None:
        snapshot.append(f"- Competitor mentioned: ~**{lead['competitor_rate']:.2f}%**.")
    if lead["savings_balance"] is not None:
        snapshot.append(f"- Deposits: ~**${lead['savings_balance']:.0f}** on deposit with you.")
    if lead["monthly_surplus"] is not None:
        snapshot.append(f"- Estimated monthly surplus: ~**${lead['monthly_surplus']:.0f}** after bills.")
    if lead["travel_spend"] is not None:
        snapshot.append(f"- Travel / card spend: ~**${lead['travel_spend']:.0f}/mo**.")
    if lead["pricing_concern"]:
        snapshot.append("- Customer is **rate‑ and fee‑sensitive**.")
    if lead["big_goal"]:
        snapshot.append("- Long‑term goal: **college / education saving** in the next few years.")

    if not snapshot:
        snapshot.append("- Key numbers not captured yet. Start with tenure, current rate, payment, and balances.")

    lines.extend(snapshot)

    # 3) Internal checklist (only what is still missing)
    need = []
    if lead["tenure_years"] is None:
        need.append("tenure with your bank (years).")
    if lead["current_rate"] is None or lead["current_payment"] is None:
        need.append("exact current rate and monthly payment.")
    if lead["remaining_balance"] is None or lead["remaining_term_years"] is None:
        need.append("approximate remaining balance and years left on the loan.")
    if lead["savings_balance"] is None or lead["monthly_surplus"] is None:
        need.append("checking / savings balances and typical monthly surplus.")
    if lead["our_rate"] is None:
        need.append("the rate you expect to position on this call.")
    if lead["pricing_concern"] and lead["competitor_rate"] is None:
        need.append("any competitor rate the borrower has mentioned.")

    if need:
        lines.append("")
        lines.append("**Your internal checklist:**")
        for n in need:
            lines.append(f"- {n}")

    lines.append("")
    lines.append("When you want the consolidated call plan, type **`summary`**.")

    return "\n".join(lines)


# ---------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------
def build_summary() -> str:
    lead = st.session_state.lead
    name = lead["name"] or "the customer"
    state = f" in {lead['state']}" if lead["state"] else ""
    parts: list[str] = []

    parts.append(f"**Call summary – {name}{state}**\n")

    if lead["tenure_years"] is not None:
        parts.append(f"- Relationship with bank: **{lead['tenure_years']:.0f} years**.")
    if lead["current_rate"] is not None:
        pay_txt = f"${lead['current_payment']:.0f}/mo" if lead["current_payment"] else "payment not captured"
        parts.append(f"- Current mortgage: **{lead['current_rate']:.2f}%**, {pay_txt}.")
    if lead["remaining_balance"] is not None:
        term_txt = (
            f"{lead['remaining_term_years']:.0f} yrs left" if lead["remaining_term_years"] else "term not captured"
        )
        parts.append(f"- Remaining balance: **${lead['remaining_balance']:.0f}**, {term_txt}.")
    if lead["our_rate"] is not None:
        parts.append(f"- Target rate to position: **{lead['our_rate']:.2f}%** (subject to underwriting).")
    if lead["competitor_rate"] is not None:
        parts.append(f"- Competitor offer in discussion: ~**{lead['competitor_rate']:.2f}%**.")
    if lead["savings_balance"] is not None:
        parts.append(f"- Deposits with your bank: ~**${lead['savings_balance']:.0f}**.")
    if lead["monthly_surplus"] is not None:
        parts.append(f"- Estimated monthly surplus after bills: ~**${lead['monthly_surplus']:.0f}**.")
    if lead["travel_spend"] is not None:
        parts.append(f"- Travel / discretionary card spend: ~**${lead['travel_spend']:.0f}/mo**.")
    if lead["pricing_concern"]:
        parts.append("- Customer is **rate‑ and fee‑sensitive**; APR and closing costs will drive the decision.")
    if lead["big_goal"]:
        parts.append("- Long‑term goal: **college / education saving in ~3 years**.")
    if lead["objective"]:
        parts.append(f"- Your stated objective: **{lead['objective']}**.")

    parts.append("")
    parts.append("**Recommended focus for this call**")
    parts.append("- Confirm remaining term, remaining balance, and how long they expect to stay in the property.")
    parts.append("- Present a simple comparison: current loan vs your offer vs any competitor (payment, APR, cash to close).")
    parts.append("- Link refinance savings to their goals (monthly comfort and college savings plan).")
    if lead["travel_spend"] is not None:
        parts.append("- Decide whether to align their travel spend with a more suitable rewards card now or at a follow‑up.")
    parts.append(
        "- Close with clear next steps: documents needed, rate‑lock / timeline expectations, and how you will send final numbers."
    )

    return "\n".join(parts)


# ---------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------
user_msg = st.chat_input(
    "Short notes only: who/where, or things like 'tenure 6 yrs, rate 9.5, pay 5200', or type 'summary'..."
)

if user_msg:
    add_message("user", user_msg)
    with st.chat_message("user"):
        st.markdown(user_msg)

    lower = user_msg.strip().lower()

    if "summary" in lower:
        with st.chat_message("assistant"):
            with st.spinner("Preparing a concise call plan..."):
                time.sleep(1.0)
                reply = build_summary()
            st.markdown(reply)
        add_message("assistant", reply)
    else:
        with st.chat_message("assistant"):
            with st.spinner("Reviewing details and shaping next questions..."):
                time.sleep(1.0)
                reply = build_guidance(user_msg)
            st.markdown(reply)
        add_message("assistant", reply)
