import time
import re
import streamlit as st

st.set_page_config(page_title="Sales Call Prep – Chat Agent", layout="wide")

st.title("💬 Sales Call Preparation – Chat Agent")
st.caption("Chat with the agent to prepare for your next customer conversation.")

# Initialise session state
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
        "You can begin with a brief greeting, and then describe who you are calling "
        "and what you wish to achieve in the conversation."
    )
    add_message("assistant", intro)
    with st.chat_message("assistant"):
        st.markdown(intro)

# --- Simple extraction helpers ------------------------------------------------
def extract_name(text: str) -> str:
    # Look for patterns like "calling John Doe" or "speaking to John Doe"
    m = re.search(r"\b(call(?:ing)?|speaking to|talking to)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", text)
    if m:
        return m.group(2)
    return ""

def detect_segment(text: str) -> str:
    t = text.lower()
    if "sme" in t or "business" in t or "msme" in t or "company" in t:
        return "SME / Business"
    if "priority" in t or "privilege" in t or "premier" in t or "hni" in t:
        return "Priority / HNI"
    if "affluent" in t or "salaried" in t or "salary account" in t:
        return "Affluent / Salaried"
    return "Retail (unspecified)"

def extract_objective(text: str) -> str:
    """
    Look for 'my objective is to ...' or 'I want to ...' or 'I’m calling ... to ...'.
    """
    patterns = [
        r"my objective (?:for this call )?(?:is|’s|is to)\s+(.*)",
        r"i want to\s+(.*)",
        r"i’m calling [^,]+?,?\s*to\s+(.*)",
        r"i am calling [^,]+?,?\s*to\s+(.*)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            phrase = m.group(1).strip().rstrip(".")
            # stop at next sentence if user wrote a lot
            phrase = phrase.split(".")[0]
            if len(phrase) > 140:
                phrase = phrase[:140] + "..."
            return phrase
    return ""

def build_briefing(text: str) -> str:
    t = text.lower()

    name = extract_name(text) or "the customer"
    segment = detect_segment(text)
    objective = extract_objective(text)
    if not objective:
        objective = "conduct a constructive check‑in and agree clear next steps"

    # Rough “last interaction” detection
    last_interaction = ""
    if "last week" in t:
        last_interaction = "You mentioned speaking with them **last week**."
    elif "last month" in t:
        last_interaction = "You mentioned a phone conversation **last month**."
    elif "yesterday" in t:
        last_interaction = "You last spoke with them **yesterday**."
    elif "over the phone" in t or "on phone" in t:
        last_interaction = "You previously spoke with them **over the phone**."

    issues = []
    if any(w in t for w in ["complaint", "issue", "problem", "unhappy", "not happy", "frustrated"]):
        issues.append("There are service or experience issues that should be addressed before offering new products.")
    if any(w in t for w in ["fees", "charges", "rate", "pricing"]):
        issues.append("The customer is sensitive to pricing, fees, or rates – prepare a clear comparison.")
    if any(w in t for w in ["inactive", "dormant", "not using", "low engagement"]):
        issues.append("Engagement appears low; focus on relevance and simplicity rather than many products.")

    opportunities = []
    if any(w in t for w in ["savings", "high‑yield", "high-yield", "deposit", "fd", "surplus", "balance"]):
        opportunities.append("Deepen balances via a high‑yield savings account or short‑term deposit.")
    if any(w in t for w in ["home loan", "mortgage", "refinance", "refi"]):
        opportunities.append("Present 2–3 refinance options with clear rate and fee comparisons.")
    if any(w in t for w in ["travel", "miles", "airline"]):
        opportunities.append("Position a travel rewards credit card aligned to recent spend.")
    if any(w in t for w in ["card spend", "credit card", "card usage"]):
        opportunities.append("Review card limits and benefits; consider an upgrade if usage is high.")
    if any(w in t for w in ["salary", "payroll"]):
        opportunities.append("Anchor the salary account with auto‑debits, SIPs, and goal‑based savings.")
    if any(w in t for w in ["working capital", "wc", "cash flow", "invoice", "receivable"]):
        opportunities.append("Discuss working‑capital enhancement and receivables/collections solutions.")

    if not opportunities:
        opportunities.append("Use this call mainly for discovery and service; introduce solutions only where there is a clear fit.")
    if not issues:
        issues.append("No strong risk signals mentioned, but still open with a quick satisfaction check.")

    briefing = f"""\
**Who you are calling**

- Customer: **{name}**  
- Segment (inferred): **{segment}**  
- Your stated objective: **{objective}**

{last_interaction or ''}

**How to open the call**

- Greet **{name}** by name and confirm that now is a good time to speak.  
- Briefly reference the last interaction or current context in simple language.  
- Set expectations: *“By the end of this call, I would like us to be clear on **{objective}**.”*

**Points to clarify early**

- Ask how {name} feels about the relationship and any recent experiences with the bank.  
- Confirm whether there were any issues with digital channels, branches, or pricing.  
- Check upcoming plans: large expenses, business milestones, travel, or life events.

**Key opportunity angles for this conversation**

- """ + "\n- ".join(opportunities) + """

**Risk and retention notes**

- """ + "\n- ".join(issues) + """

**Suggested call flow**

1. Warm up and confirm agenda  
   - Thank {name} for their time and confirm they are comfortable discussing **{objective}** today.  

2. Close the loop on past items  
   - Bring up known promises or issues from your notes and clearly confirm what has been completed and what is pending.  

3. Explore needs and constraints  
   - Ask about balances, cash‑flow patterns, major spends, or business pipeline (as relevant).  
   - Understand comfort with current limits, pricing, and digital tools.  

4. Position one or two solutions  
   - Connect the most relevant opportunity from above to what {name} has shared.  
   - Keep the explanation simple and offer to send a concise follow‑up summary instead of going into excessive detail on the call.  

5. Close with next steps  
   - Summarise decisions made, documents required, and the exact follow‑up time and channel.

**Editable post‑call note (draft)**  

"Spoke with {name} regarding **{objective}**. Reviewed prior interactions and confirmed current satisfaction. Explored near‑term goals and constraints, then discussed the most relevant solutions from the above list. Agreed clear next steps and a follow‑up plan."
"""
    return briefing

# --- Chat input --------------------------------------------------------------
user_msg = st.chat_input("Say hello or describe the customer and the upcoming call...")

if user_msg:
    # Show user message
    add_message("user", user_msg)
    with st.chat_message("user"):
        st.markdown(user_msg)

    lower = user_msg.strip().lower()
    greeting_words = ("hi", "hello", "hey", "good morning", "good evening", "good afternoon")

    # 1) Greeting-only handling
    if any(lower.startswith(g) for g in greeting_words) and len(lower.split()) <= 4:
        response = (
            "Hello. I am ready to assist with your preparation.\n\n"
            "Please describe who you are calling, how long they have banked with you, "
            "and what you wish to accomplish in the call."
        )
        with st.chat_message("assistant"):
            st.markdown(response)
        add_message("assistant", response)

    else:
        # 2) Normal prep flow
        with st.chat_message("assistant"):
            with st.spinner("Analysing the context and preparing your call plan..."):
                time.sleep(1.2)  # cosmetic delay
                reply = build_briefing(user_msg)
            st.markdown(reply)
        add_message("assistant", reply)

# Sidebar help
with st.sidebar:
    st.subheader("Tips for effective inputs")
    st.markdown(
        "- Include the customer name and type (affluent, SME, priority, etc.).\n"
        "- Mention the last interaction and any promises or issues.\n"
        "- Describe recent behaviour (balances, spends, new products).\n"
        "- State clearly what you hope to achieve in this call."
    )
