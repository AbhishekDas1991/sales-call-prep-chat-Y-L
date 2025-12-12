import time
import re
import streamlit as st

st.set_page_config(page_title="Sales Call Prep – Chat Agent", layout="wide")

st.title("💬 Sales Call Preparation – Chat Agent")
st.caption("Short, question-focused guidance for your next customer call.")

# Initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# First message
if not st.session_state.messages:
    intro = (
        "Good day. I am your Sales Call Preparation AI Agent.\n\n"
        "Start with a simple greeting, then tell me who you are calling and what the call is about."
    )
    add_message("assistant", intro)
    with st.chat_message("assistant"):
        st.markdown(intro)

# --- Simple classifiers -------------------------------------------------------

def detect_type(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["home loan", "mortgage", "refinance", "emi"]):
        return "refinance"
    if any(w in t for w in ["working capital", "cash flow", "receivable", "invoice", "sme", "business"]):
        return "sme_wc"
    if any(w in t for w in ["fees", "pricing", "charges"]):
        return "pricing"
    return "generic"

def extract_name(text: str) -> str:
    m = re.search(r"\b(call(?:ing)?|speaking to|talking to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text)
    return m.group(2) if m else "the customer"

# --- Core logic: generate short guidance -------------------------------------

def build_short_guidance(text: str) -> str:
    lead_type = detect_type(text)
    name = extract_name(text)

    header = f"Here is how you can move the conversation with **{name}** forward:\n"

    if lead_type == "refinance":
        body = (
            "**Key focus:** Home loan refinance and relationship deepening.\n\n"
            "**Ask next:**\n"
            "1. “What is most important for you in this refinance – lower EMI, faster payoff, or flexibility?”\n"
            "2. “What rate and fees has the other bank offered you so far?”\n"
            "3. “Are there any upcoming expenses or plans that might change how much EMI you are comfortable with?”\n"
            "4. “How much of your monthly surplus would you like to keep liquid versus locked in a high‑yield account?”\n"
            "5. “Is there anything in your current experience with us that you want improved before you commit?”"
        )
    elif lead_type == "pricing":
        body = (
            "**Key focus:** Pricing and fee sensitivity.\n\n"
            "**Ask next:**\n"
            "1. “Which specific fees or charges feel unfair or unclear to you?”\n"
            "2. “How are you comparing offers between banks – total cost over time, or just headline rate?”\n"
            "3. “If we could simplify or reduce certain fees, which ones would matter most?”\n"
            "4. “Apart from pricing, what else will influence your decision to stay with us?”\n"
            "5. “Would you like a simple one‑page comparison you can review after this call?”"
        )
    elif lead_type == "sme_wc":
        body = (
            "**Key focus:** SME working capital and collections.\n\n"
            "**Ask next:**\n"
            "1. “For your new customers, how many days on average do they take to pay you?”\n"
            "2. “Where do you usually feel the tightest cash‑flow gap in the month?”\n"
            "3. “Do you currently offer early‑payment discounts or use any collections tools?”\n"
            "4. “What would a comfortable working‑capital limit look like for your next 12 months of growth?”\n"
            "5. “How do you prefer to review these numbers – on a simple cash‑flow view, or with example scenarios?”"
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

    return header + "\n\n" + body

# --- Chat input --------------------------------------------------------------

user_msg = st.chat_input("Say hello or describe the customer and the upcoming call...")

if user_msg:
    # Show user message
    add_message("user", user_msg)
    with st.chat_message("user"):
        st.markdown(user_msg)

    lower = user_msg.strip().lower()
    greeting_words = ("hi", "hello", "hey", "good morning", "good evening", "good afternoon")

    if any(lower.startswith(g) for g in greeting_words) and len(lower.split()) <= 4:
        response = (
            "Hello. Please tell me who you are calling, what the call is about, "
            "and what you would like to achieve. I will suggest the next five questions to ask."
        )
        with st.chat_message("assistant"):
            st.markdown(response)
        add_message("assistant", response)
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking about the best next questions..."):
                time.sleep(1.0)
                reply = build_short_guidance(user_msg)
            st.markdown(reply)
        add_message("assistant", reply)

# Sidebar tips
with st.sidebar:
    st.subheader("Tips for better guidance")
    st.markdown(
        "- Mention the customer name and type (affluent, SME, etc.).\n"
        "- Say what the call is mainly about (refinance, pricing, working capital, etc.).\n"
        "- State briefly what you want from the call."
    )
