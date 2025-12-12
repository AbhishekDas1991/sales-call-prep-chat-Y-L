import time
import re
import streamlit as st

st.set_page_config(page_title="Sales Call Prep – Detailed Lead Coach", layout="wide")

st.title("💬 Sales Call Preparation – Detailed Lead Coach")
st.caption("Guides you through one lead, collecting numbers and details step by step.")

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lead_info" not in st.session_state:
    # structured info we collect along the way
    st.session_state.lead_info = {
        "name": None,
        "segment": None,
        "tenure_years": None,
        "objective": None,
        "current_bank_rate": None,
        "current_bank_emi": None,
        "our_offer_rate": None,
        "surplus_monthly": None,
        "savings_balance": None,
        "travel_spend": None,
        "pricing_concern": False,
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
        "Good day. I am your Sales Call Preparation AI Agent.\n\n"
        "We will focus on **one customer** at a time. Start by telling me who you are calling "
        "and what the call is broadly about. You can keep responses short and include numbers "
        "where you have them (e.g., rate %, EMI amount, balances)."
    )
    add_message("assistant", intro)
    with st.chat_message("assistant"):
        st.markdown(intro)

# ---------------------------------------------------------------------
# Helper parsing functions
# ---------------------------------------------------------------------
def extract_name(text: str) -> str | None:
    # e.g., "calling John Doe", "with John Doe"
    m = re.search(
        r"\b(call(?:ing)?|speaking to|talking to|meeting|meeting with|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        text
    )
    if m:
        return m.group(2)
    return None

def extract_number(text: str) -> float | None:
    # first float or int in the text
    m = re.search(r"(\d+(\.\d+)?)", text)
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None

def detect_segment(text: str) -> str | None:
    t = text.lower()
    if any(w in t for w in ["sme", "business", "company", "msme"]):
        return "SME / Business"
    if any(w in t for w in ["affluent", "priority", "hni", "premier"]):
        return "Affluent / Priority"
    if "salaried" in t or "salary" in t:
        return "Salaried Retail"
    return None

def detect_pricing_concern(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in ["fees", "pricing", "charges", "rate", "expensive"])

def update_lead_info_from_text(text: str):
    info = st.session_state.lead_info
    name = extract_name(text)
    if name:
        info["name"] = name

    seg = detect_segment(text)
    if seg and not info["segment"]:
        info["segment"] = seg

    if "year" in text.lower() and info["tenure_years"] is None:
        n = extract_number(text)
        if n:
            info["tenure_years"] = n

    if "objective" in text.lower() or "want to" in text.lower():
        # basic objective capture
        m = re.search(r"(objective.*|want to.*)", text, re.IGNORECASE)
        if m:
            info["objective"] = m.group(0)

    if detect_pricing_concern(text):
        info["pricing_concern"] = True

# ---------------------------------------------------------------------
# Build response with next questions + contextual hints
# ---------------------------------------------------------------------
def build_response(text: str) -> str:
    info = st.session_state.lead_info
    update_lead_info_from_text(text)

    # Try to guess if this is refinance vs generic based on keywords
    t = text.lower()
    is_refi = any(w in t for w in ["refinance", "home loan", "mortgage"])
    name = info["name"] or "the customer"

    # see what we already know
    missing = []
    if info["tenure_years"] is None:
        missing.append("tenure with the bank (in years)")
    if info["objective"] is None:
        missing.append("your objective for this call in one line")
    if info["current_bank_rate"] is None and is_refi:
        missing.append("current rate % and EMI at the other bank")
    if info["our_offer_rate"] is None and is_refi:
        missing.append("the rate % you expect to position from our side")
    if info["savings_balance"] is None:
        missing.append("current average savings balance")
    if info["surplus_monthly"] is None:
        missing.append("approximate monthly surplus after EMI and regular spends")
    if info["travel_spend"] is None and "travel" in t:
        missing.append("approximate monthly travel card spend")

    # start building reply
    reply_lines = []

    reply_lines.append(f"Understood. We are preparing for a call with **{name}**.")
    if is_refi:
        reply_lines.append("This looks like a **home loan refinance** and relationship‑deepening discussion.")
    else:
        reply_lines.append("This looks like a general relationship / needs discussion for this customer.")

    # If we have some numbers already, reflect them back
    if info["tenure_years"]:
        reply_lines.append(f"- Tenure with you: approximately **{info['tenure_years']:.0f} years**.")
    if info["current_bank_rate"]:
        reply_lines.append(f"- Current external rate: about **{info['current_bank_rate']:.2f}%**.")
    if info["current_bank_emi"]:
        reply_lines.append(f"- Current EMI: around **{info['current_bank_emi']:.0f}** per month.")
    if info["our_offer_rate"]:
        reply_lines.append(f"- Target rate you may position: around **{info['our_offer_rate']:.2f}%**.")
    if info["savings_balance"]:
        reply_lines.append(f"- Savings balance with you: roughly **{info['savings_balance']:.0f}**.")
    if info["surplus_monthly"]:
        reply_lines.append(f"- Monthly surplus estimated at **{info['surplus_monthly']:.0f}**.")
    if info["travel_spend"]:
        reply_lines.append(f"- Travel card spend: around **{info['travel_spend']:.0f} per month**.")
    if info["pricing_concern"]:
        reply_lines.append("- Pricing and fees are important to the customer.")

    reply_lines.append("")
    reply_lines.append("**Questions you can ask next in this call:**")

    if is_refi:
        reply_lines.extend([
            "1. “On your current home loan, what is the **exact rate and EMI** you are paying now?”",
            "2. “If we could reach an EMI around a certain level, what would feel comfortable for your monthly budget?”",
            "3. “Do you expect any **large expenses** in the next 6–12 months that might change how much EMI you can handle?”",
            "4. “Each month, after EMI and usual spends, roughly how much **surplus** is left in your account?”",
            "5. “Would you prefer to keep that surplus liquid, or move part of it into a **high‑yield savings or deposit**?”",
        ])
    else:
        reply_lines.extend([
            "1. “What would you like to achieve from this conversation today in one line?”",
            "2. “How satisfied are you with your current products and experience with us?”",
            "3. “Are there any upcoming life events or large expenses you are planning for?”",
            "4. “How do you usually manage your monthly cash‑flow and savings — roughly what stays as surplus?”",
            "5. “How do you prefer to stay in touch — RM, branch, app, WhatsApp, or email?”",
        ])

    if missing:
        reply_lines.append("")
        reply_lines.append("**To help me coach you better, please also share (short answers, with numbers where possible):**")
        for item in missing[:5]:  # show up to 5 missing items
            reply_lines.append(f"- {item}")

    reply_lines.append("")
    reply_lines.append("You can respond in short form, for example: `tenure 6 yrs, current rate 9.2, EMI 48k, savings 12L, surplus 40k`.")

    return "\n".join(reply_lines)

