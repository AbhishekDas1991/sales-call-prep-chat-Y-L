import time
import re
import streamlit as st

st.set_page_config(page_title="Sales Call Prep – Chat Agent", layout="wide")

st.title("💬 Sales Call Preparation – Chat Agent")
st.caption("Chat with the agent to prepare for your next customer conversation.")

# Initialise session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "need_basics" not in st.session_state:
    st.session_state.need_basics = True

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# First message
if not st.session_state.messages:
    intro = (
        "Hi, I'm your Sales Call Prep Agent. 👋\n\n"
        "Start with a quick greeting and tell me who you’re calling and why.\n"
        "Example: *“Hi, I’m speaking to John Doe, an SME client, about increasing his working capital limit.”*"
    )
    add_message("assistant", intro)
    with st.chat_message("assistant"):
        st.markdown(intro)

# --- Simple extraction helpers ------------------------------------------------
def extract_name(text: str) -> str:
    # crude pattern: "to <Name>," or "with <Name>,"
    m = re.search(r"\b(to|with)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", text)
    if m:
        return m.group(2)
    return ""

def detect_segment(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["sme", "business", "msme", "firm", "company"]):
        return "SME / Business"
    if any(w in t for w in ["priority", "privilege", "premier", "hni"]):
        return "Priority / HNI"
    if any(w in t for w in ["student", "young", "salary", "professional"]):
        return "Affluent / salaried"
    return "Retail (unspecified)"

def extract_objective(text: str) -> str:
    m = re.search(r"\b(to|for)\s+([^.]+)", text, re.IGNORECASE)
    if m:
        phrase = m.group(2).strip()
        # trim long rambling objectives
        if len(phrase) > 120:
            phrase = phrase[:120] + "..."
        return phrase
    return ""

def build_briefing(text: str) -> str:
    t = text.lower()

    name = extract_name(text)
    segment = detect_segment(text)
    objective = extract_objective(text) or "have a constructive check‑in and agree clear next steps"

    # rough “last interaction” and “issues” detection
    last_interaction = ""
    if "last week" in t or "week" in t:
        last_interaction = "You mentioned speaking with them about a week ago."
    elif "last month" in t or "month" in t:
        last_interaction = "You mentioned a conversation around last month."
    elif "yesterday" in t:
        last_interaction = "You last spoke with them yesterday."

    issues = []
    if any(w in t for w in ["complaint", "issue", "problem", "unhappy", "not happy", "frustrated"]):
        issues.append("There are service or experience issues that must be addressed before selling.")
    if any(w in t for w in ["fees", "charges", "rate", "pricing"]):
        issues.append("Customer is sensitive to pricing, fees, or rates.")
    if any(w in t for w in ["inactive", "dormant", "not using", "low engagement"]):
        issues.append("Engagement is low; focus on relevance and simplicity.")

    opportunities = []
    if any(w in t for w in ["savings", "deposit", "fd", "surplus", "balance"]):
        opportunities.append("Deepen balances via high‑yield savings or term deposits.")
    if any(w in t for w in ["home loan", "mortgage", "refinance", "refi"]):
        opportunities.append("Explore home loan refinance, top‑up, or balance transfer.")
    if any(w in t for w in ["travel", "miles", "airline"]):
        opportunities.append("Position a travel rewards credit card or travel bundle.")
    if any(w in t for w in ["card spend", "credit card", "card usage"]):
        opportunities.append("Review existing card limit/benefits and consider an upgrade or second card if relevant.")
    if any(w in t for w in ["salary", "payroll"]):
        opportunities.append("Anchor salary account with auto‑debits, SIPs, and linked card.")
    if any(w in t for w in ["working capital", "wc", "cash flow", "invoice", "receivable"]):
        opportunities.append("Discuss working capital enhancement and better collections/receivables solutions.")
    if any(w in t for w in ["investment", "mf", "mutual fund", "sip", "portfolio"]):
        opportunities.append("Introduce a goal‑based investment or review existing portfolio.")
    if any(w in t for w in ["insurance", "protection", "cover"]):
        opportunities.append("Check for basic protection needs (life, health, credit shield).")

    if not opportunities:
        opportunities.append("Use this call mainly for discovery and service; introduce solutions only where there is a clear fit.")
    if not issues:
        issues.append("No strong risk signals mentioned, but still open with a quick health‑check on satisfaction.")

    display_name = name if name else "the customer"

    briefing = f"""\
**Who you’re calling**

- Customer: **{display_name}**  
- Segment (inferred): **{segment}**  
- Your stated objective: **{objective}**

{last_interaction or ''}

**How to open the call**

- Greet {display_name} by name and confirm you have a few minutes to talk.  
- Briefly reference the last touchpoint or current context in their words.  
- Set expectations: *“By the end of this call, I’d like us to be clear on {objective}.”*

**Points to clarify early**

- Ask how they feel about the relationship and any recent experiences with the bank.  
- Confirm if there were any issues with digital channels, branch interactions, or pricing.  
- Check upcoming plans: large expenses, business milestones, travel, or life events.

**Key opportunity angles for this conversation**

- """ + "\n- ".join(opportunities) + """

**Risk / retention notes to keep in mind**

- """ + "\n- ".join(issues) + """

**Suggested call flow**

1. Warm up and confirm agenda  
   - Thank them for their time and confirm they are okay to discuss {objective}.  

2. Close the loop on any past items  
   - Bring up known promises or issues from your notes and explicitly confirm status.  

3. Explore needs and constraints  
   - Ask about cash‑flow pattern, balances, major spends, or business pipeline (as relevant).  
   - Understand comfort with current limits, pricing, and digital tools.  

4. Position 1–2 solutions, only if fit is clear  
   - Connect the most relevant opportunity from above to what they told you.  
   - Keep it simple; offer to send a follow‑up summary rather than deep‑dive everything on this call.  

5. Close with next steps  
   - Summarise decisions made, documents required, and exact follow‑up time/channel.

**Editable post‑call note (draft)**  

"Spoke with {display_name} regarding {objective}. Reviewed any past interactions and clarified current satisfaction. Explored near‑term goals and constraints, then discussed the most relevant solutions from the above list. Agreed next steps and follow‑up plan."
"""
    return briefing

# --- Chat input --------------------------------------------------------------
user_msg = st.chat_input("Say hi or describe the customer and upcoming call...")

if user_msg:
    # Show user message
    add_message("user", user_msg)
    with st.chat_message("user"):
        st.markdown(user_msg)

    lower = user_msg.strip().lower()

    # 1) Greeting-only handling
    greeting_words = ("hi", "hello", "hey", "good morning", "good evening", "good afternoon")
    if any(lower.startswith(g) for g in greeting_words) and len(lower.split()) <= 4:
        response = (
            "Hello! 👋\n\n"
            "Tell me who you’re calling and what the call is about.\n"
            "For example: *“I’m calling **John Doe**, an SME client, to discuss increasing his working capital limit.”*"
        )
        with st.chat_message("assistant"):
            st.markdown(response)
        add_message("assistant", response)

    else:
        # 2) Normal prep flow
        with st.chat_message("assistant"):
            with st.spinner("Thinking through your call..."):
                time.sleep(1.2)
                reply = build_briefing(user_msg)
            st.markdown(reply)
        add_message("assistant", reply)

# Sidebar help
with st.sidebar:
    st.subheader("Tips for better answers")
    st.markdown(
        "- Include the **customer name** and type (affluent, SME, priority, etc.).\n"
        "- Mention **last interaction** and any promises/issues.\n"
        "- Describe **recent behaviour** (balances, spends, new products).\n"
        "- State what you **hope to achieve** in this call."
    )
