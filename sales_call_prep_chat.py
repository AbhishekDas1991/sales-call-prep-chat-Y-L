import time
import streamlit as st

st.set_page_config(page_title="Sales Call Prep – Chat Agent", layout="wide")

st.title("💬 Sales Call Preparation – Chat Agent")
st.caption("Chat with the agent to prepare for your next customer conversation.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Initial assistant message
if not st.session_state.messages:
    intro = (
        "Hi, I'm your Sales Call Prep Agent.\n\n"
        "Describe the customer and your upcoming call in your own words.\n"
        "Mention segment, last interaction, any promises or issues, recent behaviour,\n"
        "and what you want to achieve in this call."
    )
    add_message("assistant", intro)
    with st.chat_message("assistant"):
        st.markdown(intro)

def build_briefing(ctx_text: str) -> str:
    text = ctx_text.lower()

    opportunities = []
    risk_flags = []

    # Simple heuristics for opportunities
    if "savings" in text or "fd" in text or "deposit" in text or "balance" in text:
        opportunities.append("Deepen balances via high-yield savings or term deposits.")
    if "home loan" in text or "mortgage" in text or "refinance" in text:
        opportunities.append("Explore home loan refinance, top-up, or balance transfer.")
    if "travel" in text or "miles" in text or "airline" in text:
        opportunities.append("Position a travel rewards credit card or travel bundle.")
    if "salary" in text or "payroll" in text or "salary account" in text:
        opportunities.append("Anchor salary account: auto-debits, SIPs, goals, and linked card.")
    if "business" in text or "sme" in text or "msme" in text:
        opportunities.append("Discuss working capital, term loans, and collections solutions.")
    if "investment" in text or "mf" in text or "mutual fund" in text or "sip" in text:
        opportunities.append("Introduce simple goal-based investment or SIP plan.")
    if "insurance" in text or "protection" in text or "risk" in text:
        opportunities.append("Check for basic protection (life, health, credit shield).")

    # Simple heuristics for risks / retention
    if "unhappy" in text or "complaint" in text or "issue" in text or "churn" in text:
        risk_flags.append("Customer may be at retention risk; fix service issues before pitching products.")
    if "rate" in text or "charges" in text or "fees" in text:
        risk_flags.append("Sensitive to pricing; be ready with a clear, transparent explanation and options.")
    if "inactive" in text or "dormant" in text or "not using" in text:
        risk_flags.append("Low engagement; focus on relevance and simplicity, not number of products.")

    if not opportunities:
        opportunities.append("Use this call mainly for discovery and service; introduce solutions only if the customer opens the door.")
    if not risk_flags:
        risk_flags.append("No explicit risk signals mentioned; still check for pain points early in the call.")

    briefing = f"""\
**Your input (condensed)**  
{ctx_text}

**Call objective (suggested)**  
- Strengthen the relationship, close open loops from previous interactions, and agree 1–2 concrete next steps.

**Suggested call structure**

1. Warm up and context  
   - Thank the customer for their time and reference the last interaction or lifecycle event.  
   - Confirm how much time they have today and what they’d like to get out of the conversation.

2. Close the loop on past items  
   - Revisit any promises, service issues, or pending documents mentioned earlier.  
   - Clearly confirm what has been resolved and what is still in progress.

3. Understand current situation and goals  
   - Ask about upcoming expenses, life events, or business milestones.  
   - Check comfort with current products, limits, pricing, and digital channels.  
   - Explore how they prefer to interact with the bank (RM, branch, app, WhatsApp, etc.).

4. Position relevant solutions  
   - Connect 1–2 specific solutions to expressed needs (not generic product pitching).  
   - Offer to share a concise follow-up summary or illustration instead of overloading in one call.

5. Close with clear next steps  
   - Confirm agreed actions, documents needed, and exact follow-up time/channel.

**Opportunity angles for this call**

- """ + "\n- ".join(opportunities) + """

**Risk / retention notes**

- """ + "\n- ".join(risk_flags) + """

**Editable post-call note (draft)**  

"Spoke with customer to review current relationship and upcoming needs. Revisited previous discussions and any open items, and confirmed resolution status. Explored goals and comfort with existing products and pricing, then positioned relevant solutions where there was clear fit. Agreed on specific next steps, documents, and follow-up date/channel."
"""
    return briefing

# Chat input at bottom
user_msg = st.chat_input("Describe the customer and the upcoming call...")

if user_msg:
    # Show user message
    add_message("user", user_msg)
    with st.chat_message("user"):
        st.markdown(user_msg)

    # Simulate thinking with spinner + short delay
    with st.chat_message("assistant"):
        with st.spinner("Preparing your call briefing..."):
            time.sleep(1.5)  # purely cosmetic delay
            reply = build_briefing(user_msg)
        st.markdown(reply)
    add_message("assistant", reply)

# Sidebar help
with st.sidebar:
    st.subheader("How to use this")
    st.markdown(
        "- Type the customer and call context in your own words.\n"
        "- Each message gets its own briefing.\n"
        "- Start a fresh chat if you switch to a different customer."
    )
