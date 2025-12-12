import streamlit as st

st.set_page_config(page_title="Sales Call Prep – Chat Agent", layout="wide")

st.title("💬 Sales Call Preparation – Chat Agent")
st.caption("Chat with the agent to prepare for your next customer conversation.")

# Initialize chat history & state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context" not in st.session_state:
    st.session_state.context = {}
if "phase" not in st.session_state:
    st.session_state.phase = "intro"  # intro -> gather -> briefing

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Initial assistant message
if st.session_state.phase == "intro" and not st.session_state.messages:
    intro = (
        "Hi, I'm your Sales Call Prep Agent.\n\n"
        "Tell me about the customer and your upcoming call. "
        "You can paste CRM notes or just describe the situation in your own words.\n\n"
        "For example: segment, last interaction, any promises you made, recent behaviour, "
        "and what you want to achieve in this call."
    )
    add_message("assistant", intro)

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
    # Add user message
    add_message("user", user_msg)

    # Accumulate context (multi-turn)
    existing = st.session_state.context.get("raw", "")
    combined = (existing + "\n" + user_msg).strip()
    st.session_state.context["raw"] = combined

    # Move phase to briefing once we have enough context
    if len(combined) < 40:
        followup = (
            "Got it. Can you share a bit more detail about:\n\n"
            "- When you last interacted and through which channel?\n"
            "- Any promises you made or issues raised?\n"
            "- Any recent changes in balances, spends, or behaviour?"
        )
        add_message("assistant", followup)
        st.session_state.phase = "gather"
    else:
        briefing = build_briefing(combined)
        add_message("assistant", briefing)
        st.session_state.phase = "briefing"

# Optional: small sidebar hints
with st.sidebar:
    st.subheader("How to use this")
    st.markdown(
        "- Paste CRM notes or type freely about the customer.\n"
        "- You can send multiple messages; the agent will combine them.\n"
        "- Once detailed enough, it generates a full call plan and note."
    )
