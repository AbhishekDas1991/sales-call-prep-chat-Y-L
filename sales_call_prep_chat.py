import time
import re
import streamlit as st

st.set_page_config(page_title="Sales Call Prep – Chat Agent", layout="wide")

st.title("💬 Sales Call Preparation – Chat Agent")
st.caption("Question-focused coaching plus a final call summary when you ask for it.")

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lead_contexts" not in st.session_state:
    st.session_state.lead_contexts = {}  # name -> full text history
if "current_lead" not in st.session_state:
    st.session_state.current_lead = None

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
        "Start with a greeting, then tell me who you are calling and what the call is about.\n"
        "I will suggest the next questions to ask. When you type **summary** for that lead, "
        "I will generate a short overall call summary."
    )
    add_message("assistant", intro)
    with st.chat_message("assistant"):
        st.markdown(intro)

# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------
def detect_type(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["home loan", "mortgage", "refinance", "emi"]):
        return "refinance"
    if any(w in t for w in ["working capital", "cash flow", "receivable", "invoice", "sme", "business"]):
        return "sme_wc"
    if any(w in t for w in ["fees", "pricing", "charges"]):
        return "pricing"
    return "generic"

def extract_name(text: str) -> str | None:
    # try "calling John Doe", "meeting with Sarah Lee", etc.
    m = re.search(
        r"\b(call(?:ing)?|speaking to|talking to|meeting with|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        text,
    )
    return m.group(2) if m else None

def ensure_lead_context(name: str):
    if name not in st.session_state.lead_contexts:
        st.session_state.lead_contexts[name] = ""

def append_to_lead_context(name: str, text: str):
    ensure_lead_context(name)
    prev = st.session_state.lead_contexts[name]
    st.session_state.lead_contexts[name] = (prev + "\n" + text).strip()

# ---------------------------------------------------------------------
# Short guidance: next questions
# ---------------------------------------------------------------------
def build_short_guidance(text: str, name: str) -> str:
    lead_type = detect_type(text)
    header = f"Here is how you can move the conversation with **{name}** forward:\n\n"

    if lead_type == "refinance":
        body = (
            "**Key focus:** Home loan refinance and relationship deepening.\n\n"
            "**Ask next:**\n"
            "1. “What is most important for you in this refinance – lower EMI, faster payoff, or more flexibility?”\n"
            "2. “What rate and fees has the other bank offered you so far?”\n"
            "3. “Are there any upcoming expenses that will affect how much EMI you are comfortable with?”\n"
            "4. “How much of your monthly surplus would you like to keep liquid versus in a high‑yield account?”\n"
            "5. “Is there anything in your experience with us that you would like improved before you decide?”"
        )
    elif lead_type == "pricing":
        body = (
            "**Key focus:** Pricing and fee sensitivity.\n\n"
            "**Ask next:**\n"
            "1. “Which specific fees or charges feel unfair or unclear to you?”\n"
            "2. “How are you comparing offers between banks – total cost over time, or mainly the headline rate?”\n"
            "3. “If we simplify or reduce some fees, which ones would matter most to you?”\n"
            "4. “Apart from pricing, what else will influence your decision to stay with us?”\n"
            "5. “Would a one‑page comparison after this call help you decide comfortably?”"
        )
    elif lead_type == "sme_wc":
        body = (
            "**Key focus:** SME working capital and collections.\n\n"
            "**Ask next:**\n"
            "1. “For your newer customers, how many days on average do they take to pay you?”\n"
            "2. “Where in the month do you usually feel the tightest cash‑flow gap?”\n"
            "3. “Do you currently use early‑payment discounts or any collections tools?”\n"
            "4. “What would a comfortable working‑capital limit look like for the next 12 months?”\n"
            "5. “How do you prefer to review this – a simple cash‑flow view or example scenarios?”"
        )
    else:
        body = (
            "**Key focus:** Understanding needs and building trust.\n\n"
            "**Ask next:**\n"
            "1. “What would make this call most valuable for you today?”\n"
            "2. “How satisfied are you with your current products and day‑to‑day experience with us?”\n"
            "3. “Are there any upcoming events or large expenses you are planning for?”\n"
            "4. “How do you prefer to communicate with us – RM, branch, app, WhatsApp, or a mix?”\n"
            "5. “Is there anything that would make you consider moving part of your business to another bank?”"
        )

    return header + body

