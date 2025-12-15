import time
import re
import streamlit as st

# -----------------------------------------------------------------------------
# Page config
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Sales Call Prep – US Mortgage Coach",
    layout="wide",
)

LOGO_URL = "https://www.ylconsulting.com/wp-content/uploads/2024/11/logo.webp"

# -----------------------------------------------------------------------------
# Global styling
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    body {
        background-color: #f5f5f7;
    }
    .block-container {
        padding-top: 2.2rem !important;  /* push content below Streamlit header */
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }

    /* Custom top bar that sits below Streamlit header */
    .top-shell {
        width: 100%;
        display: flex;
        justify-content: center;
        margin-bottom: 0.5rem;
    }
    .top-bar {
        width: 72rem;
        max-width: 96%;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        padding: 0.4rem 1.2rem;
        background: rgba(255,255,255,0.96);
        box-shadow: 0 0 0 1px rgba(15,23,42,0.04), 0 10px 28px rgba(15,23,42,0.12);
        backdrop-filter: blur(8px);
    }

    .top-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #111827;
    }
    .top-subtitle {
        font-size: 0.86rem;
        color: #6b7280;
    }

    .top-center {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1.25rem;
    }
    .top-nav-pill {
        border-radius: 999px;
        padding: 0.4rem 0.9rem;
        font-size: 0.9rem;
        font-weight: 500;
        color: #111827;
        background: #eef2ff;
        border: 1px solid #2563eb;
    }

    /* Left rail (sidebar) */
    section[data-testid="stSidebar"] {
        background: #f9fafb;
        border-right: 1px solid #e5e7eb;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.6rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.0rem !important;
        max-width: 260px !important;
    }

    .yl-logo {
        width: 84px;  /* 3x-ish compared to before */
        margin-bottom: 1.6rem;
    }

    .nav-section-label {
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #9ca3af;
        margin-bottom: 0.45rem;
    }

    .nav-item {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.45rem 0.7rem;
        border-radius: 999px;
        cursor: pointer;
        font-size: 0.9rem;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    .nav-item:hover {
        background: #e5f0ff;
        color: #1d4ed8;
    }
    .nav-icon {
        width: 26px;
        height: 26px;
        border-radius: 999px;
        background: #e0edff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        color: #2563eb;
    }
    .nav-footer {
        margin-top: 1.8rem;
        font-size: 0.8rem;
        color: #9ca3af;
    }

    /* Main area */
    .main-wrapper {
        display: flex;
        justify-content: center;
    }
    .main-card {
        margin-top: 0.4rem;
        background: #ffffff;
        border-radius: 1.25rem;
        padding: 1.75rem 2.0rem 1.3rem 2.0rem;
        box-shadow: 0 12px 35px rgba(15,23,42,0.08);
        width: 72rem;
        max-width: 96%;
    }

    /* Chat input with attach + mic icons */
    div[data-testid="stChatInput"] > div {
        border-radius: 999px !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 6px 18px rgba(15,23,42,0.06);
        background: #ffffff;
        position: relative;
        padding-right: 4.5rem !important;
    }
    .input-icons-right {
        position: absolute;
        right: 1.0rem;
        top: 50%;
        transform: translateY(-50%);
        display: flex;
        align-items: center;
        gap: 0.4rem;
        color: #6b7280;
        font-size: 1.0rem;
    }
    .input-icon-circle {
        width: 28px;
        height: 28px;
        border-radius: 999px;
        border: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #f9fafb;
    }

    /* Typography for chat */
    div[data-testid="stMarkdown"] p {
        font-size: 0.95rem;
        line-height: 1.55;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Custom top bar (center, below Streamlit header)
# -----------------------------------------------------------------------------
st.markdown('<div class="top-shell"><div class="top-bar">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="top-center">
        <div>
            <div class="top-title">US Mortgage Coach</div>
            <div class="top-subtitle">Sales Call Preparation</div>
        </div>
        <div class="top-nav-pill">Guide</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('</div></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "asked_topics" not in st.session_state:
    st.session_state.asked_topics = set()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "lead" not in st.session_state:
    st.session_state.lead = {}

def reset_lead():
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

if not st.session_state.lead:
    reset_lead()

# -----------------------------------------------------------------------------
# Sidebar = left rail (logo + new chat + bell + history + library + more)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f'<img src="{LOGO_URL}" class="yl-logo"/>', unsafe_allow_html=True)

    # New chat + bell like Perplexity
    nc_col1, nc_col2 = st.columns([1, 1])
    with nc_col1:
        new_chat_clicked = st.button("＋ New chat", key="new_chat_sidebar")
    with nc_col2:
        st.markdown(
            """
            <div style="display:flex;align-items:center;justify-content:flex-end;">
              <div class="nav-icon">🔔</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div style="margin-top:1.2rem;" class="nav-section-label">History</div>', unsafe_allow_html=True)
    if st.session_state.chat_history:
        for idx, title in enumerate(st.session_state.chat_history[:10]):
            st.markdown(
                f"""
                <div class="nav-item">
                    <div class="nav-icon">💬</div>
                    <span>{title}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("No previous chats yet.")

    st.markdown('<div style="margin-top:1.2rem;" class="nav-section-label">Library</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="nav-item">
            <div class="nav-icon">📘</div>
            <span>Library</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div style="margin-top:1.2rem;" class="nav-section-label">More</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="nav-item">
            <div class="nav-icon">⋯</div>
            <span>More</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-footer">US Mortgage Coach – Internal RM Tool</div>', unsafe_allow_html=True)

# New chat behaviour
if new_chat_clicked:
    if st.session_state.messages:
        first_user = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "New chat")
        st.session_state.chat_history.insert(0, first_user[:48])
    st.session_state.messages = []
    st.session_state.asked_topics = set()
    reset_lead()

# -----------------------------------------------------------------------------
# Main card
# -----------------------------------------------------------------------------
st.markdown('<div class="main-wrapper"><div class="main-card">', unsafe_allow_html=True)

st.markdown("### 💬 Sales Call Preparation – US Mortgage Coach")
st.caption("One refinance lead at a time. Short RM notes in, clear next questions out.")

RATE_FLOOR = 6.0  # percent

def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if not st.session_state.messages:
    intro = (
        "Good day. This assistant helps you prepare for a **US mortgage refinance** call.\n\n"
        "Tell me who you are calling and that it is a refi, for example:\n"
        "`Mary Smith in California, refi on primary home`.\n\n"
        "As you learn facts, drop in short notes like `rate 7.8 pay 3100`, "
        "`bal 410k term 19 yrs`, `dep 65k surplus 1800 travel 900`, "
        "`offer 6.9 competitor 7.1 fee conscious`. Type **summary** any time for a call plan.\n\n"
        ":red[Note: internal rate floor is **6.00%**. Do not position offers below this.]"
    )
    add_message("assistant", intro)
    with st.chat_message("assistant"):
        st.markdown(intro)

# -----------------------------------------------------------------------------
# Business logic helpers (same as before)
# -----------------------------------------------------------------------------
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

    m_state = re.search(r"\b(in|from)\s+([A-Z][a-z]+)", text)
    if m_state and not lead["state"]:
        lead["state"] = m_state.group(2)

    seg = detect_segment(text)
    if seg and not lead["segment"]:
        lead["segment"] = seg

    low = text.lower()
    if any(w in low for w in ["refinance", "refi", "mortgage"]):
        if not lead["objective"]:
            lead["objective"] = "refinance existing mortgage and improve cash flow"
    if any(w in low for w in ["fees", "pricing", "closing costs", "points", "fee conscious", "fee sensitive"]):
        lead["pricing_concern"] = True
    if any(w in low for w in ["college", "education", "tuition", "daughter", "son"]):
        lead["big_goal"] = "college / education funding"

def parse_structured_short_input(text: str):
    lead = st.session_state.lead
    t = text.lower()

    m = re.search(r"tenure\s+([0-9.,k]+)", t)
    if m:
        n = parse_us_number(m.group(1))
        if n:
            lead["tenure_years"] = n

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

    m = re.search(r"term\s+([0-9.,k]+)", t)
    if m:
        n = parse_us_number(m.group(1))
        if n:
            lead["remaining_term_years"] = n

    m = re.search(r"(bal|balance)\s+([0-9.,k]+)", t)
    if m:
        b = parse_us_number(m.group(2))
        if b:
            lead["remaining_balance"] = b

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

def infer_stage(lead) -> int:
    if lead["current_rate"] is None or lead["current_payment"] is None or lead["remaining_balance"] is None:
        return 1
    if (lead["monthly_surplus"] is None or lead["savings_balance"] is None) and not lead["pricing_concern"]:
        return 2
    if lead["pricing_concern"] and (lead["our_rate"] is None or lead["competitor_rate"] is None):
        return 3
    if lead["big_goal"] is None:
        return 4
    return 5

def build_guidance(text: str) -> str:
    lead = st.session_state.lead
    update_lead_from_free_text(text)
    parse_structured_short_input(text)

    name = lead["name"] or "the customer"
    state = f" in {lead['state']}" if lead["state"] else ""
    stage = infer_stage(lead)
    asked = st.session_state.asked_topics

    lines: list[str] = []
    all_questions = []

    if stage == 1:
        if "balance_term" not in asked:
            all_questions.append(("balance_term", "About how much do you still owe and how many years are left on the mortgage?"))
        if "payment_amount" not in asked:
            all_questions.append(("payment_amount", "What is your current monthly mortgage payment (principal + interest)?"))
        if "current_rate" not in asked:
            all_questions.append(("current_rate_q", "Do you know your current interest rate, even roughly?"))
        if "stay_horizon" not in asked:
            all_questions.append(("stay_horizon", "How long do you see yourself staying in this home?"))
        if "refi_reason" not in asked:
            all_questions.append(("refi_reason", "What made you start thinking about refinancing right now?"))
    elif stage == 2:
        if "payment_comfort" not in asked:
            all_questions.append(("payment_comfort", "Does your current payment ever force you to cut back on other things in the month?"))
        if "surplus" not in asked:
            all_questions.append(("surplus", "After the mortgage and bills, about how much cash is usually left over each month?"))
        if "deposits" not in asked:
            all_questions.append(("deposits", "Roughly how much do you keep across checking and savings with us today?"))
        if "shorten_vs_free_cash" not in asked:
            all_questions.append(("shorten_vs_free_cash", "If we reduce your payment, would you rather free up cash or shorten the time to pay off the home?"))
        if "upcoming_expenses" not in asked:
            all_questions.append(("upcoming_expenses", "Are there any large expenses coming up we should factor in?"))
    elif stage == 3:
        if "fee_concern_detail" not in asked:
            all_questions.append(("fee_concern_detail", "Which specific fees or closing costs are you most concerned about?"))
        if "competitor_detail" not in asked:
            all_questions.append(("competitor_detail", "What has the other lender offered you so far in terms of rate and fees?"))
        if "compare_focus" not in asked:
            all_questions.append(("compare_focus", "Over the next 5–7 years, what will you compare first – monthly payment, APR, or total cost?"))
        if "cash_vs_payment" not in asked:
            all_questions.append(("cash_vs_payment", "Would you prefer lower cash to close or the lowest possible payment if we have to trade off?"))
        if "if_we_beat_comp" not in asked:
            all_questions.append(("if_we_beat_comp", "If our offer clearly beats the other one, are you comfortable moving ahead with us?"))
    elif stage == 4:
        if "goals_general" not in asked:
            all_questions.append(("goals_general", "What big goals do you have over the next 3–5 years, like college or renovations?"))
        if "liquidity_vs_return" not in asked:
            all_questions.append(("liquidity_vs_return", "For those goals, do you value liquidity more, or are you open to locking some money away for better returns?"))
        if "goal_monthly_commit" not in asked:
            all_questions.append(("goal_monthly_commit", "Out of what is left each month, how much would you be comfortable committing toward those goals?"))
        if "goal_bucket" not in asked:
            all_questions.append(("goal_bucket", "Would a separate account or bucket for that goal help you stay on track?"))
        if "goal_importance" not in asked:
            all_questions.append(("goal_importance", "How important is it that the refinance structure directly supports that goal?"))
    else:
        if "ready_to_move" not in asked:
            all_questions.append(("ready_to_move", "If the numbers look good, are you comfortable moving forward with the refinance today?"))
        if "deal_stoppers" not in asked:
            all_questions.append(("deal_stoppers", "Is there anything that would stop you from saying yes if we meet your expectations on rate and fees?"))
        if "comparison_format" not in asked:
            all_questions.append(("comparison_format", "How would you like to see the comparison – side‑by‑side with your current loan and the other offer?"))
        if "card_timing" not in asked and lead["travel_spend"] is not None:
            all_questions.append(("card_timing", "Do you want to decide on any card or banking changes now, or keep that for a quick follow‑up?"))
        if "delivery_pref" not in asked:
            all_questions.append(("delivery_pref", "What is the best way for me to send you the final numbers and next steps?"))

    for topic, _ in all_questions:
        asked.add(topic)

    lines.append(f"**Ask {name}{state} now:**")
    for i, (_, q) in enumerate(all_questions[:5], start=1):
        if i <= 2:
            lines.append(f"{i}. **\"{q}\"**")
        else:
            lines.append(f"{i}. \"{q}\"")

    if not all_questions:
        lines.append("1. **\"Is there anything else on your mind before we look at the numbers?\"**")

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
        rate_txt = f"{lead['our_rate']:.2f}%"
        if lead["our_rate"] < RATE_FLOOR:
            snapshot.append(f"- :red[Working offer {rate_txt} is **below** floor {RATE_FLOOR:.2f}%. Do **not** go this low.]")
        else:
            snapshot.append(f"- Your working offer: **{rate_txt}** (subject to approval).")
    else:
        snapshot.append(f"- Pricing guardrail: :red[do not quote below **{RATE_FLOOR:.2f}%**].")
    if lead["competitor_rate"] is not None:
        snapshot.append(f"- Competitor mentioned: ~**{lead['competitor_rate']:.2f}%**.")
    if lead["savings_balance"] is not None:
        snapshot.append(f"- Deposits: ~**${lead['savings_balance']:.0f}** with your bank.")
    if lead["monthly_surplus"] is not None:
        snapshot.append(f"- Monthly surplus: ~**${lead['monthly_surplus']:.0f}** after bills.")
    if lead["travel_spend"] is not None:
        snapshot.append(f"- Travel / card spend: ~**${lead['travel_spend']:.0f}/mo**.")
    if lead["pricing_concern"]:
        snapshot.append("- Customer is **rate‑ and fee‑sensitive**.")
    if lead["big_goal"]:
        snapshot.append("- Long‑term goal discussed: **college / education in ~3–4 years**.")

    if not snapshot:
        snapshot.append("- Key numbers not captured yet.")

    lines.extend(snapshot)

    need = []
    if lead["current_rate"] is None or lead["current_payment"] is None or lead["remaining_balance"] is None:
        need.append("basic loan details (rate, payment, remaining balance / term).")
    if lead["savings_balance"] is None or lead["monthly_surplus"] is None:
        need.append("deposits and typical monthly surplus.")
    if lead["pricing_concern"] and (lead["our_rate"] is None or lead["competitor_rate"] is None):
        need.append("your working offer rate and any competitor quote.")
    if lead["big_goal"] is None and infer_stage(lead) >= 3:
        need.append("any major life goals (college, renovation, etc.).")

    if need:
        lines.append("")
        lines.append("**Your internal checklist:**")
        for n in need:
            lines.append(f"- {n}")

    lines.append("")
    lines.append("Type `summary` any time for a consolidated call plan.")
    return "\n".join(lines)

def build_summary() -> str:
    lead = st.session_state.lead
    name = lead["name"] or "the customer"
    state = f" in {lead['state']}" if lead["state"] else ""
    parts: list[str] = []

    parts.append(f"**Call summary – {name}{state}**\n")

    if lead["tenure_years"] is not None:
        parts.append(f"- Relationship: **{lead['tenure_years']:.0f} years** with your bank.")
    if lead["current_rate"] is not None:
        pay_txt = f"${lead['current_payment']:.0f}/mo" if lead["current_payment"] else "payment not captured"
        parts.append(f"- Current mortgage: **{lead['current_rate']:.2f}%**, {pay_txt}.")
    if lead["remaining_balance"] is not None:
        term_txt = f"{lead['remaining_term_years']:.0f} yrs left" if lead["remaining_term_years"] else "term not captured"
        parts.append(f"- Remaining balance: **${lead['remaining_balance']:.0f}**, {term_txt}.")
    if lead["our_rate"] is not None:
        txt = f"{lead['our_rate']:.2f}%"
        if lead["our_rate"] < RATE_FLOOR:
            parts.append(f"- :red[Offer {txt} is **below** internal floor **{RATE_FLOOR:.2f}%**. Adjust pricing upward before quoting.]")
        else:
            parts.append(f"- Working offer: **{txt}** (subject to underwriting).")
    else:
        parts.append(f"- Pricing guardrail: :red[do not go below **{RATE_FLOOR:.2f}%** on rate.]")
    if lead["competitor_rate"] is not None:
        parts.append(f"- Competitor in play: ~**{lead['competitor_rate']:.2f}%**.")
    if lead["savings_balance"] is not None:
        parts.append(f"- Deposits: around **${lead['savings_balance']:.0f}** on your books.")
    if lead["monthly_surplus"] is not None:
        parts.append(f"- Monthly surplus: roughly **${lead['monthly_surplus']:.0f}** after bills.")
    if lead["travel_spend"] is not None:
        parts.append(f"- Card / travel spend: about **${lead['travel_spend']:.0f} per month**.")
    if lead["pricing_concern"]:
        parts.append("- Borrower is strongly **price‑ and fee‑sensitive**; structure and cash to close matter.")
    if lead["big_goal"]:
        parts.append("- Stated goal: **college / education saving in the next few years**, wants liquidity with some growth.")
    if lead["objective"]:
        parts.append(f"- Your internal goal: **{lead['objective']}**.")

    parts.append("")
    parts.append("**Key insights**")
    if lead["current_rate"] and lead["our_rate"] and lead["our_rate"] >= RATE_FLOOR:
        rate_delta = lead["current_rate"] - lead["our_rate"]
        if rate_delta > 0:
            parts.append(
                f"- You have roughly a **{rate_delta:.2f}% rate improvement** above floor {RATE_FLOOR:.2f}%. "
                "Focus on what that does to payment and interest over the first 5–7 years."
            )
    if lead["monthly_surplus"]:
        parts.append("- Surplus each month allows you to propose an automatic transfer into a goal bucket without stressing cash flow.")
    if lead["pricing_concern"]:
        parts.append("- A transparent fee breakdown and breakeven view will matter more than chasing tiny extra rate cuts.")
    if lead["travel_spend"]:
        parts.append("- Card spend is large enough that a targeted rewards card can be a natural follow‑up once the refi is agreed.")

    parts.append("")
    parts.append("**How to steer the call**")
    parts.append("- Confirm remaining term, stay‑in‑home horizon, and payment comfort one more time.")
    parts.append("- Present side‑by‑side: today vs your offer vs competitor (payment, APR, cash to close, breakeven years).")
    parts.append("- Tie savings from the refi to a specific monthly amount into their college or remodel fund.")
    if lead["travel_spend"] is not None:
        parts.append("- Offer to review card options only after they are comfortable with the refinance numbers.")
    parts.append("- Finish with a clear checklist of documents, rate‑lock expectations, and how/when you will send final numbers.")
    return "\n".join(parts)

# -----------------------------------------------------------------------------
# Chat input (with visual attach/mic icons)
# -----------------------------------------------------------------------------
user_msg = st.chat_input(
    "Short notes only (e.g., 'Mary Smith CA refi', 'rate 7.8 pay 3100', 'bal 410k term 19 yrs', or 'summary')..."
)

st.markdown(
    """
    <div class="input-icons-right">
        <div class="input-icon-circle">📎</div>
        <div class="input-icon-circle">🎤</div>
    </div>
    """,
    unsafe_allow_html=True,
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

st.markdown('</div></div>', unsafe_allow_html=True)