# ---------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------
user_msg = st.chat_input("Describe the customer, paste numbers, or ask for 'summary' when ready...")

if user_msg:
    add_message("user", user_msg)
    with st.chat_message("user"):
        st.markdown(user_msg)

    lower = user_msg.strip().lower()

    # Manual updates from shorthand numeric inputs
    info = st.session_state.lead_info
    if "tenure" in lower and info["tenure_years"] is None:
        n = extract_number(user_msg)
        if n:
            info["tenure_years"] = n
    if "current rate" in lower and info["current_bank_rate"] is None:
        n = extract_number(user_msg)
        if n:
            info["current_bank_rate"] = n
    if "emi" in lower and info["current_bank_emi"] is None:
        n = extract_number(user_msg)
        if n:
            info["current_bank_emi"] = n
    if "our rate" in lower and info["our_offer_rate"] is None:
        n = extract_number(user_msg)
        if n:
            info["our_offer_rate"] = n
    if "savings" in lower and info["savings_balance"] is None:
        n = extract_number(user_msg)
        if n:
            info["savings_balance"] = n
    if "surplus" in lower and info["surplus_monthly"] is None:
        n = extract_number(user_msg)
        if n:
            info["surplus_monthly"] = n
    if "travel" in lower and info["travel_spend"] is None:
        n = extract_number(user_msg)
        if n:
            info["travel_spend"] = n

    # Summary request
    if "summary" in lower:
        info = st.session_state.lead_info
        name = info["name"] or "the customer"
        with st.chat_message("assistant"):
            with st.spinner("Compiling a brief summary for this call..."):
                time.sleep(1.0)
                parts = [f"**Call summary for {name}**\n"]
                if info["tenure_years"]:
                    parts.append(f"- Relationship tenure: **{info['tenure_years']:.0f} years**.")
                if info["current_bank_rate"]:
                    parts.append(
                        f"- Current external home loan rate: **{info['current_bank_rate']:.2f}%**, "
                        f"EMI ~ **{info['current_bank_emi'] or 0:.0f}**."
                    )
                if info["our_offer_rate"]:
                    parts.append(f"- Target rate you plan to position: **{info['our_offer_rate']:.2f}%**.")
                if info["savings_balance"]:
                    parts.append(f"- Savings balance with you: around **{info['savings_balance']:.0f}**.")
                if info["surplus_monthly"]:
                    parts.append(f"- Estimated monthly surplus: **{info['surplus_monthly']:.0f}**.")
                if info["travel_spend"]:
                    parts.append(f"- Travel card spend: about **{info['travel_spend']:.0f} per month**.")
                if info["pricing_concern"]:
                    parts.append("- Customer is sensitive to pricing/fees and is likely comparing offers.")

                parts.append("")
                parts.append("**Suggested outcome for this call**")
                parts.append(
                    "- Agree on a refinance structure that improves EMI or rate meaningfully versus current terms."
                )
                parts.append(
                    "- Agree how much surplus will move into high‑yield savings/deposits and how much remains liquid."
                )
                if info["travel_spend"]:
                    parts.append("- Decide whether a travel‑optimized card upgrade makes sense now or in a later step.")
                parts.append("- Confirm any follow‑up documents and the exact date/time of your next conversation.")

                reply = "\n".join(parts)
            st.markdown(reply)
        add_message("assistant", reply)

    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking about the next questions and what we still need to know..."):
                time.sleep(1.0)
                reply = build_response(user_msg)
            st.markdown(reply)
        add_message("assistant", reply)