# ---------------------------------------------------------------------
# Summary: overall view for a lead
# ---------------------------------------------------------------------
def build_summary(name: str, ctx: str) -> str:
    lead_type = detect_type(ctx)
    t = ctx.lower()

    themes = []
    if any(w in t for w in ["refinance", "home loan", "mortgage"]):
        themes.append("Home loan refinance is a primary topic.")
    if any(w in t for w in ["high-yield", "high‑yield", "savings", "deposit", "surplus"]):
        themes.append("There is surplus balance that could move into higher‑yield savings.")
    if any(w in t for w in ["fees", "pricing", "charges"]):
        themes.append("Pricing and fees are important in the decision.")
    if any(w in t for w in ["working capital", "cash flow", "receivable", "invoice"]):
        themes.append("Business cash‑flow and working‑capital requirements are key.")
    if not themes:
        themes.append("The call is mainly about understanding needs and keeping the relationship strong.")

    risks = []
    if any(w in t for w in ["unhappy", "complaint", "issue"]):
        risks.append("There are service issues that must be acknowledged and resolved early.")
    if any(w in t for w in ["comparing", "other bank"]):
        risks.append("The customer is comparing other banks; clarity and transparency are critical.")
    if "low engagement" in t or ("branch" in t and "digital" in t):
        risks.append("Digital engagement appears low; there is an opportunity to simplify her routine tasks.")
    if not risks:
        risks.append("No explicit red flags mentioned, but start with a quick satisfaction check.")

    opps = []
    if lead_type == "refinance":
        opps.append("Close the refinance with a clear rate and fee comparison.")
        opps.append("Deepen balances using a high‑yield savings or short‑term deposit.")
    elif lead_type == "sme_wc":
        opps.append("Right‑size working‑capital limits to match receivable cycles.")
        opps.append("Introduce simple collections and digital tools that reduce branch visits.")
    else:
        opps.append("Identify one or two specific solutions that directly match the customer’s stated needs.")

    summary = f"""\
**Lead summary – {name}**

**What this call is mainly about**

- """ + "\n- ".join(themes) + """

**Key risks to keep in mind**

- """ + "\n- ".join(risks) + """

**Main opportunities**

- """ + "\n- ".join(opps) + """

**Suggested outcome for this call**

- Agree on a clear decision or next step on the main topic, plus a simple follow‑up plan (who does what, and by when).
"""
    return summary

# ---------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------
user_msg = st.chat_input("Say hello, describe the customer, or type 'summary' for the current lead...")

if user_msg:
    add_message("user", user_msg)
    with st.chat_message("user"):
        st.markdown(user_msg)

    lower = user_msg.strip().lower()
    greeting_words = ("hi", "hello", "hey", "good morning", "good evening", "good afternoon")

    # Detect or update current lead from message
    detected_name = extract_name(user_msg)
    if detected_name:
        st.session_state.current_lead = detected_name
    current_name = st.session_state.current_lead or "this customer"

    # Save context for that lead
    if st.session_state.current_lead:
        append_to_lead_context(st.session_state.current_lead, user_msg)

    # Greeting-only
    if any(lower.startswith(g) for g in greeting_words) and len(lower.split()) <= 4:
        response = (
            "Hello. Please tell me who you are calling, what the call is about, "
            "and what you would like to achieve. I will suggest the next questions to ask."
        )
        with st.chat_message("assistant"):
            st.markdown(response)
        add_message("assistant", response)

    # Summary request
    elif "summary" in lower and st.session_state.current_lead:
        ctx = st.session_state.lead_contexts.get(st.session_state.current_lead, "")
        with st.chat_message("assistant"):
            with st.spinner(f"Compiling a brief summary for {current_name}..."):
                time.sleep(1.0)
                reply = build_summary(current_name, ctx)
            st.markdown(reply)
        add_message("assistant", reply)

    # Normal guidance
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking about the best next questions..."):
                time.sleep(1.0)
                reply = build_short_guidance(user_msg, current_name)
            st.markdown(reply)
        add_message("assistant", reply)

# Sidebar tips
with st.sidebar:
    st.subheader("How to use this")
    st.markdown(
        "- Mention the customer name to start a lead (e.g., “I am calling John Doe…”).\n"
        "- Ask for guidance multiple times; the agent will suggest the next questions.\n"
        "- When ready for a wrap‑up, type **summary** to get an overall view for that lead."
    )
