import sqlite3
from pathlib import Path
from datetime import date

import pandas as pd
import streamlit as st


# ============================================================
# TPRM RISK LAB
# Professional Streamlit MVP
# ============================================================

DB_NAME = "tprm_database.db"

REQUIRED_SHEETS = {
    "vendors",
    "documents",
    "subcontractors",
    "document_requirements",
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
    /* ---------- Global ---------- */
    .stApp {
        background: #f5f7fa;
        color: #172033;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: #101827;
        border-right: 1px solid #1f2937;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] .stRadio label {
        padding: 0.35rem 0;
    }

    /* ---------- Typography ---------- */
    h1, h2, h3 {
        color: #111827;
        letter-spacing: -0.02em;
    }

    .page-kicker {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }

    .page-title {
        font-size: 2rem;
        font-weight: 750;
        margin-bottom: 0.2rem;
    }

    .page-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* ---------- Cards ---------- */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.1rem 1.15rem;
        min-height: 125px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    .metric-label {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .metric-value {
        color: #111827;
        font-size: 2rem;
        font-weight: 750;
        margin-top: 0.35rem;
    }

    .metric-note {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-top: 0.2rem;
    }

    .risk-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        min-height: 150px;
    }

    .risk-label {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    .risk-value {
        font-size: 2rem;
        font-weight: 800;
        margin-top: 0.25rem;
    }

    .risk-high { color: #c2410c; }
    .risk-critical { color: #b91c1c; }
    .risk-medium { color: #a16207; }
    .risk-low { color: #15803d; }

    /* ---------- Status pills ---------- */
    .pill {
        display: inline-block;
        padding: 0.28rem 0.65rem;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 750;
        letter-spacing: 0.02em;
    }

    .pill-critical {
        background: #fee2e2;
        color: #991b1b;
    }

    .pill-high {
        background: #ffedd5;
        color: #9a3412;
    }

    .pill-medium {
        background: #fef3c7;
        color: #92400e;
    }

    .pill-low {
        background: #dcfce7;
        color: #166534;
    }

    .pill-valid {
        background: #dcfce7;
        color: #166534;
    }

    .pill-pending {
        background: #fef3c7;
        color: #92400e;
    }

    .pill-expired {
        background: #fee2e2;
        color: #991b1b;
    }

    /* ---------- Section cards ---------- */
    .section-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1rem;
        font-weight: 750;
        color: #111827;
        margin-bottom: 0.75rem;
    }

    .finding {
        border-left: 4px solid #dc2626;
        background: #fff7f7;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.65rem;
    }

    .finding.high {
        border-left-color: #ea580c;
        background: #fffaf5;
    }

    .finding.medium {
        border-left-color: #ca8a04;
        background: #fffdf3;
    }

    .finding-title {
        font-weight: 700;
        color: #1f2937;
    }

    .finding-detail {
        color: #64748b;
        font-size: 0.82rem;
        margin-top: 0.15rem;
    }

    /* ---------- Sidebar branding ---------- */
    .brand {
        padding: 0.5rem 0 1.25rem 0;
        border-bottom: 1px solid #263244;
        margin-bottom: 1rem;
    }

    .brand-title {
        color: #ffffff;
        font-size: 1.25rem;
        font-weight: 800;
    }

    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.75rem;
        margin-top: 0.15rem;
    }

    .sidebar-caption {
        color: #64748b;
        font-size: 0.72rem;
        margin-top: 1.5rem;
        line-height: 1.5;
    }

    /* ---------- Tables ---------- */
    div[data-testid="stDataFrame"] {
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        overflow: hidden;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        border-radius: 8px;
        font-weight: 650;
    }

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
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name=?
            """,
            conn,
            params=(table_name,),
        )
        return not result.empty
    finally:
        conn.close()


@st.cache_data(ttl=30)
def load_data(table_name):
    allowed = {
        "vendors",
        "documents",
        "subcontractors",
        "document_requirements",
    }

    if table_name not in allowed or not table_exists(table_name):
        return pd.DataFrame()

    conn = get_connection()
    try:
        return pd.read_sql_query(
            f'SELECT * FROM "{table_name}"',
            conn,
        )
    finally:
        conn.close()


def save_table(df, table_name):
    conn = get_connection()
    try:
        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False,
        )
    finally:
        conn.close()

    load_data.clear()


# ============================================================
# DATA HELPERS
# ============================================================

def normalize_columns(df):
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )
    return df


def truthy(value):
    return str(value).strip().lower() in {
        "true", "yes", "1", "y", "disclosed"
    }


def get_status_pill(value):
    text = str(value)
    css = text.lower().replace(" ", "-").replace("/", "-")
    return f'<span class="pill pill-{css}">{text}</span>'


def calculate_document_compliance(vendor, documents, requirements):
    if vendor.empty or requirements.empty:
        return {
            "required": 0,
            "compliant": 0,
            "missing": [],
            "expired": [],
            "pending": [],
            "percentage": 0,
        }

    criticality = str(vendor.iloc[0].get("criticality", "Low"))

    reqs = requirements[
        requirements["criticality"].astype(str).str.lower()
        == criticality.lower()
    ].copy()

    # High: ISO 27001 OR SOC 2
    required_groups = []
    high_alternative = False

    if criticality.lower() == "high":
        standard = reqs[
            ~reqs["required_document"].isin(
                ["ISO 27001 Certificate", "SOC 2 Report"]
            )
        ]["required_document"].tolist()

        required_groups = standard
        high_alternative = True
    else:
        required_groups = reqs["required_document"].tolist()

    vendor_id = vendor.iloc[0]["vendor_id"]

    vd = documents[
        documents["vendor_id"] == vendor_id
    ].copy()

    today = pd.Timestamp.today().normalize()

    def doc_status(doc_type):
        rows = vd[
            vd["doc_type"].astype(str).str.lower()
            == doc_type.lower()
        ]

        if rows.empty:
            return "Missing"

        # Prefer a current received record.
        for _, row in rows.iterrows():
            status = str(row.get("status", "")).lower()

            if status == "received":
                expiry = pd.to_datetime(
                    row.get("expiry_date"),
                    errors="coerce",
                )

                if pd.notna(expiry) and expiry < today:
                    continue

                return "Received"

            if status == "pending":
                return "Pending"

            if status == "expired":
                return "Expired"

        return "Missing"

    missing = []
    expired = []
    pending = []
    compliant = 0
    required_count = len(required_groups) + (1 if high_alternative else 0)

    for doc in required_groups:
        status = doc_status(doc)

        if status == "Received":
            compliant += 1
        elif status == "Pending":
            pending.append(doc)
        elif status == "Expired":
            expired.append(doc)
        else:
            missing.append(doc)

    if high_alternative:
        iso = doc_status("ISO 27001 Certificate")
        soc = doc_status("SOC 2 Report")

        if iso == "Received" or soc == "Received":
            compliant += 1
        elif iso == "Expired" and soc == "Expired":
            expired.append("ISO 27001 / SOC 2")
        elif iso == "Pending" or soc == "Pending":
            pending.append("ISO 27001 / SOC 2")
        else:
            missing.append("ISO 27001 / SOC 2")

    percentage = (
        round((compliant / required_count) * 100)
        if required_count
        else 0
    )

    return {
        "required": required_count,
        "compliant": compliant,
        "missing": missing,
        "expired": expired,
        "pending": pending,
        "percentage": percentage,
    }


def calculate_vendor_risk(vendor, documents, subcontractors, requirements):
    compliance = calculate_document_compliance(
        vendor,
        documents,
        requirements,
    )

    criticality = str(
        vendor.iloc[0].get("criticality", "Low")
    ).lower()

    score = {
        "critical": 45,
        "high": 32,
        "medium": 18,
        "low": 5,
    }.get(criticality, 10)

    findings = []

    if compliance["missing"]:
        score += min(25, len(compliance["missing"]) * 8)

        for doc in compliance["missing"]:
            findings.append({
                "severity": "High",
                "title": f"Missing {doc}",
                "detail": "Required evidence is not currently available.",
            })

    if compliance["expired"]:
        score += min(25, len(compliance["expired"]) * 8)

        for doc in compliance["expired"]:
            findings.append({
                "severity": "High",
                "title": f"Expired {doc}",
                "detail": "Required evidence is no longer valid.",
            })

    if compliance["pending"]:
        score += min(12, len(compliance["pending"]) * 4)

        for doc in compliance["pending"]:
            findings.append({
                "severity": "Medium",
                "title": f"Pending {doc}",
                "detail": "Required evidence has not yet been received.",
            })

    vendor_id = vendor.iloc[0]["vendor_id"]

    subs = subcontractors[
        subcontractors["parent_vendor_id"] == vendor_id
    ] if not subcontractors.empty else pd.DataFrame()

    hidden = 0

    if not subs.empty and "disclosed_by_vendor" in subs.columns:
        hidden = sum(
            not truthy(x)
            for x in subs["disclosed_by_vendor"]
        )

    if hidden:
        score += min(20, hidden * 10)

        findings.append({
            "severity": "High",
            "title": f"{hidden} undisclosed subcontractor(s)",
            "detail": "Fourth-party dependency was not disclosed by the primary vendor.",
        })

    contract_end = pd.to_datetime(
        vendor.iloc[0].get("contract_end_date"),
        errors="coerce",
    )

    if pd.notna(contract_end):
        days = (contract_end - pd.Timestamp.today()).days

        if days < 0:
            score += 15
            findings.append({
                "severity": "High",
                "title": "Contract has expired",
                "detail": "Contract end date has passed.",
            })
        elif days <= 90:
            score += 8
            findings.append({
                "severity": "Medium",
                "title": "Contract nearing expiration",
                "detail": f"Contract expires in approximately {days} days.",
            })

    if score >= 75:
        level = "Critical"
    elif score >= 50:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"

    return {
        "score": min(score, 100),
        "level": level,
        "findings": findings,
        "compliance": compliance,
        "hidden_subcontractors": hidden,
    }


def build_risk_register(vendors, documents, subcontractors, requirements):
    rows = []

    for _, vendor in vendors.iterrows():
        result = calculate_vendor_risk(
            pd.DataFrame([vendor]),
            documents,
            subcontractors,
            requirements,
        )

        rows.append({
            "Vendor": vendor.get("name"),
            "Criticality": vendor.get("criticality"),
            "Overall Risk": result["level"],
            "Risk Score": result["score"],
            "Document Compliance": f'{result["compliance"]["percentage"]}%',
            "Open Findings": len(result["findings"]),
            "Hidden 4th Parties": result["hidden_subcontractors"],
            "Status": vendor.get("status"),
        })

    return pd.DataFrame(rows)


# ============================================================
# LOAD DATA
# ============================================================

vendors = load_data("vendors")
documents = load_data("documents")
subcontractors = load_data("subcontractors")
requirements = load_data("document_requirements")


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
        "Fourth-Party Risk",
        "Document Compliance",
        "Data Import",
    ],
)

st.sidebar.markdown(
    """
    <div class="sidebar-caption">
        Internal risk assessment workspace<br>
        Evidence • Vendors • Supply Chain
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# EMPTY DATABASE STATE
# ============================================================

if vendors.empty and menu != "Data Import":
    st.warning(
        "No TPRM data is loaded yet. "
        "Use **Data Import** to upload the mock Excel dataset."
    )


# ============================================================
# PAGE HEADER
# ============================================================

def page_header(kicker, title, subtitle):
    st.markdown(
        f"""
        <div class="page-kicker">{kicker}</div>
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
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
        "A consolidated view of third-party exposure, evidence quality and supply-chain risk.",
    )

    if vendors.empty:
        st.stop()

    register = build_risk_register(
        vendors,
        documents,
        subcontractors,
        requirements,
    )

    critical_count = len(
        vendors[
            vendors["criticality"].astype(str).str.lower()
            == "critical"
        ]
    )

    high_risk_count = len(
        register[
            register["Overall Risk"].isin(
                ["Critical", "High"]
            )
        ]
    )

    avg_compliance = (
        round(
            register["Document Compliance"]
            .str.rstrip("%")
            .astype(float)
            .mean()
        )
        if not register.empty
        else 0
    )

    open_findings = int(
        register["Open Findings"].sum()
    )

    if high_risk_count >= 8:
        overall = "Critical"
    elif high_risk_count >= 4:
        overall = "High"
    elif high_risk_count >= 1:
        overall = "Medium"
    else:
        overall = "Low"

    cols = st.columns(5)

    cards = [
        ("Overall Exposure", overall, "Portfolio risk posture"),
        ("Total Vendors", len(vendors), "Active assessment population"),
        ("Critical Vendors", critical_count, "Highest inherent criticality"),
        ("Open Findings", open_findings, "Evidence & supply-chain issues"),
        ("Document Compliance", f"{avg_compliance}%", "Portfolio average"),
    ]

    for col, (label, value, note) in zip(cols, cards):
        with col:
            css = f"risk-{overall.lower()}" if label == "Overall Exposure" else ""
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

    left, right = st.columns([1, 1])

    with left:
        st.markdown(
            '<div class="section-card"><div class="section-title">Risk Distribution</div>',
            unsafe_allow_html=True,
        )

        distribution = (
            register["Overall Risk"]
            .value_counts()
            .reindex(
                ["Critical", "High", "Medium", "Low"],
                fill_value=0,
            )
        )

        st.bar_chart(distribution)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="section-card"><div class="section-title">Document Compliance</div>',
            unsafe_allow_html=True,
        )

        compliance_counts = pd.Series({
            "Compliant": int(
                register["Document Compliance"]
                .str.rstrip("%")
                .astype(int)
                .ge(100)
                .sum()
            ),
            "Partial": int(
                register["Document Compliance"]
                .str.rstrip("%")
                .astype(int)
                .between(1, 99)
                .sum()
            ),
            "No evidence": int(
                register["Document Compliance"]
                .str.rstrip("%")
                .astype(int)
                .eq(0)
                .sum()
            ),
        })

        st.bar_chart(compliance_counts)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="section-card"><div class="section-title">Priority Attention</div>',
        unsafe_allow_html=True,
    )

    priority = register[
        register["Overall Risk"].isin(["Critical", "High"])
    ].sort_values(
        ["Overall Risk", "Risk Score"],
        ascending=[True, False],
    )

    if priority.empty:
        st.success("No Critical or High risk vendors require immediate attention.")
    else:
        st.dataframe(
            priority[
                [
                    "Vendor",
                    "Criticality",
                    "Overall Risk",
                    "Risk Score",
                    "Document Compliance",
                    "Open Findings",
                    "Hidden 4th Parties",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
# VENDOR PORTFOLIO
# ============================================================

elif menu == "Vendor Portfolio":

    page_header(
        "Vendor Management",
        "Vendor Portfolio",
        "Search, filter and investigate your third-party population.",
    )

    if vendors.empty:
        st.stop()

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        criticality = st.selectbox(
            "Criticality",
            ["All", "Critical", "High", "Medium", "Low"],
        )

    with col2:
        status = st.selectbox(
            "Vendor Status",
            ["All"] + sorted(
                vendors["status"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            ),
        )

    with col3:
        search = st.text_input(
            "Search vendor",
            placeholder="e.g. SecureSend",
        )

    filtered = vendors.copy()

    if criticality != "All":
        filtered = filtered[
            filtered["criticality"].astype(str).str.lower()
            == criticality.lower()
        ]

    if status != "All":
        filtered = filtered[
            filtered["status"].astype(str) == status
        ]

    if search:
        filtered = filtered[
            filtered["name"].astype(str).str.contains(
                search,
                case=False,
                na=False,
            )
        ]

    st.caption(
        f"{len(filtered)} vendor(s) match the current filters."
    )

    st.dataframe(
        filtered[
            [
                "vendor_id",
                "name",
                "service_type",
                "data_accessed",
                "criticality",
                "contract_end_date",
                "status",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Vendor Assessment")

    selected_name = st.selectbox(
        "Select a vendor to investigate",
        filtered["name"].tolist()
        if not filtered.empty
        else vendors["name"].tolist(),
    )

    selected = vendors[
        vendors["name"] == selected_name
    ]

    if not selected.empty:
        vendor = selected.iloc[0]

        result = calculate_vendor_risk(
            selected,
            documents,
            subcontractors,
            requirements,
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Overall Risk", result["level"])
        c2.metric("Risk Score", f'{result["score"]}/100')
        c3.metric(
            "Document Compliance",
            f'{result["compliance"]["percentage"]}%',
        )
        c4.metric(
            "Hidden 4th Parties",
            result["hidden_subcontractors"],
        )

        st.markdown(
            f"""
            ### {vendor["name"]}
            **{vendor["service_type"]}** ·
            Data accessed: **{vendor["data_accessed"]}**
            """
        )

        st.markdown(
            f"Criticality: {get_status_pill(vendor['criticality'])}",
            unsafe_allow_html=True,
        )

        st.write("")

        if result["findings"]:
            st.markdown("#### Open Findings")

            for finding in result["findings"]:
                severity_class = finding["severity"].lower()

                st.markdown(
                    f"""
                    <div class="finding {severity_class}">
                        <div class="finding-title">
                            {finding["severity"]} · {finding["title"]}
                        </div>
                        <div class="finding-detail">
                            {finding["detail"]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("No open findings identified.")


# ============================================================
# RISK REGISTER
# ============================================================

elif menu == "Risk Register":

    page_header(
        "Risk Management",
        "Risk Register",
        "Prioritize third parties based on criticality, evidence gaps and fourth-party exposure.",
    )

    if vendors.empty:
        st.stop()

    register = build_risk_register(
        vendors,
        documents,
        subcontractors,
        requirements,
    )

    selected_risk = st.multiselect(
        "Risk level",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"],
    )

    result = register[
        register["Overall Risk"].isin(selected_risk)
    ].sort_values(
        "Risk Score",
        ascending=False,
    )

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Export Risk Register",
        result.to_csv(index=False).encode("utf-8"),
        "tprm_risk_register.csv",
        "text/csv",
    )


# ============================================================
# FOURTH-PARTY RISK
# ============================================================

elif menu == "Fourth-Party Risk":

    page_header(
        "Supply Chain",
        "Fourth-Party Risk",
        "Map subcontractor dependencies and identify undisclosed supply-chain relationships.",
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

    c1.metric("Total Subcontractors", len(merged))
    c2.metric("Undisclosed", len(hidden))
    c3.metric(
        "Vendors with Hidden 4th Parties",
        hidden["name"].nunique(),
    )

    st.write("")

    if not hidden.empty:
        st.error(
            f"{len(hidden)} subcontractor relationship(s) "
            "were not disclosed by the primary vendor."
        )

    display = merged[
        [
            "name",
            "criticality",
            "subcontractor_name",
            "service_provided",
            "disclosed_by_vendor",
        ]
    ].copy()

    display["Disclosure"] = display[
        "disclosed_by_vendor"
    ].apply(
        lambda x: "Disclosed" if truthy(x) else "Undisclosed"
    )

    display = display.drop(
        columns=["disclosed_by_vendor"]
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Undisclosed Dependencies")

    for _, row in hidden.iterrows():

        st.markdown(
            f"""
            <div class="finding">
                <div class="finding-title">
                    {row["name"]} → {row["subcontractor_name"]}
                </div>
                <div class="finding-detail">
                    {row["service_provided"]} ·
                    Vendor criticality: {row["criticality"]}
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
        "Compare required evidence against what has actually been received and what is still valid.",
    )

    if vendors.empty:
        st.stop()

    selected_vendor_name = st.selectbox(
        "Vendor",
        vendors["name"].tolist(),
    )

    vendor = vendors[
        vendors["name"] == selected_vendor_name
    ]

    result = calculate_document_compliance(
        vendor,
        documents,
        requirements,
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Required", result["required"])
    c2.metric("Compliant", result["compliant"])
    c3.metric("Pending", len(result["pending"]))
    c4.metric(
        "Compliance",
        f'{result["percentage"]}%',
    )

    st.write("")

    rows = []

    for item in result["missing"]:
        rows.append([item, "Missing"])

    for item in result["expired"]:
        rows.append([item, "Expired"])

    for item in result["pending"]:
        rows.append([item, "Pending"])

    # Build list of received requirements from the vendor.
    criticality = str(vendor.iloc[0]["criticality"]).lower()

    req = requirements[
        requirements["criticality"].astype(str).str.lower()
        == criticality
    ]

    if criticality == "high":
        candidate_docs = req[
            ~req["required_document"].isin(
                ["ISO 27001 Certificate", "SOC 2 Report"]
            )
        ]["required_document"].tolist()

        iso_received = "ISO 27001 Certificate" not in (
            result["missing"] + result["expired"] + result["pending"]
        )

        soc_received = "SOC 2 Report" not in (
            result["missing"] + result["expired"] + result["pending"]
        )

        if iso_received or soc_received:
            rows.append(["ISO 27001 / SOC 2", "Received"])
    else:
        candidate_docs = req["required_document"].tolist()

    for doc in candidate_docs:
        if doc not in result["missing"] + result["expired"] + result["pending"]:
            rows.append([doc, "Received"])

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
        st.success("All required evidence is currently compliant.")
    elif result["expired"]:
        st.error("Expired evidence requires remediation.")
    elif result["missing"]:
        st.warning("Required evidence is missing.")
    else:
        st.info("Some evidence is still pending.")


# ============================================================
# DATA IMPORT
# ============================================================

elif menu == "Data Import":

    page_header(
        "Administration",
        "Data Import",
        "Load vendor, evidence and supply-chain data from an Excel workbook.",
    )

    st.info(
        "Expected sheets: vendors, documents, subcontractors and document_requirements."
    )

    uploaded_file = st.file_uploader(
        "Upload Excel workbook",
        type=["xlsx"],
    )

    if uploaded_file:

        try:
            xls = pd.ExcelFile(uploaded_file)

            available = {
                name.strip().lower()
                for name in xls.sheet_names
            }

            missing = REQUIRED_SHEETS - available

            if missing:
                st.error(
                    "Missing required sheets: "
                    + ", ".join(sorted(missing))
                )
                st.stop()

            st.success("Workbook structure validated successfully.")

            sheets = {}

            for sheet in xls.sheet_names:
                df = pd.read_excel(
                    xls,
                    sheet_name=sheet,
                )
                sheets[sheet.lower()] = normalize_columns(df)

            tabs = st.tabs(
                [
                    "Vendors",
                    "Documents",
                    "Subcontractors",
                    "Requirements",
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
                    df = sheets[name]

                    st.caption(
                        f"{len(df):,} records · {len(df.columns)} fields"
                    )

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                    )

            st.divider()

            if st.button(
                "Commit Dataset to TPRM Database",
                type="primary",
                use_container_width=True,
            ):

                for name, df in sheets.items():
                    if name in REQUIRED_SHEETS:
                        save_table(df, name)

                st.success(
                    "Dataset imported successfully. "
                    "The TPRM dashboard is now ready."
                )

        except Exception as exc:
            st.error(
                f"Unable to process workbook: {exc}"
            )
