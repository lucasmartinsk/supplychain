import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st


# ============================================================
# TPRM RISK LAB — V2
# Vendor Risk • Evidence • Findings • Fourth Parties
# Training / Portfolio Project
# ============================================================

DB_NAME = "tprm_database.db"

REQUIRED_SHEETS = {
    "vendors",
    "documents",
    "subcontractors",
    "document_requirements",
    "findings",
}


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TPRM Risk Lab",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PROFESSIONAL UI
# ============================================================

st.markdown(
    """
    <style>
    .stApp { background:#f5f7fa; color:#172033; }
    .block-container { max-width:1500px; padding-top:1.4rem; padding-bottom:3rem; }

    section[data-testid="stSidebar"] {
        background:#101827;
        border-right:1px solid #1f2937;
    }
    section[data-testid="stSidebar"] * { color:#e5e7eb; }

    h1,h2,h3 { color:#111827; letter-spacing:-.02em; }

    .brand {
        padding:.5rem 0 1.25rem;
        border-bottom:1px solid #263244;
        margin-bottom:1rem;
    }
    .brand-title { color:white; font-size:1.25rem; font-weight:800; }
    .brand-subtitle { color:#94a3b8; font-size:.75rem; margin-top:.15rem; }

    .page-kicker {
        color:#64748b; font-size:.76rem; font-weight:800;
        letter-spacing:.12em; text-transform:uppercase;
    }
    .page-title { font-size:2rem; font-weight:800; margin:.15rem 0; }
    .page-subtitle { color:#64748b; font-size:.94rem; margin-bottom:1.4rem; }

    .metric-card,.section-card {
        background:#fff;
        border:1px solid #e5e7eb;
        border-radius:12px;
        box-shadow:0 1px 2px rgba(15,23,42,.04);
    }
    .metric-card { padding:1rem 1.1rem; min-height:118px; }
    .metric-label {
        color:#64748b; font-size:.74rem; font-weight:800;
        text-transform:uppercase; letter-spacing:.06em;
    }
    .metric-value { color:#111827; font-size:1.9rem; font-weight:800; margin-top:.3rem; }
    .metric-note { color:#94a3b8; font-size:.76rem; margin-top:.15rem; }
    .section-card { padding:1.2rem; margin-bottom:1rem; }
    .section-title { font-size:1rem; font-weight:800; color:#111827; margin-bottom:.7rem; }

    .risk-critical { color:#b91c1c; }
    .risk-high { color:#c2410c; }
    .risk-medium { color:#a16207; }
    .risk-low { color:#15803d; }

    .pill {
        display:inline-block; padding:.26rem .62rem; border-radius:999px;
        font-size:.7rem; font-weight:800;
    }
    .pill-critical { background:#fee2e2; color:#991b1b; }
    .pill-high { background:#ffedd5; color:#9a3412; }
    .pill-medium { background:#fef3c7; color:#92400e; }
    .pill-low { background:#dcfce7; color:#166534; }
    .pill-received,.pill-closed,.pill-compliant { background:#dcfce7; color:#166534; }
    .pill-pending,.pill-in-progress { background:#fef3c7; color:#92400e; }
    .pill-expired,.pill-missing,.pill-open,.pill-undisclosed { background:#fee2e2; color:#991b1b; }

    .finding {
        border-left:4px solid #dc2626; background:#fff7f7;
        padding:.75rem 1rem; border-radius:0 8px 8px 0; margin-bottom:.6rem;
    }
    .finding.medium { border-left-color:#ca8a04; background:#fffdf3; }
    .finding.low { border-left-color:#16a34a; background:#f4fff7; }
    .finding-title { font-weight:750; color:#1f2937; }
    .finding-detail { color:#64748b; font-size:.8rem; margin-top:.12rem; }

    .score-box {
        background:#fff; border:1px solid #e5e7eb; border-radius:12px;
        padding:1.15rem;
    }
    .score-number { font-size:2.5rem; font-weight:850; color:#111827; }
    .driver-row {
        display:flex; justify-content:space-between; padding:.42rem 0;
        border-bottom:1px solid #f1f5f9; font-size:.83rem;
    }
    .driver-row:last-child { border-bottom:0; }
    .driver-name { color:#475569; }
    .driver-score { font-weight:800; color:#111827; }

    .sidebar-caption { color:#64748b; font-size:.72rem; margin-top:1.5rem; line-height:1.5; }
    div[data-testid="stDataFrame"] { border:1px solid #e5e7eb; border-radius:10px; overflow:hidden; }
    .stButton > button { border-radius:8px; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


def table_exists(table_name):
    conn = get_connection()
    try:
        result = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            conn,
            params=(table_name,),
        )
        return not result.empty
    finally:
        conn.close()


@st.cache_data(ttl=30)
def load_data(table_name):
    allowed = {
        "vendors", "documents", "subcontractors",
        "document_requirements", "findings",
    }
    if table_name not in allowed or not table_exists(table_name):
        return pd.DataFrame()

    conn = get_connection()
    try:
        return pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)
    finally:
        conn.close()


def save_table(df, table_name):
    conn = get_connection()
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    finally:
        conn.close()
    load_data.clear()


# ============================================================
# HELPERS
# ============================================================

def normalize_columns(df):
    df = df.copy()
    df.columns = (
        df.columns.str.strip().str.lower()
        .str.replace(" ", "_").str.replace("-", "_")
    )
    return df


def truthy(value):
    return str(value).strip().lower() in {
        "true", "yes", "1", "y", "disclosed"
    }


def pill(value):
    text = str(value)
    css = (
        text.lower().replace(" ", "-")
        .replace("/", "-")
    )
    return f'<span class="pill pill-{css}">{text}</span>'


def page_header(kicker, title, subtitle):
    st.markdown(
        f"""
        <div class="page-kicker">{kicker}</div>
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def days_to_contract_end(value):
    dt = pd.to_datetime(value, errors="coerce")
    if pd.isna(dt):
        return None
    return (dt.normalize() - pd.Timestamp.today().normalize()).days


# ============================================================
# DOCUMENT ENGINE
# ============================================================

def document_status(vendor_id, doc_type, documents):
    rows = documents[
        (documents["vendor_id"] == vendor_id)
        & (
            documents["doc_type"].astype(str).str.lower()
            == str(doc_type).lower()
        )
    ].copy()

    if rows.empty:
        return "Missing"

    today = pd.Timestamp.today().normalize()

    for _, row in rows.iterrows():
        status = str(row.get("status", "")).lower()
        expiry = pd.to_datetime(row.get("expiry_date"), errors="coerce")

        if status == "received":
            if pd.notna(expiry) and expiry < today:
                continue
            return "Received"

        if status == "pending":
            return "Pending"

        if status == "expired":
            return "Expired"

    return "Missing"


def compliance_engine(vendor, documents, requirements):
    if vendor.empty or requirements.empty:
        return {
            "required": 0, "received": 0, "missing": [],
            "pending": [], "expired": [], "percentage": 0
        }

    v = vendor.iloc[0]
    vendor_id = v["vendor_id"]
    criticality = str(v.get("criticality", "Low"))

    req = requirements[
        requirements["criticality"].astype(str).str.lower()
        == criticality.lower()
    ]

    required_docs = req["required_document"].tolist()

    # Business rule: High vendors require ISO 27001 OR SOC 2.
    alternatives = []
    if criticality.lower() == "high":
        required_docs = [
            d for d in required_docs
            if d not in ["ISO 27001 Certificate", "SOC 2 Report"]
        ]
        alternatives = ["ISO 27001 Certificate", "SOC 2 Report"]

    received, missing, pending, expired = [], [], [], []

    for doc in required_docs:
        status = document_status(vendor_id, doc, documents)

        if status == "Received":
            received.append(doc)
        elif status == "Pending":
            pending.append(doc)
        elif status == "Expired":
            expired.append(doc)
        else:
            missing.append(doc)

    if alternatives:
        alt_status = {
            d: document_status(vendor_id, d, documents)
            for d in alternatives
        }

        if "Received" in alt_status.values():
            received.append("ISO 27001 / SOC 2")
        elif "Pending" in alt_status.values():
            pending.append("ISO 27001 / SOC 2")
        elif all(s == "Expired" for s in alt_status.values()):
            expired.append("ISO 27001 / SOC 2")
        else:
            missing.append("ISO 27001 / SOC 2")

    required_count = (
        len(required_docs) + (1 if alternatives else 0)
    )
    received_count = len(received)

    percentage = (
        round(received_count / required_count * 100)
        if required_count else 0
    )

    return {
        "required": required_count,
        "received": received_count,
        "missing": missing,
        "pending": pending,
        "expired": expired,
        "percentage": percentage,
    }


# ============================================================
# RISK ENGINE
# ============================================================

def risk_engine(vendor, documents, subcontractors, requirements):
    v = vendor.iloc[0]

    criticality = str(v.get("criticality", "Low")).lower()
    data_access = str(v.get("data_accessed", "None")).lower()

    # Inherent risk — 30 points
    criticality_score = {
        "critical": 30,
        "high": 22,
        "medium": 12,
        "low": 4,
    }.get(criticality, 5)

    # Data sensitivity — 20 points
    if "payment" in data_access:
        data_score = 20
    elif "client pii" in data_access and "employee data" in data_access:
        data_score = 18
    elif "client pii" in data_access:
        data_score = 16
    elif "employee data" in data_access:
        data_score = 12
    elif "security logs" in data_access:
        data_score = 15
    elif "none" in data_access:
        data_score = 0
    else:
        data_score = 8

    compliance = compliance_engine(
        vendor, documents, requirements
    )

    # Evidence risk — 20 points
    evidence_gap = (
        len(compliance["missing"]) * 7
        + len(compliance["expired"]) * 6
        + len(compliance["pending"]) * 3
    )
    evidence_score = min(20, evidence_gap)

    # Fourth-party risk — 15 points
    vendor_id = v["vendor_id"]
    subs = subcontractors[
        subcontractors["parent_vendor_id"] == vendor_id
    ] if not subcontractors.empty else pd.DataFrame()

    hidden = 0
    if not subs.empty and "disclosed_by_vendor" in subs.columns:
        hidden = sum(
            not truthy(x)
            for x in subs["disclosed_by_vendor"]
        )

    fourth_party_score = min(15, hidden * 8)

    # Contract risk — 10 points
    contract_days = days_to_contract_end(
        v.get("contract_end_date")
    )

    if contract_days is None:
        contract_score = 5
    elif contract_days < 0:
        contract_score = 10
    elif contract_days <= 90:
        contract_score = 7
    elif contract_days <= 180:
        contract_score = 3
    else:
        contract_score = 0

    # Status / operational issue — 5 points
    vendor_status = str(v.get("status", "")).lower()
    status_score = 5 if vendor_status in {
        "under review", "terminated"
    } else 0

    score = min(
        100,
        criticality_score
        + data_score
        + evidence_score
        + fourth_party_score
        + contract_score
        + status_score,
    )

    if score >= 75:
        level = "Critical"
    elif score >= 50:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"

    drivers = [
        ("Criticality", criticality_score, 30),
        ("Data sensitivity", data_score, 20),
        ("Documentation", evidence_score, 20),
        ("Fourth-party exposure", fourth_party_score, 15),
        ("Contract", contract_score, 10),
        ("Operational status", status_score, 5),
    ]

    return {
        "score": score,
        "level": level,
        "drivers": drivers,
        "compliance": compliance,
        "hidden_subcontractors": hidden,
        "contract_days": contract_days,
    }


# ============================================================
# FINDINGS ENGINE
# ============================================================

def generate_findings(vendor, documents, subcontractors, requirements):
    result = risk_engine(
        vendor, documents, subcontractors, requirements
    )

    v = vendor.iloc[0]
    findings = []

    for doc in result["compliance"]["missing"]:
        findings.append({
            "vendor_id": v["vendor_id"],
            "vendor_name": v["name"],
            "severity": "High",
            "finding_type": "Missing Evidence",
            "description": f"Required document missing: {doc}",
        })

    for doc in result["compliance"]["expired"]:
        findings.append({
            "vendor_id": v["vendor_id"],
            "vendor_name": v["name"],
            "severity": "High",
            "finding_type": "Expired Evidence",
            "description": f"Required document expired: {doc}",
        })

    for doc in result["compliance"]["pending"]:
        findings.append({
            "vendor_id": v["vendor_id"],
            "vendor_name": v["name"],
            "severity": "Medium",
            "finding_type": "Pending Evidence",
            "description": f"Required document pending: {doc}",
        })

    if result["hidden_subcontractors"]:
        findings.append({
            "vendor_id": v["vendor_id"],
            "vendor_name": v["name"],
            "severity": "High",
            "finding_type": "Fourth-Party Risk",
            "description": (
                f'{result["hidden_subcontractors"]} undisclosed '
                "subcontractor relationship(s) identified."
            ),
        })

    if result["contract_days"] is not None:
        if result["contract_days"] < 0:
            findings.append({
                "vendor_id": v["vendor_id"],
                "vendor_name": v["name"],
                "severity": "High",
                "finding_type": "Contract",
                "description": "Contract has expired.",
            })
        elif result["contract_days"] <= 90:
            findings.append({
                "vendor_id": v["vendor_id"],
                "vendor_name": v["name"],
                "severity": "Medium",
                "finding_type": "Contract",
                "description": (
                    f'Contract expires in {result["contract_days"]} days.'
                ),
            })

    return findings


# ============================================================
# LOAD DATA
# ============================================================

vendors = load_data("vendors")
documents = load_data("documents")
subcontractors = load_data("subcontractors")
requirements = load_data("document_requirements")
findings_db = load_data("findings")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <div class="brand">
        <div class="brand-title">🛡️ TPRM RISK LAB</div>
        <div class="brand-subtitle">Third-Party Risk Management</div>
    </div>
    """,
    unsafe_allow_html=True,
)

menu = st.sidebar.radio(
    "WORKSPACE",
    [
        "Executive Dashboard",
        "Vendor Portfolio",
        "Risk Register",
        "Findings & Remediation",
        "Fourth-Party Risk",
        "Document Compliance",
        "Assessment Simulation",
        "Data Import",
    ],
)

st.sidebar.markdown(
    """
    <div class="sidebar-caption">
        Portfolio project & practical training lab<br>
        IT Risk • Cyber GRC • TPRM
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if menu == "Executive Dashboard":

    page_header(
        "Executive Overview",
        "TPRM Risk Overview",
        "Portfolio exposure, evidence quality, remediation and supply-chain risk.",
    )

    if vendors.empty:
        st.info("Import the mock dataset to activate the dashboard.")
        st.stop()

    results = []
    for _, vendor in vendors.iterrows():
        r = risk_engine(
            pd.DataFrame([vendor]),
            documents,
            subcontractors,
            requirements,
        )
        results.append({
            "Vendor": vendor["name"],
            "Risk": r["level"],
            "Score": r["score"],
            "Compliance": r["compliance"]["percentage"],
            "Hidden": r["hidden_subcontractors"],
        })

    register = pd.DataFrame(results)

    critical = int(
        (vendors["criticality"].astype(str).str.lower() == "critical").sum()
    )
    high_risk = int(
        register["Risk"].isin(["Critical", "High"]).sum()
    )
    avg_compliance = int(register["Compliance"].mean())
    total_hidden = int(register["Hidden"].sum())

    overall = (
        "Critical" if high_risk >= 8
        else "High" if high_risk >= 4
        else "Medium" if high_risk >= 1
        else "Low"
    )

    cols = st.columns(5)
    cards = [
        ("Overall Exposure", overall, "Portfolio posture"),
        ("Vendors", len(vendors), "Assessment population"),
        ("Critical", critical, "Inherent criticality"),
        ("High/Critical Risk", high_risk, "Immediate attention"),
        ("Evidence Compliance", f"{avg_compliance}%", "Portfolio average"),
    ]

    for col, (label, value, note) in zip(cols, cards):
        with col:
            css = f"risk-{str(value).lower()}" if label == "Overall Exposure" else ""
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value {css}">{value}</div>
                    <div class="metric-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    left, right = st.columns(2)

    with left:
        st.markdown(
            '<div class="section-card"><div class="section-title">Risk Distribution</div>',
            unsafe_allow_html=True,
        )
        distribution = register["Risk"].value_counts().reindex(
            ["Critical", "High", "Medium", "Low"],
            fill_value=0,
        )
        st.bar_chart(distribution)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="section-card"><div class="section-title">Top Risk Vendors</div>',
            unsafe_allow_html=True,
        )
        top = register.sort_values("Score", ascending=False).head(8)
        st.dataframe(
            top,
            use_container_width=True,
            hide_index=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-card"><div class="section-title">Executive Attention</div>',
        unsafe_allow_html=True,
    )

    attention = register[
        register["Risk"].isin(["Critical", "High"])
    ].sort_values("Score", ascending=False)

    if attention.empty:
        st.success("No High or Critical risk vendors identified.")
    else:
        st.dataframe(
            attention,
            use_container_width=True,
            hide_index=True,
        )

    if total_hidden:
        st.warning(
            f"{total_hidden} undisclosed fourth-party relationship(s) "
            "require review across the portfolio."
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# VENDOR PORTFOLIO
# ============================================================

elif menu == "Vendor Portfolio":

    page_header(
        "Vendor Management",
        "Vendor Portfolio",
        "Investigate vendors from an inherent-risk and evidence perspective.",
    )

    if vendors.empty:
        st.stop()

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        crit = st.selectbox(
            "Criticality",
            ["All", "Critical", "High", "Medium", "Low"],
        )

    with c2:
        status = st.selectbox(
            "Status",
            ["All"] + sorted(vendors["status"].astype(str).unique()),
        )

    with c3:
        search = st.text_input(
            "Search",
            placeholder="Vendor name or service...",
        )

    filtered = vendors.copy()

    if crit != "All":
        filtered = filtered[
            filtered["criticality"].astype(str).str.lower()
            == crit.lower()
        ]

    if status != "All":
        filtered = filtered[
            filtered["status"].astype(str) == status
        ]

    if search:
        mask = (
            filtered["name"].astype(str).str.contains(search, case=False, na=False)
            | filtered["service_type"].astype(str).str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    selected_name = st.selectbox(
        "Open Vendor Assessment",
        filtered["name"].tolist() if not filtered.empty else [],
    )

    if selected_name:

        vendor = vendors[vendors["name"] == selected_name]
        v = vendor.iloc[0]

        risk = risk_engine(
            vendor, documents, subcontractors, requirements
        )

        st.markdown(
            f"## {v['name']}"
        )
        st.caption(
            f"{v['service_type']} · {v['data_accessed']}"
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall Risk", risk["level"])
        c2.metric("Risk Score", f"{risk['score']}/100")
        c3.metric("Evidence", f"{risk['compliance']['percentage']}%")
        c4.metric("4th Parties", risk["hidden_subcontractors"])

        st.write("")

        left, right = st.columns([1, 1])

        with left:
            st.markdown(
                '<div class="section-card"><div class="section-title">Risk Drivers</div>',
                unsafe_allow_html=True,
            )

            for name, value, maximum in risk["drivers"]:
                st.markdown(
                    f"""
                    <div class="driver-row">
                        <span class="driver-name">{name}</span>
                        <span class="driver-score">{value}/{maximum}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(
                '<div class="section-card"><div class="section-title">Contract & Status</div>',
                unsafe_allow_html=True,
            )

            st.write(f"**Criticality:** {v['criticality']}")
            st.write(f"**Vendor status:** {v['status']}")
            st.write(f"**Onboarded:** {v['onboarded_date']}")
            st.write(f"**Contract end:** {v['contract_end_date']}")

            days = risk["contract_days"]
            if days is not None:
                if days < 0:
                    st.error("Contract expired.")
                elif days <= 90:
                    st.warning(f"Contract expires in {days} days.")
                else:
                    st.success(f"{days} days remaining.")

            st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("Open Findings")

        generated = generate_findings(
            vendor, documents, subcontractors, requirements
        )

        if not generated:
            st.success("No findings generated for this vendor.")
        else:
            for f in generated:
                cls = f["severity"].lower()
                st.markdown(
                    f"""
                    <div class="finding {cls}">
                        <div class="finding-title">
                            {f["severity"]} · {f["finding_type"]}
                        </div>
                        <div class="finding-detail">
                            {f["description"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# RISK REGISTER
# ============================================================

elif menu == "Risk Register":

    page_header(
        "Risk Management",
        "Risk Register",
        "A consolidated register of inherent risk, control gaps and exposure.",
    )

    if vendors.empty:
        st.stop()

    rows = []

    for _, vendor in vendors.iterrows():
        r = risk_engine(
            pd.DataFrame([vendor]),
            documents,
            subcontractors,
            requirements,
        )

        rows.append({
            "Vendor": vendor["name"],
            "Criticality": vendor["criticality"],
            "Risk": r["level"],
            "Score": r["score"],
            "Evidence": f'{r["compliance"]["percentage"]}%',
            "Findings": len(
                generate_findings(
                    pd.DataFrame([vendor]),
                    documents,
                    subcontractors,
                    requirements,
                )
            ),
            "Hidden 4th Parties": r["hidden_subcontractors"],
            "Contract End": vendor["contract_end_date"],
        })

    register = pd.DataFrame(rows)

    selected = st.multiselect(
        "Risk level",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"],
    )

    view = register[
        register["Risk"].isin(selected)
    ].sort_values("Score", ascending=False)

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Export Risk Register",
        view.to_csv(index=False).encode("utf-8"),
        "tprm_risk_register.csv",
        "text/csv",
    )


# ============================================================
# FINDINGS & REMEDIATION
# ============================================================

elif menu == "Findings & Remediation":

    page_header(
        "Issue Management",
        "Findings & Remediation",
        "Track evidence gaps, fourth-party issues and contract risks through remediation.",
    )

    if vendors.empty:
        st.stop()

    rows = []
    finding_id = 1

    for _, vendor in vendors.iterrows():
        generated = generate_findings(
            pd.DataFrame([vendor]),
            documents,
            subcontractors,
            requirements,
        )

        for f in generated:
            rows.append({
                "Finding ID": f"F-{finding_id:03d}",
                "Vendor": f["vendor_name"],
                "Severity": f["severity"],
                "Type": f["finding_type"],
                "Description": f["description"],
                "Status": "Open",
                "Owner": "TPRM",
            })
            finding_id += 1

    finding_df = pd.DataFrame(rows)

    if finding_df.empty:
        st.success("No open findings.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Open Findings", len(finding_df))
        c2.metric(
            "High / Critical",
            int(finding_df["Severity"].isin(["High", "Critical"]).sum()),
        )
        c3.metric(
            "Vendors Affected",
            finding_df["Vendor"].nunique(),
        )

        st.dataframe(
            finding_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Export Findings",
            finding_df.to_csv(index=False).encode("utf-8"),
            "tprm_findings.csv",
            "text/csv",
        )

        st.info(
            "V2 generates findings dynamically from evidence and supply-chain data. "
            "The next evolution can persist owner, due date, comments and closure evidence "
            "directly in SQLite."
        )


# ============================================================
# FOURTH-PARTY RISK
# ============================================================

elif menu == "Fourth-Party Risk":

    page_header(
        "Supply Chain",
        "Fourth-Party Risk",
        "Identify hidden dependencies beneath your primary vendors.",
    )

    if subcontractors.empty:
        st.info("No subcontractor data available.")
        st.stop()

    merged = subcontractors.merge(
        vendors[["vendor_id", "name", "criticality"]],
        left_on="parent_vendor_id",
        right_on="vendor_id",
        how="left",
    )

    hidden = merged[
        ~merged["disclosed_by_vendor"].apply(truthy)
    ]

    c1, c2, c3 = st.columns(3)
    c1.metric("Subcontractors", len(merged))
    c2.metric("Undisclosed", len(hidden))
    c3.metric("Vendors Exposed", hidden["name"].nunique())

    st.write("")

    st.dataframe(
        merged[
            [
                "name",
                "criticality",
                "subcontractor_name",
                "service_provided",
                "disclosed_by_vendor",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Supply-Chain Findings")

    for _, row in hidden.iterrows():
        st.markdown(
            f"""
            <div class="finding">
                <div class="finding-title">
                    {row["name"]} → {row["subcontractor_name"]}
                </div>
                <div class="finding-detail">
                    {row["service_provided"]} ·
                    {row["criticality"]} primary vendor ·
                    Undisclosed relationship
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# DOCUMENT COMPLIANCE
# ============================================================

elif menu == "Document Compliance":

    page_header(
        "Evidence Management",
        "Document Compliance",
        "Assess whether required evidence is present, valid and current.",
    )

    if vendors.empty:
        st.stop()

    selected = st.selectbox(
        "Vendor",
        vendors["name"].tolist(),
    )

    vendor = vendors[
        vendors["name"] == selected
    ]

    result = compliance_engine(
        vendor, documents, requirements
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Required", result["required"])
    c2.metric("Received", result["received"])
    c3.metric("Gaps", len(result["missing"]) + len(result["expired"]))
    c4.metric("Compliance", f'{result["percentage"]}%')

    st.write("")

    rows = []

    for doc in result["missing"]:
        rows.append([doc, "Missing"])
    for doc in result["expired"]:
        rows.append([doc, "Expired"])
    for doc in result["pending"]:
        rows.append([doc, "Pending"])

    # Reconstruct received evidence.
    vendor_id = vendor.iloc[0]["vendor_id"]
    req = requirements[
        requirements["criticality"].astype(str).str.lower()
        == str(vendor.iloc[0]["criticality"]).lower()
    ]

    for doc in req["required_document"].tolist():
        if doc in ["ISO 27001 Certificate", "SOC 2 Report"]:
            continue
        if document_status(vendor_id, doc, documents) == "Received":
            rows.append([doc, "Received"])

    if str(vendor.iloc[0]["criticality"]).lower() == "high":
        iso = document_status(vendor_id, "ISO 27001 Certificate", documents)
        soc = document_status(vendor_id, "SOC 2 Report", documents)
        if iso == "Received" or soc == "Received":
            rows.append(["ISO 27001 / SOC 2", "Received"])

    compliance_table = pd.DataFrame(
        rows,
        columns=["Required Evidence", "Status"],
    )

    st.dataframe(
        compliance_table,
        use_container_width=True,
        hide_index=True,
    )

    if result["percentage"] == 100:
        st.success("Evidence set is fully compliant.")
    elif result["expired"]:
        st.error("Expired evidence requires remediation.")
    elif result["missing"]:
        st.warning("Missing evidence requires follow-up.")
    else:
        st.info("Evidence is partially complete; pending items remain.")


# ============================================================
# ASSESSMENT SIMULATION
# ============================================================

elif menu == "Assessment Simulation":

    page_header(
        "Training Lab",
        "TPRM Assessment Simulation",
        "Practice assessing a vendor before revealing the model answer.",
    )

    if vendors.empty:
        st.stop()

    selected_name = st.selectbox(
        "Choose a case",
        vendors["name"].tolist(),
    )

    vendor = vendors[
        vendors["name"] == selected_name
    ]
    v = vendor.iloc[0]

    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">Case File</div>
            <b>Vendor:</b> {v["name"]}<br>
            <b>Service:</b> {v["service_type"]}<br>
            <b>Data accessed:</b> {v["data_accessed"]}<br>
            <b>Criticality:</b> {v["criticality"]}<br>
            <b>Status:</b> {v["status"]}<br>
            <b>Contract end:</b> {v["contract_end_date"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Your Assessment")

    answer_risk = st.radio(
        "1. What is the overall risk level?",
        ["Low", "Medium", "High", "Critical"],
        horizontal=True,
    )

    answer_fourth = st.radio(
        "2. Is there a fourth-party risk?",
        ["Yes", "No"],
        horizontal=True,
    )

    answer_evidence = st.multiselect(
        "3. Which evidence issues should be investigated?",
        [
            "Missing documents",
            "Expired documents",
            "Pending documents",
            "Contract expiry",
            "Undisclosed subcontractors",
        ],
    )

    if st.button("Submit Assessment", type="primary"):
        model = risk_engine(
            vendor, documents, subcontractors, requirements
        )

        actual_risk = model["level"]
        actual_fourth = (
            "Yes"
            if model["hidden_subcontractors"] > 0
            else "No"
        )

        expected_evidence = set()

        if model["compliance"]["missing"]:
            expected_evidence.add("Missing documents")
        if model["compliance"]["expired"]:
            expected_evidence.add("Expired documents")
        if model["compliance"]["pending"]:
            expected_evidence.add("Pending documents")
        if model["contract_days"] is not None and model["contract_days"] <= 90:
            expected_evidence.add("Contract expiry")
        if model["hidden_subcontractors"]:
            expected_evidence.add("Undisclosed subcontractors")

        risk_correct = answer_risk == actual_risk
        fourth_correct = answer_fourth == actual_fourth
        evidence_correct = expected_evidence == set(answer_evidence)

        st.divider()
        st.subheader("Assessment Result")

        if risk_correct:
            st.success(f"✓ Risk level correct: {actual_risk}")
        else:
            st.error(
                f"Risk level: your answer was {answer_risk}; "
                f"model assessment is {actual_risk}."
            )

        if fourth_correct:
            st.success(f"✓ Fourth-party answer correct: {actual_fourth}")
        else:
            st.error(
                f"Fourth-party risk: your answer was {answer_fourth}; "
                f"model assessment is {actual_fourth}."
            )

        if evidence_correct:
            st.success("✓ Evidence issue identification is correct.")
        else:
            st.warning(
                "Evidence issue identification differs from the model."
            )

        st.markdown(
            f"""
            <div class="score-box">
                <div class="metric-label">Model Risk Score</div>
                <div class="score-number">{model["score"]}/100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        st.write("**Risk drivers:**")
        for name, value, maximum in model["drivers"]:
            st.write(f"- {name}: {value}/{maximum}")

        st.info(
            "This is a training model, not a production risk methodology. "
            "In a real organization, scoring should be aligned with approved "
            "risk appetite, control frameworks and governance."
        )


# ============================================================
# DATA IMPORT
# ============================================================

elif menu == "Data Import":

    page_header(
        "Administration",
        "Data Import",
        "Load the training dataset or replace it with your own TPRM case data.",
    )

    st.info(
        "Expected sheets: vendors, documents, subcontractors, "
        "document_requirements and findings."
    )

    uploaded = st.file_uploader(
        "Upload Excel workbook",
        type=["xlsx"],
    )

    if uploaded:

        try:
            xls = pd.ExcelFile(uploaded)

            available = {
                s.strip().lower()
                for s in xls.sheet_names
            }

            # Findings is optional for backward compatibility.
            required_for_upload = REQUIRED_SHEETS - {"findings"}
            missing = required_for_upload - available

            if missing:
                st.error(
                    "Missing required sheets: "
                    + ", ".join(sorted(missing))
                )
                st.stop()

            sheets = {
                s.lower(): normalize_columns(
                    pd.read_excel(xls, sheet_name=s)
                )
                for s in xls.sheet_names
            }

            tabs = st.tabs(
                [
                    "Vendors",
                    "Documents",
                    "Subcontractors",
                    "Requirements",
                    "Findings",
                ]
            )

            mapping = [
                ("vendors", tabs[0]),
                ("documents", tabs[1]),
                ("subcontractors", tabs[2]),
                ("document_requirements", tabs[3]),
            ]

            for name, tab in mapping:
                with tab:
                    st.caption(
                        f'{len(sheets[name]):,} records'
                    )
                    st.dataframe(
                        sheets[name],
                        use_container_width=True,
                        hide_index=True,
                    )

            with tabs[4]:
                if "findings" in sheets:
                    st.dataframe(
                        sheets["findings"],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info(
                        "Findings are generated dynamically; "
                        "no findings sheet was supplied."
                    )

            st.divider()

            if st.button(
                "Commit Dataset to TPRM Database",
                type="primary",
                use_container_width=True,
            ):

                for name in [
                    "vendors",
                    "documents",
                    "subcontractors",
                    "document_requirements",
                ]:
                    save_table(sheets[name], name)

                if "findings" in sheets:
                    save_table(sheets["findings"], "findings")

                st.success(
                    "Dataset imported successfully."
                )

        except Exception as exc:
            st.error(
                f"Unable to process workbook: {exc}"
            )
