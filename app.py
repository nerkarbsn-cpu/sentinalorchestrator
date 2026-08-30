"""
================================================================================
 SENTINEL ORCHESTRATOR — AI Governance & Shadow-AI Risk Management Platform
================================================================================
A single-file Streamlit MVP that demonstrates the core "Sentinel Orchestrator"
concept:

    1) Falcon Risk Dashboard    -> visualize data classification & shadow AI risk
    2) Swarm Agentic Simulator  -> simulate a governed multi-step AI agent run
    3) Governance Playbook      -> a mock keyword-based compliance assistant
    4) Bottleneck Detection     -> simulate workflow handoff failures/delays

No external API keys are required. All "AI" behavior (agent outputs, risk
scores, compliance answers) is SIMULATED using Python's `random` and simple
string/keyword logic, so the app runs instantly, offline, with no cost.

Run with:  streamlit run app.py
================================================================================
"""

import random
import time
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==============================================================================
# SECTION 0: PAGE CONFIG & GLOBAL STYLING
# ==============================================================================
st.set_page_config(
    page_title="Sentinel Orchestrator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Light custom CSS for a "modern dashboard" feel on top of Streamlit's defaults.
st.markdown(
    """
    <style>
        .main { background-color: #0e1117; }
        div[data-testid="stMetric"] {
            background-color: rgba(38, 39, 48, 0.6);
            border: 1px solid #30333d;
            border-radius: 10px;
            padding: 15px 15px 5px 15px;
        }
        .sentinel-header {
            font-size: 2.1rem;
            font-weight: 700;
            margin-bottom: 0px;
        }
        .sentinel-subheader {
            color: #9aa0aa;
            font-size: 1rem;
            margin-top: 0px;
            margin-bottom: 1.5rem;
        }
        .risk-badge-pass {
            background-color: #1e4620; color: #6fe884; padding: 4px 12px;
            border-radius: 20px; font-weight: 600; display: inline-block;
        }
        .risk-badge-fail {
            background-color: #4a1e1e; color: #ff6b6b; padding: 4px 12px;
            border-radius: 20px; font-weight: 600; display: inline-block;
        }
        .playbook-answer {
            background-color: rgba(38, 39, 48, 0.6);
            border-left: 4px solid #4c8bf5;
            border-radius: 6px;
            padding: 14px 18px;
            margin-top: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============================================================================
# SECTION 1: MOCK DATA GENERATION
# ------------------------------------------------------------------------------
# In a real product this would come from a data classification scanner (DLP),
# a network/SaaS discovery tool (CASB), and an AI usage telemetry pipeline.
# Here we hard-code realistic-looking mock data so the dashboard has something
# to render immediately, with no backend required.
# ==============================================================================

DEPARTMENTS = ["Marketing", "Engineering", "Legal", "Finance", "HR", "Sales"]

UNSANCTIONED_TOOLS = [
    "ChatGPT (Personal)", "Midjourney", "Character.AI", "Jasper AI",
    "Grammarly Business (unapproved tier)", "Otter.ai", "DeepL Pro",
    "Perplexity AI", "Notion AI (personal workspace)", "Claude (personal account)",
]

# Data Classification breakdown (mocked scan results) — used for the pie chart.
DATA_CLASSIFICATION = {
    "Public": 32,
    "Internal": 41,
    "Sensitive": 19,
    "Restricted": 8,
}

# Shadow AI exposure score (0-100) per department — used for the bar chart.
# Seeded once per session so numbers don't jump around on every rerun.
if "shadow_ai_exposure" not in st.session_state:
    random.seed(42)
    st.session_state.shadow_ai_exposure = {
        dept: random.randint(15, 95) for dept in DEPARTMENTS
    }

if "unsanctioned_tools_detected" not in st.session_state:
    st.session_state.unsanctioned_tools_detected = random.randint(14, 37)

if "handoff_scan" not in st.session_state:
    st.session_state.handoff_scan = None

if "scan_history" not in st.session_state:
    # Simulated 14-day trend of detected shadow AI incidents, for extra flavor.
    base = datetime.now() - timedelta(days=13)
    st.session_state.scan_history = pd.DataFrame(
        {
            "date": [base + timedelta(days=i) for i in range(14)],
            "incidents": [random.randint(2, 14) for _ in range(14)],
        }
    )


# ==============================================================================
# SECTION 2: SIMULATED "AI" LOGIC HELPERS
# ------------------------------------------------------------------------------
# These functions fake the behavior of generative AI / governance engines using
# random.choice, random.randint and basic string templating — NO external API
# calls, NO API keys, and everything resolves instantly.
# ==============================================================================

TASK_TEMPLATES = {
    "Generate Campaign": [
        "Draft campaign concept: '{dept} Momentum Q{q} Launch' targeting mid-funnel prospects "
        "with a 3-touch email + social sequence.",
        "Generated 5 headline variants and 2 CTA options for the {dept} campaign brief.",
        "Proposed budget split: 60% paid social, 25% email, 15% retargeting.",
    ],
    "Summarize Legal Doc": [
        "Summary: The reviewed agreement contains a 12-month auto-renewal clause and a "
        "limitation-of-liability cap at 1x annual contract value.",
        "Key risk flagged: indemnification clause is broader than standard template (Section 8.2).",
        "3 of 14 clauses deviate from the approved legal playbook and are marked for counsel review.",
    ],
    "Draft Customer Email": [
        "Drafted a customer response addressing the billing discrepancy with an apology, "
        "root-cause note, and a goodwill credit offer.",
        "Generated 2 tone variants (formal / friendly) for the {dept} support reply.",
    ],
    "Analyze Financial Report": [
        "Flagged a 14% variance in Q{q} opex vs. forecast, concentrated in vendor spend.",
        "Generated a 4-bullet executive summary of the {dept} quarterly report.",
    ],
    "Screen Resume": [
        "Ranked candidate against role requirements: 78% keyword/skill match.",
        "Generated 3 recommended interview questions based on resume gaps for {dept}.",
    ],
}

PLANNING_MESSAGES = [
    "Parsing task intent and required data scopes...",
    "Identifying department-approved AI model and guardrail policy set...",
    "Checking data classification of referenced inputs...",
]

EXECUTING_MESSAGES = [
    "Invoking sandboxed generation model...",
    "Applying prompt-injection and PII filters...",
    "Synthesizing draft output...",
]

REVIEWING_MESSAGES = [
    "Running output against compliance guardrails...",
    "Scoring hallucination and toxicity risk...",
    "Finalizing audit log entry...",
]


def simulate_agent_run(department: str, task: str, quarter: int) -> dict:
    """Fake a generative-AI agent's output for a given department/task.

    Uses random.choice / random.randint to simulate variability — no network
    calls, no API keys, resolves instantly.
    """
    templates = TASK_TEMPLATES.get(task, ["Task completed with a simulated generic output."])
    output_lines = [t.format(dept=department, q=quarter) for t in templates]

    risk_score = random.randint(1, 100)
    # Guardrail fails more often as risk score climbs, with some randomness.
    guardrail_pass = risk_score < random.randint(55, 80)

    return {
        "output_lines": output_lines,
        "risk_score": risk_score,
        "guardrail_pass": guardrail_pass,
        "model_used": random.choice(
            ["Sentinel-Guarded-GPT (sandboxed)", "Sentinel-Guarded-Claude (sandboxed)", "Sentinel-Local-LLM"]
        ),
        "tokens_used": random.randint(280, 2400),
        "latency_ms": random.randint(340, 2100),
    }


# Governance Playbook: basic keyword -> policy-answer mapping.
# A real system would use retrieval-augmented generation over an actual policy
# corpus; here we simulate it with simple substring matching for the MVP.
PLAYBOOK_RULES = [
    (["data", "pii", "personal information", "customer data"],
     "🔐 **Security:** Any dataset containing personal or customer data must be "
     "encrypted at rest (AES-256) and in transit (TLS 1.2+). Access requires "
     "role-based approval logged in the audit trail."),
    (["contract", "legal", "agreement", "clause"],
     "⚖️ **Legal:** AI-generated summaries of contracts must be reviewed by "
     "in-house counsel before being relied upon. Cite the source clause number "
     "for every AI-derived statement."),
    (["marketing", "campaign", "advertising", "brand"],
     "📣 **Brand & Compliance:** AI-generated marketing copy must pass through "
     "brand-voice review and cannot make unverified claims (e.g., 'clinically "
     "proven') without a substantiation file attached."),
    (["finance", "budget", "revenue", "forecast"],
     "💰 **Finance Controls:** AI outputs touching financial figures are "
     "advisory only. A human financial analyst must sign off before any "
     "AI-derived number is published externally."),
    (["shadow", "unsanctioned", "unapproved tool", "personal account"],
     "🚨 **Shadow AI Policy:** Use of unsanctioned AI tools (personal ChatGPT, "
     "unmanaged browser extensions, etc.) on company data is prohibited under "
     "Policy AI-004. Route requests through the approved Sentinel gateway."),
    (["employee", "hr", "hiring", "resume", "performance review"],
     "🧑‍💼 **HR & Fairness:** AI-assisted hiring or performance decisions "
     "require a documented human-in-the-loop review to mitigate algorithmic "
     "bias, per Policy AI-011."),
    (["vendor", "third party", "third-party", "saas"],
     "🤝 **Vendor Risk:** Any third-party AI vendor must complete the Sentinel "
     "Vendor Risk Questionnaire and sign a Data Processing Addendum (DPA) "
     "before integration."),
    (["retention", "delete", "deletion", "storage"],
     "🗄️ **Data Retention:** AI conversation logs containing sensitive data "
     "are retained for a maximum of 90 days unless subject to a legal hold."),
]

DEFAULT_PLAYBOOK_ANSWER = (
    "🤖 **General Guidance:** No specific policy rule matched this question "
    "directly. As a default control, apply the principle of least privilege, "
    "avoid inputting Restricted or Sensitive-classified data into any "
    "non-sandboxed AI tool, and consult the Governance team for edge cases."
)


# ------------------------------------------------------------------------------
# Bottleneck Detection: a simulated end-to-end workflow, made up of ordered
# stages. A "handoff" is the gap between one stage and the next (e.g. work
# leaving Intake and landing in Requirements Review). In real life, handoffs
# are where work stalls — a task sits in someone's inbox, ownership is
# unclear, or approvals queue up. We simulate that stalling here.
# ------------------------------------------------------------------------------
WORKFLOW_STAGES = [
    "Intake / Request Logged",
    "Requirements Review",
    "Stakeholder Approval",
    "Execution / Build",
    "QA & Guardrail Check",
    "Deployment / Closure",
]

# Plausible-sounding root causes for a stalled handoff, keyed loosely to the
# kind of stage transition. Picked at random per handoff to simulate a
# diagnostic engine without needing a real one.
HANDOFF_ROOT_CAUSES = [
    "No single owner assigned on the receiving side — request sits unclaimed.",
    "Approval queue backlog — reviewer has 3x normal pending volume.",
    "Missing information from upstream stage forces a rework loop.",
    "Manual hand-off (email/spreadsheet) instead of a tracked system step.",
    "Cross-department dependency — receiving team waits on a different team.",
    "Unclear acceptance criteria — receiving stage rejects and sends back.",
    "Reviewer/approver out-of-office with no defined backup.",
    "Tooling gap — no automated notification when the prior stage completes.",
]


def simulate_bottleneck_scan() -> dict:
    """Fake a workflow-mining style bottleneck scan.

    For each handoff between consecutive WORKFLOW_STAGES, simulate:
      - starting volume of work items reaching that stage
      - a % that fail / stall / bounce back at the handoff
      - an average delay (in hours) introduced at that handoff
    Uses random.randint/choice only — no real workflow data required.
    """
    handoffs = []
    volume = 100  # start with 100 simulated work items entering the workflow

    for i in range(len(WORKFLOW_STAGES) - 1):
        from_stage = WORKFLOW_STAGES[i]
        to_stage = WORKFLOW_STAGES[i + 1]

        failure_rate = random.randint(3, 42)  # % of items that stall/bounce here
        avg_delay_hours = random.randint(1, 48)
        items_lost = round(volume * (failure_rate / 100))
        volume_after = max(volume - items_lost, 0)

        handoffs.append(
            {
                "Handoff": f"{from_stage}  →  {to_stage}",
                "From": from_stage,
                "To": to_stage,
                "Items Entering": volume,
                "Failure/Stall Rate (%)": failure_rate,
                "Avg. Delay (hrs)": avg_delay_hours,
                "Items Lost": items_lost,
                "Root Cause": random.choice(HANDOFF_ROOT_CAUSES),
            }
        )
        volume = volume_after

    df = pd.DataFrame(handoffs)
    worst = df.loc[df["Failure/Stall Rate (%)"].idxmax()]

    return {
        "df": df,
        "worst_handoff": worst["Handoff"],
        "worst_rate": worst["Failure/Stall Rate (%)"],
        "worst_cause": worst["Root Cause"],
        "final_volume": volume,
        "total_lost": 100 - volume,
        "scanned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def query_playbook(question: str) -> list:
    """Very small keyword-matching 'compliance assistant'.

    Scans the question for keywords and returns every matching policy rule.
    This deliberately simple approach stands in for a future RAG-based system.
    """
    q = question.lower()
    matches = []
    for keywords, answer in PLAYBOOK_RULES:
        if any(kw in q for kw in keywords):
            matches.append(answer)
    if not matches:
        matches.append(DEFAULT_PLAYBOOK_ANSWER)
    return matches


# ==============================================================================
# SECTION 3: SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.markdown("## 🛡️ Sentinel Orchestrator")
    st.caption("AI Governance Command Center")
    st.divider()

    page = st.radio(
        "Navigate",
        options=[
            "🦅 Falcon Risk Dashboard",
            "🐝 Swarm Agentic Simulator",
            "📖 Governance Playbook",
            "🔗 Bottleneck Detection",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    st.caption("Simulated data — no external API calls.")

    if st.button("🔄 Re-run Simulated Scan", use_container_width=True):
        # Re-seed randomness to produce a "fresh scan" feel without an API.
        random.seed()
        st.session_state.shadow_ai_exposure = {
            dept: random.randint(15, 95) for dept in DEPARTMENTS
        }
        st.session_state.unsanctioned_tools_detected = random.randint(14, 37)
        st.rerun()


# ==============================================================================
# SECTION 4: PAGE 1 — FALCON RISK DASHBOARD
# ==============================================================================
if page == "🦅 Falcon Risk Dashboard":
    st.markdown('<p class="sentinel-header">🦅 Falcon Risk Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sentinel-subheader">Continuous simulated scan of company data '
        "classification and shadow AI exposure across departments.</p>",
        unsafe_allow_html=True,
    )

    # ---- Top metric row ------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Unsanctioned AI Tools Detected",
            st.session_state.unsanctioned_tools_detected,
            delta=f"+{random.randint(1,4)} this week",
            delta_color="inverse",
        )
    with col2:
        avg_exposure = int(sum(st.session_state.shadow_ai_exposure.values()) / len(DEPARTMENTS))
        st.metric("Avg. Shadow AI Exposure Score", f"{avg_exposure}/100",
                   delta=f"{random.choice(['+','-'])}{random.randint(1,7)} pts")
    with col3:
        restricted_pct = DATA_CLASSIFICATION["Restricted"]
        st.metric("Restricted Data Assets", f"{restricted_pct}%",
                   delta=f"-{random.randint(1,3)}% vs last scan", delta_color="normal")
    with col4:
        st.metric("Active Guardrail Policies", "18", delta="+2 new")

    st.divider()

    # ---- Charts row ------------------------------------------------------------
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Data Classification Breakdown")
        pie_df = pd.DataFrame(
            {"Classification": list(DATA_CLASSIFICATION.keys()),
             "Percentage": list(DATA_CLASSIFICATION.values())}
        )
        fig_pie = px.pie(
            pie_df, names="Classification", values="Percentage", hole=0.45,
            color="Classification",
            color_discrete_map={
                "Public": "#4c8bf5", "Internal": "#6fcf97",
                "Sensitive": "#f2c94c", "Restricted": "#eb5757",
            },
        )
        fig_pie.update_traces(textinfo="percent+label")
        fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

    with chart_col2:
        st.subheader("Shadow AI Exposure by Department")
        bar_df = pd.DataFrame(
            {
                "Department": list(st.session_state.shadow_ai_exposure.keys()),
                "Exposure Score": list(st.session_state.shadow_ai_exposure.values()),
            }
        ).sort_values("Exposure Score", ascending=True)
        fig_bar = px.bar(
            bar_df, x="Exposure Score", y="Department", orientation="h",
            color="Exposure Score", color_continuous_scale=["#6fcf97", "#f2c94c", "#eb5757"],
            range_color=[0, 100], text="Exposure Score",
        )
        fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380,
                               coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ---- Trend + tools table row -----------------------------------------------
    trend_col, table_col = st.columns([1.3, 1])

    with trend_col:
        st.subheader("14-Day Shadow AI Incident Trend")
        fig_trend = go.Figure()
        fig_trend.add_trace(
            go.Scatter(
                x=st.session_state.scan_history["date"],
                y=st.session_state.scan_history["incidents"],
                mode="lines+markers", fill="tozeroy",
                line=dict(color="#eb5757", width=2),
            )
        )
        fig_trend.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=320,
                                 xaxis_title=None, yaxis_title="Incidents")
        st.plotly_chart(fig_trend, use_container_width=True)

    with table_col:
        st.subheader("Detected Unsanctioned Tools")
        sample_tools = random.sample(UNSANCTIONED_TOOLS, k=min(6, len(UNSANCTIONED_TOOLS)))
        tools_df = pd.DataFrame(
            {
                "Tool": sample_tools,
                "Department": [random.choice(DEPARTMENTS) for _ in sample_tools],
                "Risk": [random.choice(["🟢 Low", "🟡 Medium", "🔴 High"]) for _ in sample_tools],
            }
        )
        st.dataframe(tools_df, use_container_width=True, hide_index=True, height=320)


# ==============================================================================
# SECTION 5: PAGE 2 — SWARM AGENTIC SIMULATOR
# ==============================================================================
elif page == "🐝 Swarm Agentic Simulator":
    st.markdown('<p class="sentinel-header">🐝 Swarm Agentic Simulator</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sentinel-subheader">Run a governed AI agent against a '
        "department task and watch it move through Planning → Executing → "
        "Reviewing, with a guardrail check on the output.</p>",
        unsafe_allow_html=True,
    )

    with st.form("agent_run_form"):
        col1, col2 = st.columns(2)
        with col1:
            department = st.selectbox("Select Department", DEPARTMENTS)
        with col2:
            task = st.selectbox("Select Task", list(TASK_TEMPLATES.keys()))

        quarter = st.slider("Reporting Quarter", 1, 4, value=random.randint(1, 4))
        run_clicked = st.form_submit_button("▶️ Run Agent", use_container_width=True, type="primary")

    if run_clicked:
        progress_bar = st.progress(0, text="Initializing Sentinel Agent...")
        status_box = st.empty()

        # --- Step 1: Planning -----------------------------------------------
        for i, msg in enumerate(PLANNING_MESSAGES):
            status_box.info(f"**🧭 Planning** — {msg}")
            progress_bar.progress(int((i + 1) / len(PLANNING_MESSAGES) * 30), text="Planning...")
            time.sleep(0.35)

        # --- Step 2: Executing ------------------------------------------------
        for i, msg in enumerate(EXECUTING_MESSAGES):
            status_box.info(f"**⚙️ Executing** — {msg}")
            progress_bar.progress(30 + int((i + 1) / len(EXECUTING_MESSAGES) * 40), text="Executing...")
            time.sleep(0.35)

        # --- Step 3: Reviewing ------------------------------------------------
        for i, msg in enumerate(REVIEWING_MESSAGES):
            status_box.info(f"**🔍 Reviewing** — {msg}")
            progress_bar.progress(70 + int((i + 1) / len(REVIEWING_MESSAGES) * 30), text="Reviewing...")
            time.sleep(0.35)

        progress_bar.progress(100, text="Complete.")
        status_box.empty()

        result = simulate_agent_run(department, task, quarter)

        st.success("Agent run complete.")
        st.divider()

        out_col, meta_col = st.columns([1.6, 1])

        with out_col:
            st.subheader("Simulated Agent Output")
            for line in result["output_lines"]:
                st.write(f"- {line}")

        with meta_col:
            st.subheader("Guardrail Report")

            risk_score = result["risk_score"]
            st.metric("Risk Score", f"{risk_score} / 100")
            st.progress(risk_score / 100)

            if result["guardrail_pass"]:
                st.markdown('<span class="risk-badge-pass">✅ GUARDRAIL: PASS</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="risk-badge-fail">⛔ GUARDRAIL: FAIL</span>', unsafe_allow_html=True)
                st.caption("Output withheld from auto-publish; routed to human reviewer.")

            st.write("")
            st.caption(f"Model: {result['model_used']}")
            st.caption(f"Tokens used: {result['tokens_used']:,}")
            st.caption(f"Latency: {result['latency_ms']} ms")
            st.caption(f"Audit log ID: SENT-{random.randint(100000,999999)}")
    else:
        st.info("Configure the run above and click **Run Agent** to simulate a governed workflow.")


# ==============================================================================
# SECTION 6: PAGE 3 — GOVERNANCE PLAYBOOK
# ==============================================================================
elif page == "📖 Governance Playbook":
    st.markdown('<p class="sentinel-header">📖 Governance Playbook</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sentinel-subheader">Paste a policy question below. A mock '
        "compliance assistant matches keywords against the Sentinel policy "
        "library and returns applicable guardrails.</p>",
        unsafe_allow_html=True,
    )

    example_questions = [
        "Can marketing use AI to write ad copy about our product?",
        "What do we need before sending customer PII to a third-party AI vendor?",
        "Is it okay to summarize a legal contract with ChatGPT?",
        "How long do we retain AI chat logs?",
    ]

    with st.expander("💡 Example questions"):
        for eq in example_questions:
            st.write(f"- {eq}")

    question = st.text_area(
        "Enter your policy question",
        placeholder="e.g. 'Can I use a personal AI tool to summarize a customer contract?'",
        height=120,
    )

    ask_col, clear_col = st.columns([1, 5])
    with ask_col:
        ask_clicked = st.button("🔎 Ask Sentinel", type="primary", use_container_width=True)

    if ask_clicked:
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Matching against governance policy library..."):
                time.sleep(0.6)
                answers = query_playbook(question)

            st.subheader("Sentinel Compliance Guidance")
            for ans in answers:
                st.markdown(f'<div class="playbook-answer">{ans}</div>', unsafe_allow_html=True)
                st.write("")

            st.caption(
                "⚠️ This is a simulated, keyword-based response for MVP demo "
                "purposes only and does not constitute legal advice."
            )

    st.divider()
    st.subheader("📚 Policy Library (Reference)")
    policy_ref = pd.DataFrame(
        {
            "Policy ID": ["AI-001", "AI-002", "AI-004", "AI-007", "AI-011"],
            "Title": [
                "Data Encryption & Classification Handling",
                "Legal Document AI Review Requirement",
                "Shadow AI / Unsanctioned Tool Prohibition",
                "Vendor Risk & DPA Requirement",
                "Human-in-the-Loop for HR Decisions",
            ],
            "Owner": ["Security", "Legal", "IT Governance", "Procurement", "HR"],
            "Last Updated": ["2026-06-01", "2026-05-14", "2026-07-22", "2026-04-30", "2026-06-18"],
        }
    )
    st.dataframe(policy_ref, use_container_width=True, hide_index=True)


# ==============================================================================
# SECTION 7: PAGE 4 — BOTTLENECK DETECTION
# ------------------------------------------------------------------------------
# Simulates a "process mining" style scan: it walks a fixed sequence of
# workflow stages and, for each handoff between two stages, fakes a
# stall/failure rate, an average delay, and a likely root cause. This mirrors
# how real bottleneck-detection tools (e.g. workflow/process mining engines)
# report where work gets stuck — except every number here comes from
# random.randint(), not a real system.
# ==============================================================================
elif page == "🔗 Bottleneck Detection":
    st.markdown('<p class="sentinel-header">🔗 Bottleneck Detection</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sentinel-subheader">Simulates a process-mining scan across a '
        "6-stage workflow, flagging which handoff between stages is failing "
        "or stalling the most, with a likely root cause.</p>",
        unsafe_allow_html=True,
    )

    st.caption(
        "Simulated workflow: " + "  →  ".join(WORKFLOW_STAGES)
    )

    if st.button("🚦 Run Bottleneck Scan", type="primary", use_container_width=False):
        with st.spinner("Analyzing simulated handoff logs across all stages..."):
            time.sleep(0.8)
            st.session_state.handoff_scan = simulate_bottleneck_scan()

    result = st.session_state.handoff_scan

    if result is None:
        st.info("Click **Run Bottleneck Scan** to simulate a workflow handoff analysis.")
    else:
        df = result["df"]

        # ---- Top metric row --------------------------------------------------
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Worst Handoff Stall Rate", f"{result['worst_rate']}%")
        with m2:
            st.metric("Items Lost End-to-End", f"{result['total_lost']} / 100")
        with m3:
            st.metric("Items Completing Workflow", f"{result['final_volume']} / 100")
        with m4:
            st.metric("Handoffs Scanned", len(df))

        st.divider()

        # ---- Funnel chart: volume dropping off stage by stage ----------------
        funnel_col, bar_col = st.columns(2)

        with funnel_col:
            st.subheader("Work Item Funnel (Drop-off by Stage)")
            funnel_stages = WORKFLOW_STAGES
            # Per-stage volume series: entering volume of each stage, ending
            # with the final completed volume after the last handoff.
            funnel_values = [df["Items Entering"].iloc[0]] + \
                [df["Items Entering"].iloc[i] - df["Items Lost"].iloc[i] for i in range(len(df))]
            fig_funnel = go.Figure(
                go.Funnel(
                    y=funnel_stages,
                    x=funnel_values,
                    textinfo="value+percent initial",
                    marker=dict(color=["#4c8bf5", "#6fcf97", "#f2c94c", "#f2994a", "#eb5757", "#9b51e0"]),
                )
            )
            fig_funnel.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380)
            st.plotly_chart(fig_funnel, use_container_width=True)

        with bar_col:
            st.subheader("Stall/Failure Rate per Handoff")
            fig_bar = px.bar(
                df.sort_values("Failure/Stall Rate (%)"),
                x="Failure/Stall Rate (%)", y="Handoff", orientation="h",
                color="Failure/Stall Rate (%)",
                color_continuous_scale=["#6fcf97", "#f2c94c", "#eb5757"],
                range_color=[0, 50], text="Failure/Stall Rate (%)",
            )
            fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=380,
                                   coloraxis_showscale=False, yaxis_title=None)
            st.plotly_chart(fig_bar, use_container_width=True)

        st.divider()

        # ---- Flagged bottleneck callout ---------------------------------------
        st.subheader("🚨 Primary Bottleneck Detected")
        st.error(
            f"**{result['worst_handoff']}** is the weakest handoff, with a "
            f"**{result['worst_rate']}%** stall/failure rate.\n\n"
            f"**Likely root cause:** {result['worst_cause']}"
        )

        st.subheader("Full Handoff Report")
        display_df = df[[
            "Handoff", "Items Entering", "Failure/Stall Rate (%)",
            "Avg. Delay (hrs)", "Items Lost", "Root Cause",
        ]].copy()
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.caption(f"Scan completed at {result['scanned_at']} · Simulated data, not a live workflow feed.")


# ==============================================================================
# FOOTER
# ==============================================================================
st.divider()
st.caption(
    "Sentinel Orchestrator MVP · All data shown is simulated for demonstration "
    "purposes · No external AI API calls are made."
)
