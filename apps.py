


import base64
import io
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


# ============================================================
# TPRM RISK LAB - V3
# Vendor Risk - Evidence - Findings - Fourth Parties - Sample Docs
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
    page_title="IT Risk / GRC Lab",
    page_icon="#",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM - "SIGNAL ROOM"
# Dark analyst-console theme. Monospace for data/numbers,
# sans-serif for prose. Sharp corners, restrained accent color,
# muted (not neon) severity palette. Intentionally not another
# generic light SaaS dashboard template.
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] { font-family:'Inter', sans-serif; }
    .mono { font-family:'JetBrains Mono', monospace; }

    /* Light content area, dark navy sidebar for anchor/contrast - reads as a
       professional analytical tool without the readability issues of full dark mode. */
    .stApp { background:#f4f6fa; color:#1a2233; }
    .block-container { max-width:1520px; padding-top:1.3rem; padding-bottom:3.5rem; }

    section[data-testid="stSidebar"] {
        background:#0f1729;
        border-right:1px solid #1f2b45;
    }
    section[data-testid="stSidebar"] * { color:#e2e8f5; }
    section[data-testid="stSidebar"] label { color:#c3cee3; }

    h1,h2,h3 { color:#0f1729; letter-spacing:-.02em; }

    .brand {
        padding:.6rem 0 1.15rem;
        border-bottom:1px solid #1f2b45;
        margin-bottom:1.1rem;
    }
    .brand-mark {
        display:inline-flex; width:30px; height:30px;
        align-items:center; justify-content:center;
        border:1px solid #f5a623; border-radius:6px;
        background:#241c08; color:#f5a623; font-size:.95rem;
        margin-right:.5rem; vertical-align:middle;
    }
    .brand-title {
        color:#ffffff; font-size:1.05rem; font-weight:800;
        letter-spacing:.04em; vertical-align:middle;
    }
    .brand-subtitle {
        color:#8a96b3; font-size:.68rem; margin-top:.4rem;
        letter-spacing:.06em; text-transform:uppercase;
    }

    .page-kicker {
        color:#b5760f; font-size:.68rem; font-weight:800;
        letter-spacing:.16em; text-transform:uppercase;
        font-family:'JetBrains Mono', monospace;
    }
    .page-title { font-size:1.9rem; font-weight:800; margin:.15rem 0; color:#0f1729; }
    .page-subtitle { color:#5b6478; font-size:.88rem; margin-bottom:1.3rem; }

    /* Cards - sharp corners, hairline borders, minimal shadow */
    .metric-card, .section-card, .console-card {
        background:#ffffff;
        border:1px solid #dde2ec;
        border-radius:6px;
        box-shadow:0 1px 2px rgba(15,23,42,.04);
    }
    .metric-card { padding:.95rem 1rem; position:relative; overflow:hidden; }
    .metric-card::before {
        content:""; position:absolute; left:0; top:0; bottom:0; width:3px;
        background:#b5760f;
    }
    .metric-label {
        color:#5b6478; font-size:.66rem; font-weight:800;
        text-transform:uppercase; letter-spacing:.09em;
    }
    .metric-value {
        color:#0f1729; font-size:1.7rem; font-weight:800; margin-top:.3rem;
        font-family:'JetBrains Mono', monospace;
    }
    .metric-note { color:#7c8598; font-size:.72rem; margin-top:.15rem; }

    .section-card { padding:1.1rem 1.2rem; margin-bottom:1rem; }
    .section-title {
        font-size:.76rem; font-weight:800; color:#1a2233;
        margin-bottom:.7rem; letter-spacing:.08em; text-transform:uppercase;
        font-family:'JetBrains Mono', monospace;
    }

    .console-card {
        padding:1.2rem 1.3rem; margin-bottom:1rem;
        background:linear-gradient(135deg,#0f1729 0%,#182238 100%);
        border-color:#1f2b45;
        color:#e2e8f5;
    }
    .console-kicker {
        color:#7fa8ea; font-size:.64rem; font-weight:800;
        letter-spacing:.14em; text-transform:uppercase;
        font-family:'JetBrains Mono', monospace;
    }
    .console-title { color:#ffffff; font-size:1.2rem; font-weight:800; margin:.2rem 0; }
    .console-copy { color:#b7c0d6; font-size:.82rem; line-height:1.55; }
    .console-score {
        color:#ffffff; font-size:2.5rem; line-height:1; font-weight:800;
        font-family:'JetBrains Mono', monospace;
    }
    .console-score-label {
        color:#8a96b3; font-size:.64rem; font-weight:700;
        letter-spacing:.08em; text-transform:uppercase;
    }

    .signal {
        display:flex; align-items:center; justify-content:space-between; gap:.7rem;
        padding:.58rem .7rem; border:1px solid #e2e6ee; border-radius:5px;
        background:#f8f9fc; margin-bottom:.45rem;
    }
    .signal-name { color:#3b4356; font-size:.78rem; font-weight:600; }
    .signal-value {
        color:#0f1729; font-size:.78rem; font-weight:700;
        font-family:'JetBrains Mono', monospace;
    }

    .risk-critical { color:#b3261e; }
    .risk-high { color:#b45f0e; }
    .risk-medium { color:#96790f; }
    .risk-low { color:#1f7a4d; }

    /* Badges: small rectangles with a left tick - light backgrounds, dark readable text */
    .badge {
        display:inline-flex; align-items:center; gap:.35rem;
        padding:.22rem .5rem; border-radius:4px;
        font-size:.65rem; font-weight:800; letter-spacing:.03em;
        font-family:'JetBrains Mono', monospace;
        border:1px solid transparent;
    }
    .badge::before { content:""; width:6px; height:6px; border-radius:1px; display:inline-block; }
    .badge-critical { background:#fde2e1; color:#b3261e; border-color:#f7c3c1; }
    .badge-critical::before { background:#b3261e; }
    .badge-high { background:#fdead9; color:#b45f0e; border-color:#f8d3ab; }
    .badge-high::before { background:#b45f0e; }
    .badge-medium { background:#fbf1cf; color:#96790f; border-color:#f2e0a0; }
    .badge-medium::before { background:#96790f; }
    .badge-low { background:#dcf3e6; color:#1f7a4d; border-color:#b7e5cb; }
    .badge-low::before { background:#1f7a4d; }
    .badge-received,.badge-closed,.badge-compliant { background:#dcf3e6; color:#1f7a4d; border-color:#b7e5cb; }
    .badge-received::before,.badge-closed::before,.badge-compliant::before { background:#1f7a4d; }
    .badge-pending,.badge-in-progress { background:#fbf1cf; color:#96790f; border-color:#f2e0a0; }
    .badge-pending::before,.badge-in-progress::before { background:#96790f; }
    .badge-expired,.badge-missing,.badge-open,.badge-undisclosed { background:#fde2e1; color:#b3261e; border-color:#f7c3c1; }
    .badge-expired::before,.badge-missing::before,.badge-open::before,.badge-undisclosed::before { background:#b3261e; }
    .badge-active { background:#dbe8fc; color:#1d4ed8; border-color:#b9d3f7; }
    .badge-active::before { background:#1d4ed8; }
    .badge-under-review { background:#fbf1cf; color:#96790f; border-color:#f2e0a0; }
    .badge-under-review::before { background:#96790f; }
    .badge-terminated { background:#e7e9ee; color:#4a5265; border-color:#d3d7e0; }
    .badge-terminated::before { background:#4a5265; }

    .finding {
        border-left:3px solid #d33a30; background:#fdf4f3;
        padding:.7rem .9rem; border-radius:0 5px 5px 0; margin-bottom:.5rem;
    }
    .finding.medium { border-left-color:#b8930f; background:#fbf7ea; }
    .finding.low { border-left-color:#1f7a4d; background:#f0faf4; }
    .finding-title { font-weight:700; color:#1a2233; }
    .finding-detail { color:#5b6478; font-size:.78rem; margin-top:.12rem; }

    .score-box { background:#0f1729; border:1px solid #1f2b45; border-radius:6px; padding:1.15rem; }
    .score-number {
        font-size:2.5rem; font-weight:800; color:#ffffff;
        font-family:'JetBrains Mono', monospace;
    }
    .score-box .metric-label { color:#8a96b3; }

    .driver-row {
        display:flex; justify-content:space-between; padding:.45rem 0;
        border-bottom:1px solid #edeff4; font-size:.81rem;
    }
    .driver-row:last-child { border-bottom:0; }
    .driver-name { color:#3b4356; }
    .driver-score { font-weight:700; color:#0f1729; font-family:'JetBrains Mono', monospace; }

    .risk-flow { display:grid; grid-template-columns:1fr auto 1fr auto 1fr; gap:.45rem; margin:.2rem 0 1rem; }
    .risk-node { border:1px solid #dde2ec; border-radius:5px; padding:.75rem; background:#f8f9fc; }
    .risk-node-label { color:#7c8598; font-size:.62rem; font-weight:800; text-transform:uppercase; letter-spacing:.08em; }
    .risk-node-value { color:#0f1729; font-size:1.05rem; font-weight:700; margin-top:.15rem; font-family:'JetBrains Mono', monospace; }
    .risk-arrow { display:flex; align-items:center; color:#9aa3b8; font-weight:900; }

    .treatment-card {
        border:1px solid #dde2ec; border-radius:5px; background:#f8f9fc;
        padding:.78rem .9rem; margin-bottom:.5rem;
    }
    .treatment-title { color:#1a2233; font-weight:700; font-size:.79rem; }
    .treatment-copy { color:#5b6478; font-size:.74rem; margin-top:.15rem; line-height:1.45; }

    .attention-row {
        display:grid; grid-template-columns:1.6fr .7fr .55fr; gap:.8rem; align-items:center;
        padding:.7rem 0; border-bottom:1px solid #edeff4;
    }
    .attention-row:last-child { border-bottom:0; }
    .attention-name { color:#1a2233; font-weight:700; font-size:.79rem; }
    .attention-meta { color:#5b6478; font-size:.69rem; }
    .attention-score { text-align:right; font-weight:800; color:#0f1729; font-family:'JetBrains Mono', monospace; }

    .doc-preview-frame {
        border:1px solid #dde2ec; border-radius:5px; overflow:hidden; margin-top:.5rem;
    }

    .sample-card {
        border:1px solid #dde2ec; border-radius:6px; background:#ffffff;
        padding:1rem; margin-bottom:.8rem;
    }
    .sample-title { color:#1a2233; font-weight:700; font-size:.88rem; }
    .sample-copy { color:#5b6478; font-size:.76rem; margin-top:.2rem; }

    .sidebar-caption { color:#8a96b3; font-size:.68rem; margin-top:1.4rem; line-height:1.55; }
    div[data-testid="stDataFrame"] { border:1px solid #dde2ec; border-radius:6px; overflow:hidden; }
    .stButton > button { border-radius:5px; font-weight:700; border-color:#c7cddb; }
    button[kind="primary"] { background:#1d4ed8; border-color:#1d4ed8; color:#ffffff; }
    button[kind="primary"]:hover { background:#1741b8; border-color:#1741b8; color:#ffffff; }
    div[data-baseweb="select"] > div { border-radius:5px; }
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


def ensure_document_files_table():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER,
                doc_type TEXT,
                filename TEXT,
                content_type TEXT,
                file_b64 TEXT,
                uploaded_at TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def ensure_vendor_assessments_table():
    """Stores explainable, vendor-level inputs without changing the source workbook."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS vendor_assessments (
                vendor_id INTEGER PRIMARY KEY,
                service_interruption INTEGER,
                customer_impact INTEGER,
                regulatory_importance INTEGER,
                substitutability INTEGER,
                data_exposure INTEGER,
                system_access INTEGER,
                customer_transaction_exposure INTEGER,
                delivery_exposure INTEGER,
                fourth_party_exposure INTEGER,
                override_rating TEXT,
                override_reason TEXT,
                override_review_date TEXT,
                updated_at TEXT
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


@st.cache_data(ttl=30)
def load_data(table_name):
    allowed = {
        "vendors", "documents", "subcontractors",
        "document_requirements", "findings", "document_files",
        "vendor_assessments",
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


def save_document_file(vendor_id, doc_type, filename, content_type, file_bytes):
    ensure_document_files_table()
    conn = get_connection()
    try:
        b64 = base64.b64encode(file_bytes).decode("utf-8")
        conn.execute(
            """
            INSERT INTO document_files
                (vendor_id, doc_type, filename, content_type, file_b64, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                int(vendor_id), str(doc_type), filename, content_type,
                b64, datetime.now().strftime("%Y-%m-%d %H:%M"),
            ),
        )
        conn.commit()
    finally:
        conn.close()
    load_data.clear()


def save_vendor_assessment(vendor_id, values):
    ensure_vendor_assessments_table()
    columns = [
        "service_interruption", "customer_impact", "regulatory_importance",
        "substitutability", "data_exposure", "system_access",
        "customer_transaction_exposure", "delivery_exposure",
        "fourth_party_exposure", "override_rating", "override_reason",
        "override_review_date",
    ]
    payload = [values.get(column) for column in columns]
    conn = get_connection()
    try:
        placeholders = ", ".join(["?"] * (len(columns) + 2))
        updates = ", ".join([f"{column}=excluded.{column}" for column in columns])
        conn.execute(
            f"""
            INSERT INTO vendor_assessments
                (vendor_id, {', '.join(columns)}, updated_at)
            VALUES ({placeholders})
            ON CONFLICT(vendor_id) DO UPDATE SET
                {updates}, updated_at=excluded.updated_at
            """,
            [int(vendor_id), *payload, datetime.now().strftime("%Y-%m-%d %H:%M")],
        )
        conn.commit()
    finally:
        conn.close()
    load_data.clear()


def get_document_file(vendor_id, doc_type):
    ensure_document_files_table()
    df = load_data("document_files")
    if df.empty:
        return None
    match = df[
        (df["vendor_id"] == vendor_id)
        & (df["doc_type"].astype(str).str.lower() == str(doc_type).lower())
    ]
    if match.empty:
        return None
    return match.iloc[-1]  # most recently attached


def render_file_preview(row, height=420):
    """Renders a PDF inline via embedded base64 iframe, or an image directly,
    or a generic download button for other file types."""
    file_bytes = base64.b64decode(row["file_b64"])
    content_type = row.get("content_type", "") or ""

    if "pdf" in content_type.lower() or row["filename"].lower().endswith(".pdf"):
        b64 = base64.b64encode(file_bytes).decode("utf-8")
        st.markdown(
            f"""
            <div class="doc-preview-frame">
                <iframe src="data:application/pdf;base64,{b64}"
                    width="100%" height="{height}" style="border:none;"></iframe>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif content_type.startswith("image/") or row["filename"].lower().endswith((".png", ".jpg", ".jpeg")):
        st.image(file_bytes, use_container_width=True)
    else:
        st.info(f"Preview not available for this file type ({row['filename']}).")

    st.download_button(
        "Download attached file",
        file_bytes,
        row["filename"],
        content_type or "application/octet-stream",
        key=f"dl_{row['file_id']}",
    )


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


def badge(value):
    text = str(value)
    css = text.lower().replace(" ", "-").replace("/", "-")
    return f'<span class="badge badge-{css}">{text}</span>'


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


def contract_watch_item(contract_days):
    """Creates a non-scoring operational alert before contract expiry."""
    if contract_days is None or contract_days > 90 or contract_days < 0:
        return None
    if contract_days <= 30:
        status = "Urgent"
        action = (
            "Confirm the renewal or termination decision immediately and verify that "
            "Legal, Procurement and the exit owner are engaged."
        )
    else:
        status = "Review"
        action = (
            "Confirm the renewal or termination decision, validate required contract "
            "changes and check whether an exit or transition plan is needed."
        )
    return {
        "status": status,
        "days": contract_days,
        "owner": "Relationship Owner — First Line",
        "action": action,
        "risk_impact": "None unless the review identifies an actual issue",
    }


# ============================================================
# MOCK / ILLUSTRATIVE SAMPLE DOCUMENTS
# ============================================================

MOCK_TEMPLATES = {
    "ISO 27001 Certificate": {
        "heading": "CERTIFICATE OF REGISTRATION",
        "subheading": "ISO/IEC 27001:2022 - Information Security Management System",
        "body": [
            "This is to certify that the Information Security Management System of:",
            "",
            "        [VENDOR NAME]",
            "",
            "has been assessed and found to conform to the requirements of",
            "ISO/IEC 27001:2022 for the following scope of activities:",
            "",
            "        Provision of [SERVICE TYPE] and supporting infrastructure.",
            "",
            "Certificate No.:  ISO-XXXXXX          Issue Date:  [DATE]",
            "Original Issue:   [DATE]               Expiry Date: [DATE]",
        ],
    },
    "SOC 2 Report": {
        "heading": "SOC 2 TYPE II REPORT",
        "subheading": "Independent Service Auditor's Report - Security, Availability, Confidentiality",
        "body": [
            "Scope: This report addresses the suitability of the design and operating",
            "effectiveness of controls at [VENDOR NAME] relevant to the Trust Services",
            "Criteria for Security, Availability and Confidentiality, throughout the",
            "period [START DATE] to [END DATE].",
            "",
            "Opinion: In our opinion, the controls were suitably designed and operated",
            "effectively to provide reasonable assurance that the criteria were met",
            "throughout the specified period.",
            "",
            "Section II - Description of the System   ................ page 4",
            "Section III - Trust Services Criteria & Controls ......... page 9",
            "Section IV - Tests of Controls and Results ............... page 15",
        ],
    },
    "DPA": {
        "heading": "DATA PROCESSING AGREEMENT",
        "subheading": "Annex to the Master Services Agreement - GDPR Art. 28",
        "body": [
            "This Data Processing Agreement (\"DPA\") is entered into between:",
            "",
            "  Data Controller:  [YOUR COMPANY]",
            "  Data Processor:   [VENDOR NAME]",
            "",
            "1. Subject matter and duration of processing",
            "2. Nature and purpose of processing: [SERVICE TYPE]",
            "3. Categories of data subjects and personal data: [DATA ACCESSED]",
            "4. Sub-processor authorization and notification requirements",
            "5. Technical and organisational security measures (Art. 32)",
            "6. Data breach notification obligations (Art. 33)",
            "7. Data return / deletion upon termination of services",
        ],
    },
    "BCP/DRP Summary": {
        "heading": "BUSINESS CONTINUITY & DISASTER RECOVERY SUMMARY",
        "subheading": "Vendor Resilience Attestation",
        "body": [
            "Vendor: [VENDOR NAME]          Last tested: [DATE]",
            "",
            "Recovery Time Objective (RTO):        4 hours",
            "Recovery Point Objective (RPO):       15 minutes",
            "",
            "Summary of test scenario: Simulated primary data center outage;",
            "failover to secondary region validated; all critical services",
            "restored within RTO target.",
            "",
            "Next scheduled test: [DATE]",
        ],
    },
}


def generate_mock_document(doc_type):
    """
    Generates an illustrative, clearly-watermarked SAMPLE PDF so someone who
    has never seen a real ISO 27001 / SOC 2 / DPA / BCP document can
    understand its typical structure. This is NOT a valid certificate or
    legal document of any kind - every page carries a disclaimer.
    """
    template = MOCK_TEMPLATES.get(doc_type)
    if template is None:
        return None

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    c.saveState()
    c.setFont("Helvetica-Bold", 60)
    c.setFillColor(colors.Color(0.85, 0.85, 0.85))
    c.translate(width / 2, height / 2)
    c.rotate(45)
    c.drawCentredString(0, 0, "SAMPLE - ILLUSTRATIVE ONLY")
    c.restoreState()

    c.setFillColor(colors.HexColor("#12171f"))
    c.rect(0, height - 25 * mm, width, 25 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, height - 15 * mm, template["heading"])
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, height - 21 * mm, template["subheading"])

    c.setFillColor(colors.HexColor("#1a1a1a"))
    y = height - 40 * mm
    c.setFont("Helvetica", 10)
    for line in template["body"]:
        c.drawString(20 * mm, y, line)
        y -= 6 * mm

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.HexColor("#b91c1c"))
    c.drawString(
        20 * mm, 15 * mm,
        "This is a fictional, illustrative sample created for TPRM Risk Lab training purposes."
    )
    c.drawString(
        20 * mm, 11 * mm,
        "It is not issued by any certification body and has no legal or attestation value."
    )

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()


# ============================================================
# DOCUMENT ENGINE
# ============================================================

def document_status(vendor_id, doc_type, documents):
    """
    Returns: 'Received', 'Pending', 'Expired', or 'Missing'.

    A document whose latest row has status 'Received' but whose
    expiry_date has already passed is reported as 'Expired', not
    silently as 'Missing' - the two mean different things for
    remediation ownership.
    """
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
    lapsed_found = False

    for _, row in rows.iterrows():
        status = str(row.get("status", "")).strip().lower()
        expiry = pd.to_datetime(row.get("expiry_date"), errors="coerce")

        if status == "received":
            if pd.notna(expiry) and expiry < today:
                lapsed_found = True
                continue
            return "Received"

        if status == "pending":
            return "Pending"

        if status == "expired":
            return "Expired"

    return "Expired" if lapsed_found else "Missing"


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

    required_count = (len(required_docs) + (1 if alternatives else 0))
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

RISK_ORDER = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3, "Review Required": -1}

CRITICALITY_FIELDS = [
    "service_interruption", "customer_impact",
    "regulatory_importance", "substitutability",
]

INHERENT_FIELDS = [
    "data_exposure", "system_access", "customer_transaction_exposure",
    "delivery_exposure", "fourth_party_exposure",
]

FIELD_LABELS = {
    "service_interruption": "Service interruption",
    "customer_impact": "Customer impact",
    "regulatory_importance": "Regulatory importance",
    "substitutability": "Substitutability and exit",
    "data_exposure": "Data exposure",
    "system_access": "System access",
    "customer_transaction_exposure": "Customer / transaction exposure",
    "delivery_exposure": "Delivery exposure",
    "fourth_party_exposure": "Fourth-party exposure",
}


def assessment_row(vendor_id):
    rows = load_data("vendor_assessments")
    if rows.empty:
        return {}
    match = rows[rows["vendor_id"] == vendor_id]
    return {} if match.empty else match.iloc[-1].to_dict()


def valid_assessment_value(value):
    if value is None or pd.isna(value):
        return False
    try:
        return int(value) in {0, 1, 2, 3}
    except (TypeError, ValueError):
        return False


def legacy_tier(value):
    mapping = {
        "critical": "Tier 1 — Critical",
        "high": "Tier 2 — High Importance",
        "medium": "Tier 3 — Moderate",
        "low": "Tier 4 — Low",
    }
    return mapping.get(str(value).strip().lower(), "Review Required")


def tier_from_score(score):
    if score >= 10:
        return "Tier 1 — Critical"
    if score >= 7:
        return "Tier 2 — High Importance"
    if score >= 4:
        return "Tier 3 — Moderate"
    return "Tier 4 — Low"


def tier_number(tier):
    for number in (1, 2, 3, 4):
        if str(tier).startswith(f"Tier {number}"):
            return number
    return None


def inherent_level(score):
    if score <= 3:
        return "Low"
    if score <= 7:
        return "Medium"
    if score <= 11:
        return "High"
    return "Very High"


def derive_provisional_inherent(v, subs):
    """Creates visible mock-data mappings; every derived input is labelled provisional."""
    data = str(v.get("data_accessed", "None")).strip().lower()
    service = str(v.get("service_type", "")).strip().lower()
    legacy = str(v.get("criticality", "Low")).strip().lower()

    if "payment" in data or ("client pii" in data and "employee data" in data):
        data_score = 3
    elif any(term in data for term in ["client pii", "employee data", "security logs"]):
        data_score = 2
    elif data in {"", "none", "nan"}:
        data_score = 0
    else:
        data_score = 1

    if any(term in service for term in ["core", "cloud", "hosting", "infrastructure", "managed", "security", "api"]):
        system_score = 2
    elif any(term in service for term in ["software", "platform", "saas", "analytics"]):
        system_score = 1
    else:
        system_score = 0

    if any(term in (service + " " + data) for term in ["payment", "transaction", "core banking"]):
        customer_score = 3
    elif any(term in (service + " " + data) for term in ["client", "customer"]):
        customer_score = 2
    elif "employee" in data:
        customer_score = 1
    else:
        customer_score = 0

    delivery_score = {"critical": 3, "high": 2, "medium": 1, "low": 0}.get(legacy, 1)

    if subs.empty:
        fourth_score = 0
    else:
        hidden = sum(not truthy(x) for x in subs.get("disclosed_by_vendor", []))
        fourth_score = 3 if hidden > 1 else 2 if hidden == 1 else 1

    values = {
        "data_exposure": data_score,
        "system_access": system_score,
        "customer_transaction_exposure": customer_score,
        "delivery_exposure": delivery_score,
        "fourth_party_exposure": fourth_score,
    }
    sources = {
        "data_exposure": f"Modelled from imported data_accessed: {v.get('data_accessed', 'Not provided')}",
        "system_access": f"Provisional mapping from service_type: {v.get('service_type', 'Not provided')}",
        "customer_transaction_exposure": "Provisional mapping from service and data fields",
        "delivery_exposure": f"Provisional mapping from imported criticality: {v.get('criticality', 'Not provided')}",
        "fourth_party_exposure": f"Modelled from {len(subs)} subcontractor record(s)",
    }
    return values, sources


def finding_severity(base, tier):
    number = tier_number(tier)
    if base == "material":
        return "High" if number in {1, 2} else "Medium"
    return "Medium" if number in {1, 2} else "Low"


def build_findings(v, compliance, hidden, contract_days, tier):
    findings = []
    for status, docs in (("Missing", compliance["missing"]), ("Expired", compliance["expired"])):
        for doc in docs:
            severity = finding_severity("material", tier)
            findings.append({
                "vendor_id": v["vendor_id"], "vendor_name": v["name"],
                "severity": severity, "finding_type": f"{status} Evidence",
                "domain": "Information Security / Evidence",
                "description": f"Required document {status.lower()}: {doc}",
                "rationale": f"Severity reflects {tier} and the absence of a valid required artefact.",
            })

    if hidden:
        severity = finding_severity("material" if hidden > 1 else "limited", tier)
        findings.append({
            "vendor_id": v["vendor_id"], "vendor_name": v["name"],
            "severity": severity, "finding_type": "Fourth-Party Risk",
            "domain": "Fourth-Party Management",
            "description": f"{hidden} undisclosed subcontractor relationship(s) identified.",
            "rationale": "The transparency failure is assessed in proportion to service importance and dependency count.",
        })

    if contract_days is not None and contract_days < 0:
        severity = finding_severity("material", tier)
        findings.append({
            "vendor_id": v["vendor_id"], "vendor_name": v["name"],
            "severity": severity, "finding_type": "Contract",
            "domain": "Contract and Exit",
            "description": "Contract has expired and requires confirmation of the current legal basis for service continuation.",
            "rationale": "An expired contract is an active issue; an approaching date alone is not scored.",
        })
    return findings


def control_effectiveness(findings):
    severities = [item["severity"] for item in findings]
    high_count = severities.count("High")
    medium_count = severities.count("Medium")
    systemic_high = any(
        item.get("severity") == "High" and item.get("systemic")
        for item in findings
    )
    if "Critical" in severities or systemic_high:
        return "Ineffective"
    if high_count == 1 or medium_count >= 3:
        return "Partially Effective"
    if severities:
        return "Mostly Effective"
    return "Effective"


def residual_from_matrix(inherent, effectiveness):
    matrix = {
        "Low": {"Effective": "Low", "Mostly Effective": "Low", "Partially Effective": "Medium", "Ineffective": "High"},
        "Medium": {"Effective": "Low", "Mostly Effective": "Medium", "Partially Effective": "High", "Ineffective": "High"},
        "High": {"Effective": "Medium", "Mostly Effective": "High", "Partially Effective": "High", "Ineffective": "Critical"},
        "Very High": {"Effective": "High", "Mostly Effective": "High", "Partially Effective": "Critical", "Ineffective": "Critical"},
    }
    return matrix[inherent][effectiveness]


def treatment_for_rating(rating):
    return {
        "Low": ("Monitor", "Approval and normal monitoring."),
        "Medium": ("Monitor / Mitigate", "Approval may proceed with proportionate remediation where required."),
        "High": ("Mitigate / Accept", "Conditional approval, formal remediation, enhanced monitoring and senior risk acceptance."),
        "Critical": ("Avoid / Escalate", "Avoid or suspend unless an extraordinary time-bound exception is approved."),
    }.get(rating, ("Review Required", "Complete the assessment before approval."))


def monitoring_frequency(tier, rating):
    tier_frequency = {1: "Quarterly", 2: "Semi-annual", 3: "Annual", 4: "Event-driven"}.get(tier_number(tier), "Review Required")
    risk_frequency = {"Critical": "Monthly / continuous", "High": "Quarterly", "Medium": "Semi-annual", "Low": "Annual"}.get(rating, "Review Required")
    rank = {"Monthly / continuous": 0, "Quarterly": 1, "Semi-annual": 2, "Annual": 3, "Event-driven": 4, "Review Required": 5}
    return min([tier_frequency, risk_frequency], key=lambda value: rank[value])


def risk_engine(vendor, documents, subcontractors, requirements):
    v = vendor.iloc[0]
    vendor_id = v["vendor_id"]
    saved = assessment_row(vendor_id)
    subs = subcontractors[
        subcontractors["parent_vendor_id"] == vendor_id
    ] if not subcontractors.empty else pd.DataFrame()

    hidden = 0
    if not subs.empty and "disclosed_by_vendor" in subs.columns:
        hidden = sum(not truthy(x) for x in subs["disclosed_by_vendor"])

    manual_criticality = all(valid_assessment_value(saved.get(field)) for field in CRITICALITY_FIELDS)
    if manual_criticality:
        criticality_factors = {field: int(saved[field]) for field in CRITICALITY_FIELDS}
        criticality_score = sum(criticality_factors.values())
        tier = tier_from_score(criticality_score)
        criticality_source = "Factor assessment"
    else:
        criticality_factors = {}
        criticality_score = None
        tier = legacy_tier(v.get("criticality"))
        criticality_source = "Imported classification — complete factor assessment to verify"

    manual_inherent = all(valid_assessment_value(saved.get(field)) for field in INHERENT_FIELDS)
    if manual_inherent:
        inherent_factors = {field: int(saved[field]) for field in INHERENT_FIELDS}
        inherent_sources = {field: "Confirmed assessment input" for field in INHERENT_FIELDS}
        assessment_quality = "Verified"
    else:
        inherent_factors, inherent_sources = derive_provisional_inherent(v, subs)
        assessment_quality = "Provisional — review modelled inputs"

    inherent_score = sum(inherent_factors.values())
    inherent = inherent_level(inherent_score)
    compliance = compliance_engine(vendor, documents, requirements)
    contract_days = days_to_contract_end(v.get("contract_end_date"))
    contract_watch = contract_watch_item(contract_days)
    findings = build_findings(v, compliance, hidden, contract_days, tier)
    effectiveness = control_effectiveness(findings)
    calculated_residual = residual_from_matrix(inherent, effectiveness)

    override = str(saved.get("override_rating", "") or "").strip()
    override_reason = str(saved.get("override_reason", "") or "").strip()
    valid_override = override in {"Low", "Medium", "High", "Critical"} and bool(override_reason)
    final_residual = override if valid_override else calculated_residual
    treatment, treatment_copy = treatment_for_rating(final_residual)

    drivers = [
        (FIELD_LABELS[field], inherent_factors[field], 3, inherent_sources[field])
        for field in INHERENT_FIELDS
    ]

    return {
        "criticality_tier": tier,
        "criticality_score": criticality_score,
        "criticality_factors": criticality_factors,
        "criticality_source": criticality_source,
        "inherent_score": inherent_score,
        "inherent_level": inherent,
        "assessment_quality": assessment_quality,
        "drivers": drivers,
        "control_effectiveness": effectiveness,
        "calculated_residual": calculated_residual,
        "final_residual": final_residual,
        "level": final_residual,
        "risk_rank": RISK_ORDER[final_residual],
        "override_applied": valid_override,
        "override_reason": override_reason if valid_override else "",
        "override_review_date": saved.get("override_review_date", "") if valid_override else "",
        "treatment": treatment,
        "treatment_copy": treatment_copy,
        "monitoring": monitoring_frequency(tier, final_residual),
        "compliance": compliance,
        "hidden_subcontractors": hidden,
        "contract_days": contract_days,
        "contract_watch": contract_watch,
        "findings": findings,
        "pending_review": compliance["pending"],
    }


# ============================================================
# FINDINGS ENGINE
# ============================================================

def generate_findings(vendor, documents, subcontractors, requirements):
    return risk_engine(vendor, documents, subcontractors, requirements)["findings"]


# ============================================================
# LOAD DATA
# ============================================================

ensure_document_files_table()
ensure_vendor_assessments_table()

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
        <div>
            <span class="brand-mark">#</span>
            <span class="brand-title">IT RISK / GRC LAB</span>
        </div>
        <div class="brand-subtitle">Technology Risk - Cyber GRC - TPRM</div>
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
        "Sample Document Library",
        "Assessment Simulation",
        "IT Risk / GRC Practice Lab",
        "Data Import",
    ],
)

st.sidebar.markdown(
    """
    <div class="sidebar-caption">
        Portfolio project & practical training lab<br>
        IT Risk - Cyber GRC - TPRM
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if menu == "Executive Dashboard":

    page_header(
        "Portfolio Intelligence",
        "TPRM Risk Overview",
        "Executive view of exposure, evidence quality, supply-chain dependencies and remediation pressure.",
    )

    if vendors.empty:
        st.info("Import the mock dataset to activate the dashboard.")
        st.stop()

    results = []
    for _, vendor in vendors.iterrows():
        r = risk_engine(pd.DataFrame([vendor]), documents, subcontractors, requirements)
        results.append({
            "Vendor": vendor["name"], "Risk": r["level"], "Risk Rank": r["risk_rank"],
            "Criticality": r["criticality_tier"], "Inherent": r["inherent_level"],
            "Controls": r["control_effectiveness"], "Monitoring": r["monitoring"],
            "Contract Watch": r["contract_watch"]["status"] if r["contract_watch"] else "None",
            "Compliance": r["compliance"]["percentage"], "Hidden": r["hidden_subcontractors"],
            "Findings": len(generate_findings(pd.DataFrame([vendor]), documents, subcontractors, requirements)),
        })

    register = pd.DataFrame(results)

    critical = int(register["Criticality"].astype(str).str.startswith("Tier 1").sum())
    high_risk = int(register["Risk"].isin(["Critical", "High"]).sum())
    avg_compliance = int(register["Compliance"].mean())
    total_hidden = int(register["Hidden"].sum())
    open_findings = int(register["Findings"].sum())
    contract_watch_count = int((register["Contract Watch"] != "None").sum())

    overall = (
        "Critical" if high_risk >= 8
        else "High" if high_risk >= 4
        else "Medium" if high_risk >= 1
        else "Low"
    )

    st.markdown(
        f"""
        <div class="console-card">
            <div class="console-kicker">Executive Signal - Portfolio Posture</div>
            <div style="display:flex;justify-content:space-between;gap:2rem;align-items:end;">
                <div style="flex:1;">
                    <div class="console-title">Risk exposure requires active management</div>
                    <div class="console-copy">
                        {high_risk} of {len(vendors)} vendors are currently High or Critical risk.
                        Evidence compliance is {avg_compliance}% and {total_hidden} undisclosed
                        fourth-party relationship(s) are visible in the current dataset.
                    </div>
                </div>
                <div style="min-width:150px;text-align:right;">
                    <div class="console-score" style="font-size:1.65rem;">{overall}</div>
                    <div class="console-score-label">Portfolio Residual Risk</div>
                    <div style="margin-top:.45rem;">{badge(overall)}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    cards = [
        ("Vendors", len(vendors), "Assessment population"),
        ("Critical", critical, "Inherent criticality"),
        ("High / Critical", high_risk, "Immediate attention"),
        ("Evidence", f"{avg_compliance}%", "Portfolio compliance"),
        ("Open Findings", open_findings, "Remediation pressure"),
    ]
    for col, (label, value, note) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if contract_watch_count:
        st.info(
            f"{contract_watch_count} contract renewal watch item(s) require first-line review. "
            "These alerts do not affect residual risk unless an actual contract or exit issue is identified."
        )

    st.write("")

    left, right = st.columns([1.05, .95])

    with left:
        st.markdown(
            '<div class="section-card"><div class="section-title">Risk Exposure</div>',
            unsafe_allow_html=True,
        )

        distribution = register["Risk"].value_counts().reindex(
            ["Critical", "High", "Medium", "Low"], fill_value=0,
        )
        st.bar_chart(distribution, height=250)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown(
            '<div class="section-card"><div class="section-title">Executive Attention</div>',
            unsafe_allow_html=True,
        )
        attention = register[
            register["Risk"].isin(["Critical", "High"])
        ].sort_values(["Risk Rank", "Findings"], ascending=False).head(6)

        if attention.empty:
            st.success("No High or Critical risk vendors identified.")
        else:
            for _, row in attention.iterrows():
                st.markdown(
                    f"""
                    <div class="attention-row">
                        <div>
                            <div class="attention-name">{row["Vendor"]}</div>
                            <div class="attention-meta">
                                {row["Risk"]} risk - Evidence {row["Compliance"]}% -
                                {row["Findings"]} finding(s)
                            </div>
                        </div>
                        <div>{badge(row["Risk"])}</div>
                        <div class="attention-score" style="font-size:.68rem;">{row["Monitoring"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    if total_hidden:
        st.warning(
            f"{total_hidden} undisclosed fourth-party relationship(s) require review across the portfolio."
        )


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
        crit = st.selectbox("Imported Criticality", ["All", "Critical", "High", "Medium", "Low"])
    with c2:
        status = st.selectbox("Status", ["All"] + sorted(vendors["status"].astype(str).unique()))
    with c3:
        search = st.text_input("Search", placeholder="Vendor name or service...")

    filtered = vendors.copy()
    if crit != "All":
        filtered = filtered[filtered["criticality"].astype(str).str.lower() == crit.lower()]
    if status != "All":
        filtered = filtered[filtered["status"].astype(str) == status]
    if search:
        mask = (
            filtered["name"].astype(str).str.contains(search, case=False, na=False)
            | filtered["service_type"].astype(str).str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.divider()

    selected_name = st.selectbox(
        "Open Vendor Assessment",
        filtered["name"].tolist() if not filtered.empty else [],
    )

    if selected_name:
        vendor = vendors[vendors["name"] == selected_name]
        v = vendor.iloc[0]
        risk = risk_engine(vendor, documents, subcontractors, requirements)

        st.markdown(
            f"""
            <div class="console-card">
                <div class="console-kicker">Vendor Risk Profile - {v["status"]}</div>
                <div style="display:flex;justify-content:space-between;gap:2rem;align-items:center;">
                    <div>
                        <div class="console-title">{v["name"]}</div>
                        <div class="console-copy">
                            {v["service_type"]} - {v["data_accessed"]}<br>
                            Criticality: <strong>{risk["criticality_tier"]}</strong><br>
                            Assessment: <strong>{risk["assessment_quality"]}</strong>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div class="console-score" style="font-size:1.8rem;">{risk["final_residual"]}</div>
                        <div class="console-score-label">Final Residual Risk</div>
                        <div style="margin-top:.4rem;">{badge(risk["level"])}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="section-card">
                <div class="section-title">Risk Lifecycle</div>
                <div class="risk-flow">
                    <div class="risk-node">
                        <div class="risk-node-label">Inherent Risk</div>
                        <div class="risk-node-value">{risk["inherent_level"]} · {risk["inherent_score"]}/15</div>
                    </div>
                    <div class="risk-arrow">-></div>
                    <div class="risk-node">
                        <div class="risk-node-label">Control Effectiveness</div>
                        <div class="risk-node-value">{risk["control_effectiveness"]}</div>
                    </div>
                    <div class="risk-arrow">-></div>
                    <div class="risk-node">
                        <div class="risk-node-label">Residual Risk</div>
                        <div class="risk-node-value">{risk["final_residual"]}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if risk["criticality_factors"]:
            calculation = " + ".join(
                f'{FIELD_LABELS[field]} {value}'
                for field, value in risk["criticality_factors"].items()
            )
            st.caption(
                f'Criticality calculation: {calculation} = '
                f'{risk["criticality_score"]}/12 → {risk["criticality_tier"]}'
            )
        else:
            st.caption(
                f'Criticality source: {risk["criticality_source"]}. '
                "Open the assessment inputs to complete the transparent 0–12 factor calculation."
            )

        with st.expander("Assessment inputs and human override"):
            st.caption(
                "Confirm the inputs used by the model. Until all inherent-risk inputs are saved, "
                "the rating is clearly marked as provisional."
            )
            saved = assessment_row(v["vendor_id"])
            score_options = [None, 0, 1, 2, 3]
            score_labels = {
                None: "Review Required", 0: "0 — None / negligible",
                1: "1 — Limited", 2: "2 — Significant", 3: "3 — Severe",
            }

            def saved_index(field):
                value = saved.get(field)
                return score_options.index(int(value)) if valid_assessment_value(value) else 0

            with st.form(f"assessment_{v['vendor_id']}"):
                st.markdown("**Criticality factors**")
                criticality_values = {}
                crit_cols = st.columns(2)
                for index, field in enumerate(CRITICALITY_FIELDS):
                    with crit_cols[index % 2]:
                        criticality_values[field] = st.selectbox(
                            FIELD_LABELS[field], score_options, index=saved_index(field),
                            format_func=lambda value: score_labels[value], key=f"{field}_{v['vendor_id']}",
                        )

                st.markdown("**Inherent-risk factors**")
                inherent_values = {}
                inherent_cols = st.columns(2)
                for index, field in enumerate(INHERENT_FIELDS):
                    with inherent_cols[index % 2]:
                        inherent_values[field] = st.selectbox(
                            FIELD_LABELS[field], score_options, index=saved_index(field),
                            format_func=lambda value: score_labels[value], key=f"{field}_{v['vendor_id']}",
                        )

                st.markdown("**Human override — optional**")
                override_options = ["No override", "Low", "Medium", "High", "Critical"]
                current_override = str(saved.get("override_rating", "") or "")
                override_default = override_options.index(current_override) if current_override in override_options else 0
                override_rating = st.selectbox("Final rating override", override_options, index=override_default)
                override_reason = st.text_area(
                    "Override reason", value=str(saved.get("override_reason", "") or ""),
                    placeholder="Required when an override is selected.",
                )
                override_review_date = st.text_input(
                    "Override review date", value=str(saved.get("override_review_date", "") or ""),
                    placeholder="YYYY-MM-DD",
                )

                if st.form_submit_button("Save Assessment", type="primary", use_container_width=True):
                    if override_rating != "No override" and not override_reason.strip():
                        st.error("Document the reason before applying a human override.")
                    else:
                        save_vendor_assessment(v["vendor_id"], {
                            **criticality_values, **inherent_values,
                            "override_rating": "" if override_rating == "No override" else override_rating,
                            "override_reason": override_reason.strip(),
                            "override_review_date": override_review_date.strip(),
                        })
                        st.success("Assessment saved.")
                        st.rerun()

        left, right = st.columns([1.05, .95])
        with left:
            st.markdown(
                '<div class="section-card"><div class="section-title">Risk Drivers</div>',
                unsafe_allow_html=True,
            )
            for name, value, maximum, source in risk["drivers"]:
                pct = int(value / maximum * 100) if maximum else 0
                st.markdown(
                    f"""
                    <div class="driver-row">
                        <span class="driver-name">{name}</span>
                        <span class="driver-score">{value}/{maximum}</span>
                    </div>
                    <div style="height:3px;background:#1a212b;border-radius:2px;margin:-.25rem 0 .35rem;">
                        <div style="width:{pct}%;height:3px;background:#ffb020;border-radius:2px;"></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.caption(source)
            st.markdown(
                f'**Inherent Risk Total: {risk["inherent_score"]}/15 — {risk["inherent_level"]}**'
            )
            st.caption(
                f'Assessment status: {risk["assessment_quality"]}. '
                "Modelled inputs remain visible and should be confirmed by a reviewer."
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(
                '<div class="section-card"><div class="section-title">Contract & Operational Context</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="signal"><span class="signal-name">Criticality</span><span class="signal-value">{risk["criticality_tier"]}</span></div>
                <div class="signal"><span class="signal-name">Criticality source</span><span class="signal-value">{risk["criticality_source"]}</span></div>
                <div class="signal"><span class="signal-name">Vendor status</span><span class="signal-value">{v["status"]}</span></div>
                <div class="signal"><span class="signal-name">Onboarded</span><span class="signal-value">{v["onboarded_date"]}</span></div>
                <div class="signal"><span class="signal-name">Contract end</span><span class="signal-value">{v["contract_end_date"]}</span></div>
                """,
                unsafe_allow_html=True,
            )
            days = risk["contract_days"]
            if days is not None:
                if days < 0:
                    st.error("Contract expired.")
                elif days <= 90:
                    st.caption(f"Contract expires in {days} days — operational watch active.")
                else:
                    st.success(f"{days} days remaining.")
            st.markdown("</div>", unsafe_allow_html=True)

        if risk["contract_watch"]:
            watch = risk["contract_watch"]
            st.warning(
                f'Contract Watch Item — {watch["status"]}\n\n'
                f'**{watch["days"]} days remaining.** {watch["action"]}\n\n'
                f'Owner: {watch["owner"]}  \n'
                f'Risk impact: {watch["risk_impact"]}.'
            )

        st.markdown(
            '<div class="section-card"><div class="section-title">Residual Risk Decision Trace</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="signal"><span class="signal-name">Inherent Risk</span><span class="signal-value">{risk["inherent_level"]}</span></div>
            <div class="signal"><span class="signal-name">Control Effectiveness</span><span class="signal-value">{risk["control_effectiveness"]}</span></div>
            <div class="signal"><span class="signal-name">Calculated Residual Risk</span><span class="signal-value">{risk["calculated_residual"]}</span></div>
            <div class="signal"><span class="signal-name">Human Override</span><span class="signal-value">{'Applied' if risk["override_applied"] else 'None'}</span></div>
            <div class="signal"><span class="signal-name">Final Residual Risk</span><span class="signal-value">{risk["final_residual"]}</span></div>
            """,
            unsafe_allow_html=True,
        )
        if risk["override_applied"]:
            st.warning(
                f'Override rationale: {risk["override_reason"]} · '
                f'Review date: {risk["override_review_date"] or "Not provided"}'
            )
        st.caption(
            "Matrix rule: the final calculated rating is the intersection of Inherent Risk "
            "and Control Effectiveness. Criticality determines oversight frequency and is not added as a penalty."
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Evidence Posture + attach/view files ---
        st.markdown(
            '<div class="section-card"><div class="section-title">Evidence Posture</div>',
            unsafe_allow_html=True,
        )
        ec1, ec2, ec3, ec4 = st.columns(4)
        ec1.metric("Coverage", f'{risk["compliance"]["percentage"]}%')
        ec2.metric("Received", risk["compliance"]["received"])
        ec3.metric("Missing", len(risk["compliance"]["missing"]))
        ec4.metric("Expired", len(risk["compliance"]["expired"]))

        evidence_items = []
        for doc in risk["compliance"]["missing"]:
            evidence_items.append(("Missing", doc))
        for doc in risk["compliance"]["expired"]:
            evidence_items.append(("Expired", doc))
        for doc in risk["compliance"]["pending"]:
            evidence_items.append(("Pending", doc))

        if evidence_items:
            for status_, doc in evidence_items:
                attached = get_document_file(v["vendor_id"], doc)
                st.markdown(
                    f"""
                    <div class="signal">
                        <span class="signal-name">{doc}</span>
                        <span>{badge(status_)}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander(f"Attach / view file - {doc}"):
                    if attached is not None:
                        st.caption(f"Currently attached: {attached['filename']} ({attached['uploaded_at']})")
                        render_file_preview(attached, height=350)
                    up = st.file_uploader(
                        "Upload evidence file", type=["pdf", "png", "jpg", "jpeg"],
                        key=f"upload_{v['vendor_id']}_{doc}",
                    )
                    if up is not None:
                        save_document_file(v["vendor_id"], doc, up.name, up.type, up.getvalue())
                        st.success("File attached. Reopen this panel to preview it.")
        else:
            st.success("No evidence gaps identified by the current compliance engine.")
        if risk["pending_review"]:
            st.caption(
                "Pending evidence is shown for follow-up but does not reduce Control Effectiveness "
                "until a due date or an actual overdue exposure is established."
            )
        st.markdown("</div>", unsafe_allow_html=True)

        generated = generate_findings(vendor, documents, subcontractors, requirements)

        st.markdown(
            '<div class="section-card"><div class="section-title">Recommended Risk Treatment</div>',
            unsafe_allow_html=True,
        )
        treatment_title = risk["treatment"]
        treatment_copy = risk["treatment_copy"] + f' Monitoring frequency: {risk["monitoring"]}.'

        st.markdown(
            f"""
            <div class="treatment-card">
                <div class="treatment-title">{treatment_title}</div>
                <div class="treatment-copy">{treatment_copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-card"><div class="section-title">Open Findings</div>',
            unsafe_allow_html=True,
        )
        if not generated:
            st.success("No findings generated for this vendor.")
        else:
            for f in generated:
                cls = f["severity"].lower()
                st.markdown(
                    f"""
                    <div class="finding {cls}">
                        <div class="finding-title">{f["severity"]} - {f["finding_type"]}</div>
                        <div class="finding-detail">{f["domain"]} · {f["description"]}</div>
                        <div class="finding-detail">Rationale: {f["rationale"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)


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
        r = risk_engine(pd.DataFrame([vendor]), documents, subcontractors, requirements)
        rows.append({
            "Vendor": vendor["name"], "Criticality": r["criticality_tier"],
            "Inherent Risk": r["inherent_level"],
            "Control Effectiveness": r["control_effectiveness"],
            "Residual Risk": r["level"], "Risk Rank": r["risk_rank"],
            "Assessment": r["assessment_quality"],
            "Treatment": r["treatment"], "Monitoring": r["monitoring"],
            "Contract Watch": r["contract_watch"]["status"] if r["contract_watch"] else "None",
            "Evidence": f'{r["compliance"]["percentage"]}%',
            "Findings": len(generate_findings(pd.DataFrame([vendor]), documents, subcontractors, requirements)),
            "Hidden 4th Parties": r["hidden_subcontractors"],
            "Contract End": vendor["contract_end_date"],
        })

    register = pd.DataFrame(rows)
    selected = st.multiselect(
        "Risk level", ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"],
    )
    view = register[register["Residual Risk"].isin(selected)].sort_values(
        ["Risk Rank", "Findings"], ascending=False
    ).drop(columns=["Risk Rank"])
    st.dataframe(view, use_container_width=True, hide_index=True)
    st.download_button(
        "Export Risk Register", view.to_csv(index=False).encode("utf-8"),
        "tprm_risk_register.csv", "text/csv",
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
        generated = generate_findings(pd.DataFrame([vendor]), documents, subcontractors, requirements)
        for f in generated:
            rows.append({
                "Finding ID": f"F-{finding_id:03d}", "Vendor": f["vendor_name"],
                "Severity": f["severity"], "Type": f["finding_type"],
                "Domain": f["domain"], "Description": f["description"],
                "Rationale": f["rationale"], "Status": "Open",
                "Owner": "Relationship Owner — First Line",
            })
            finding_id += 1

    finding_df = pd.DataFrame(rows)

    if finding_df.empty:
        st.success("No open findings.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Open Findings", len(finding_df))
        c2.metric("High / Critical", int(finding_df["Severity"].isin(["High", "Critical"]).sum()))
        c3.metric("Vendors Affected", finding_df["Vendor"].nunique())

        st.dataframe(finding_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Export Findings", finding_df.to_csv(index=False).encode("utf-8"),
            "tprm_findings.csv", "text/csv",
        )
        st.info(
            "Findings are generated dynamically from evidence and supply-chain data. "
            "A future evolution can persist owner, due date, comments and closure evidence directly in SQLite."
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
        left_on="parent_vendor_id", right_on="vendor_id", how="left",
    )
    hidden = merged[~merged["disclosed_by_vendor"].apply(truthy)]

    c1, c2, c3 = st.columns(3)
    c1.metric("Subcontractors", len(merged))
    c2.metric("Undisclosed", len(hidden))
    c3.metric("Vendors Exposed", hidden["name"].nunique())

    st.write("")
    st.dataframe(
        merged[["name", "criticality", "subcontractor_name", "service_provided", "disclosed_by_vendor"]],
        use_container_width=True, hide_index=True,
    )

    st.subheader("Supply-Chain Findings")
    for _, row in hidden.iterrows():
        st.markdown(
            f"""
            <div class="finding">
                <div class="finding-title">{row["name"]} -> {row["subcontractor_name"]}</div>
                <div class="finding-detail">
                    {row["service_provided"]} - {row["criticality"]} primary vendor - Undisclosed relationship
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
        "Assess whether required evidence is present, valid and current - and attach the actual files.",
    )

    if vendors.empty:
        st.stop()

    selected = st.selectbox("Vendor", vendors["name"].tolist())
    vendor = vendors[vendors["name"] == selected]
    v = vendor.iloc[0]
    vendor_id = v["vendor_id"]

    result = compliance_engine(vendor, documents, requirements)

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

    req = requirements[
        requirements["criticality"].astype(str).str.lower() == str(v["criticality"]).lower()
    ]
    for doc in req["required_document"].tolist():
        if doc in ["ISO 27001 Certificate", "SOC 2 Report"]:
            continue
        if document_status(vendor_id, doc, documents) == "Received":
            rows.append([doc, "Received"])

    if str(v["criticality"]).lower() == "high":
        iso = document_status(vendor_id, "ISO 27001 Certificate", documents)
        soc = document_status(vendor_id, "SOC 2 Report", documents)
        if iso == "Received" or soc == "Received":
            rows.append(["ISO 27001 / SOC 2", "Received"])

    st.markdown('<div class="section-card"><div class="section-title">Required Evidence</div>', unsafe_allow_html=True)
    for doc, status_ in rows:
        attached = get_document_file(vendor_id, doc)
        attach_tag = " - file attached" if attached is not None else ""
        st.markdown(
            f"""
            <div class="signal">
                <span class="signal-name">{doc}{attach_tag}</span>
                <span>{badge(status_)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander(f"Attach / view file - {doc}"):
            if attached is not None:
                st.caption(f"Currently attached: {attached['filename']} ({attached['uploaded_at']})")
                render_file_preview(attached, height=380)
            else:
                sample = MOCK_TEMPLATES.get(doc.split(" / ")[0])
                if sample:
                    st.caption("No file attached yet. Not sure what this document looks like?")
                    if st.button(f"Preview an illustrative sample of '{doc}'", key=f"sample_btn_{doc}"):
                        sample_bytes = generate_mock_document(doc.split(" / ")[0])
                        b64 = base64.b64encode(sample_bytes).decode("utf-8")
                        st.markdown(
                            f"""
                            <div class="doc-preview-frame">
                                <iframe src="data:application/pdf;base64,{b64}"
                                    width="100%" height="380" style="border:none;"></iframe>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            up = st.file_uploader(
                "Upload real evidence file", type=["pdf", "png", "jpg", "jpeg"],
                key=f"dc_upload_{vendor_id}_{doc}",
            )
            if up is not None:
                save_document_file(vendor_id, doc, up.name, up.type, up.getvalue())
                st.success("File attached. Reopen this panel to preview it.")
    st.markdown("</div>", unsafe_allow_html=True)

    if result["percentage"] == 100:
        st.success("Evidence set is fully compliant.")
    elif result["expired"]:
        st.error("Expired evidence requires remediation.")
    elif result["missing"]:
        st.warning("Missing evidence requires follow-up.")
    else:
        st.info("Evidence is partially complete; pending items remain.")


# ============================================================
# SAMPLE DOCUMENT LIBRARY
# ============================================================

elif menu == "Sample Document Library":

    page_header(
        "Reference Library",
        "Sample Document Library",
        "Never seen a real ISO 27001 certificate or SOC 2 report? These illustrative mockups show the typical structure.",
    )

    st.warning(
        "WARNING These are fictional, generated examples for training purposes only - "
        "not issued by any certification body and not valid for any real assessment."
    )

    for doc_type, template in MOCK_TEMPLATES.items():
        st.markdown(
            f"""
            <div class="sample-card">
                <div class="sample-title">{doc_type}</div>
                <div class="sample-copy">{template["subheading"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_a, col_b = st.columns([1, 4])
        with col_a:
            preview_clicked = st.button("Preview", key=f"lib_preview_{doc_type}")
        with col_b:
            sample_bytes = generate_mock_document(doc_type)
            st.download_button(
                "Download sample PDF", sample_bytes,
                f"SAMPLE_{doc_type.replace(' ', '_').replace('/', '_')}.pdf",
                "application/pdf", key=f"lib_dl_{doc_type}",
            )
        if preview_clicked:
            b64 = base64.b64encode(sample_bytes).decode("utf-8")
            st.markdown(
                f"""
                <div class="doc-preview-frame">
                    <iframe src="data:application/pdf;base64,{b64}"
                        width="100%" height="480" style="border:none;"></iframe>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.write("")


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

    selected_name = st.selectbox("Choose a case", vendors["name"].tolist())
    vendor = vendors[vendors["name"] == selected_name]
    v = vendor.iloc[0]
    case_model = risk_engine(vendor, documents, subcontractors, requirements)

    st.markdown(
        f"""
        <div class="section-card">
            <div class="section-title">Case File</div>
            <b>Vendor:</b> {v["name"]}<br>
            <b>Service:</b> {v["service_type"]}<br>
            <b>Data accessed:</b> {v["data_accessed"]}<br>
            <b>Criticality:</b> {case_model["criticality_tier"]}<br>
            <b>Assessment status:</b> {case_model["assessment_quality"]}<br>
            <b>Status:</b> {v["status"]}<br>
            <b>Contract end:</b> {v["contract_end_date"]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Your Assessment")

    answer_risk = st.radio(
        "1. What is the overall risk level?",
        ["Low", "Medium", "High", "Critical"], horizontal=True,
    )
    answer_fourth = st.radio(
        "2. Is there a fourth-party risk?",
        ["Yes", "No"], horizontal=True,
    )
    answer_evidence = st.multiselect(
        "3. Which evidence issues should be investigated?",
        ["Missing documents", "Expired documents", "Pending documents",
         "Contract expiry", "Undisclosed subcontractors"],
    )

    if st.button("Submit Assessment", type="primary"):
        model = case_model
        actual_risk = model["level"]
        actual_fourth = "Yes" if model["hidden_subcontractors"] > 0 else "No"

        expected_evidence = set()
        if model["compliance"]["missing"]:
            expected_evidence.add("Missing documents")
        if model["compliance"]["expired"]:
            expected_evidence.add("Expired documents")
        if model["compliance"]["pending"]:
            expected_evidence.add("Pending documents")
        if model["contract_days"] is not None and model["contract_days"] < 0:
            expected_evidence.add("Contract expiry")
        if model["hidden_subcontractors"]:
            expected_evidence.add("Undisclosed subcontractors")

        risk_correct = answer_risk == actual_risk
        fourth_correct = answer_fourth == actual_fourth
        evidence_correct = expected_evidence == set(answer_evidence)

        st.divider()
        st.subheader("Assessment Result")

        if risk_correct:
            st.success(f"OK Risk level correct: {actual_risk}")
        else:
            st.error(f"Risk level: your answer was {answer_risk}; model assessment is {actual_risk}.")

        if fourth_correct:
            st.success(f"OK Fourth-party answer correct: {actual_fourth}")
        else:
            st.error(f"Fourth-party risk: your answer was {answer_fourth}; model assessment is {actual_fourth}.")

        if evidence_correct:
            st.success("OK Evidence issue identification is correct.")
        else:
            st.warning("Evidence issue identification differs from the model.")

        st.markdown(
            f"""
            <div class="score-box">
                <div class="metric-label">Model Assessment</div>
                <div class="score-number" style="font-size:1.55rem;">{model["level"]}</div>
                <div style="color:#b7c0d6;margin-top:.45rem;">
                    {model["criticality_tier"]} · Inherent {model["inherent_level"]} ·
                    Controls {model["control_effectiveness"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")
        st.write("**Transparent inherent-risk calculation:**")
        for name, value, maximum, source in model["drivers"]:
            st.write(f"- {name}: {value}/{maximum} — {source}")
        st.write(f'**Total:** {model["inherent_score"]}/15 — {model["inherent_level"]}')

        st.info(
            "This is a training model, not a production risk methodology. "
            "In a real organization, scoring should be aligned with approved "
            "risk appetite, control frameworks and governance."
        )


# ============================================================
# IT RISK / GRC PRACTICE LAB
# ============================================================

elif menu == "IT Risk / GRC Practice Lab":

    page_header(
        "Hands-on Practice",
        "IT Risk / GRC Practice Lab",
        "Learn how the technology works first, then investigate evidence, form a risk view and map it to DORA, NIS2 and ISO 27001.",
    )

    st.markdown(
        """
        <div class="console-card">
            <div class="console-kicker">How to use this lab</div>
            <div class="console-title">Learn -> Read -> Investigate -> Assess</div>
            <div class="console-copy">
                You are not expected to understand an unfamiliar technical screen immediately.
                Start with <strong>Learn the Environment</strong>, then use the guided questions.
                The independent assessment comes only after you understand what the evidence is showing.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    practice_cases = {
        "IAM-001 - Non-human identity with static secret": {
            "domain": "IAM / Non-human identities",
            "difficulty": "Foundation",
            "learning_goal": "Understand how an application can have its own identity and authenticate without a human user or MFA.",
            "plain_story": (
                "A payment application needs to connect automatically to another system every night. "
                "No employee is sitting at a keyboard, so the application needs its own digital identity. "
                "In this case that identity is called a service principal. It proves who it is using a client secret "
                "stored in Azure Key Vault."
            ),
            "glossary": [
                ("Service principal", "An identity representing an application/service rather than a person."),
                ("Non-human identity", "An account or identity used by software, automation or a workload."),
                ("Client ID", "The public identifier of the application identity - similar to a username."),
                ("Client secret", "A secret credential used by the application to prove its identity - similar to a password."),
                ("Key Vault", "A protected Azure service used to store secrets, keys and certificates."),
                ("API permission", "Defines what the application is allowed to do in another service."),
                ("Managed Identity", "An Azure-managed application identity that can avoid manually storing/rotating a client secret."),
                ("Rotation", "Replacing an old credential with a new one on a controlled schedule."),
            ],
            "screen_help": {
                "Identity record": [
                    ("Object", "Name of the application identity."),
                    ("Type", "Tells us this is a service principal, not a human user."),
                    ("Owner", "Team accountable for the identity."),
                    ("Last sign-in", "Last time the application identity authenticated."),
                    ("Privileged role", "Whether it holds an administrative/high-privilege role."),
                ],
                "Credential inventory": [
                    ("Credential", "How the application authenticates."),
                    ("Created / Expires", "Lifetime of the credential."),
                    ("Last rotated", "Whether the credential has ever been replaced."),
                    ("Storage", "Where the secret is kept."),
                ],
                "API permissions": [
                    ("Permission", "What actions the application can perform."),
                    ("Type = Application", "Permission is granted to the application itself, not inherited from a signed-in user."),
                    ("Admin consent", "Whether an administrator approved the permission."),
                ],
                "Key Vault access": [
                    ("Principal", "User/group/application with access to the vault."),
                    ("Get/List/Set", "Actions the principal can perform on secrets."),
                    ("Members", "How many people/accounts are behind the group."),
                ],
                "Sign-in telemetry": [
                    ("Source", "Where the authentication came from."),
                    ("Result", "Whether authentication succeeded or failed."),
                    ("Auth", "Authentication method used."),
                ],
            },
            "context": (
                "A payment-reconciliation application uses a service principal to access an internal API. "
                "During a quarterly access review, the account is flagged because MFA is not configured. "
                "The application owner says MFA is not applicable because the identity is non-human."
            ),
            "mission": "Work out whether 'no MFA' is actually the problem, and identify what really matters for this application identity.",

            "shadowing": [
                {
                    "step": "1. Identify what kind of identity this is",
                    "senior": (
                        "I start with the Identity record. Type says Service principal, so this is not a human user account. "
                        "That immediately changes how I think about MFA. I would not raise a finding just because MFA is absent."
                    ),
                    "why": "The first job is to understand what object you are reviewing before applying a control designed for a different object.",
                    "next": "Now I need to understand how this application proves its identity."
                },
                {
                    "step": "2. Check the authentication method",
                    "senior": (
                        "Credential inventory says Client secret. That means the application authenticates with a stored secret. "
                        "Now the control question becomes credential protection and lifecycle, not human MFA."
                    ),
                    "why": "Static credentials can be copied or exposed, so storage, rotation, ownership and monitoring matter.",
                    "next": "I check where the secret is stored and how long it has existed."
                },
                {
                    "step": "3. Inspect credential lifecycle",
                    "senior": (
                        "The secret is stored in Key Vault, which is good context, but I also see Last rotated: Never. "
                        "That gets my attention. I still do not call it a finding yet because I need the applicable policy and technical constraints."
                    ),
                    "why": "A control concern becomes a finding only when you know the expected control and have evidence that it is not met.",
                    "next": "I ask for the credential rotation standard and whether Managed Identity or certificate authentication is feasible."
                },
                {
                    "step": "4. Review who can access the credential",
                    "senior": (
                        "The application can Get the secret, but the Payments-App-Admins group can Get, List and Set, with 12 members. "
                        "I want to know who those 12 people are and whether all of them need that level of access."
                    ),
                    "why": "Protecting a secret is not only about where it is stored. It is also about who can retrieve or change it.",
                    "next": "Request group membership, access-review evidence and privileged activity logs."
                },
                {
                    "step": "5. Form a preliminary risk view",
                    "senior": (
                        "My preliminary view is not 'MFA missing'. It is: a production workload depends on a long-lived static secret that has never been rotated, "
                        "and I need to validate least privilege, monitoring and whether a stronger authentication design is feasible."
                    ),
                    "why": "This turns raw technical facts into a risk statement without overclaiming.",
                    "next": "Only after policy/evidence review would I decide whether this is a formal finding and its severity."
                },
            ],
            "guided_steps": [
                {
                    "question": "1. Is this account used by a human being?",
                    "hint": "Look at Type in the Identity record.",
                    "answer": "No. It is a service principal used by an application.",
                },
                {
                    "question": "2. If no human is typing a password, how does the application authenticate?",
                    "hint": "Open Credential inventory and Sign-in telemetry.",
                    "answer": "It authenticates using a client secret.",
                },
                {
                    "question": "3. Where is that credential stored?",
                    "hint": "Look at Storage in Credential inventory.",
                    "answer": "Azure Key Vault.",
                },
                {
                    "question": "4. What fact should make you ask a follow-up question about credential lifecycle?",
                    "hint": "Compare Created, Expires and Last rotated.",
                    "answer": "The client secret is long-lived and has never been rotated.",
                },
                {
                    "question": "5. What would you inspect next before calling this secure or insecure?",
                    "hint": "Think ownership, access to the vault, permissions and monitoring.",
                    "answer": "Who can retrieve/change the secret, whether the permissions are necessary, whether activity is monitored, and whether a safer authentication design is possible.",
                },
            ],
            "evidence": {
                "Identity record": pd.DataFrame([
                    {"Object": "svc-pay-recon-prod", "Type": "Service principal", "Owner": "Payments Apps", "Created": "2024-02-11", "Last sign-in": "2026-08-23 03:14", "Privileged role": "No"},
                ]),
                "Credential inventory": pd.DataFrame([
                    {"Credential": "Client secret", "Created": "2024-02-11", "Expires": "2027-02-11", "Last rotated": "Never", "Storage": "Azure Key Vault"},
                ]),
                "API permissions": pd.DataFrame([
                    {"Permission": "Payments.Read.All", "Type": "Application", "Admin consent": "Granted"},
                    {"Permission": "Reconciliation.Write", "Type": "Application", "Admin consent": "Granted"},
                ]),
                "Key Vault access": pd.DataFrame([
                    {"Principal": "Payments-App-Admins", "Access": "Secrets: Get/List/Set", "Members": 12},
                    {"Principal": "svc-pay-recon-prod", "Access": "Secrets: Get", "Members": "N/A"},
                ]),
                "Sign-in telemetry": pd.DataFrame([
                    {"Time": "2026-08-23 03:14", "Source": "10.20.18.44", "Result": "Success", "Auth": "Client secret"},
                    {"Time": "2026-08-22 03:13", "Source": "10.20.18.44", "Result": "Success", "Auth": "Client secret"},
                    {"Time": "2026-08-21 03:14", "Source": "10.20.18.44", "Result": "Success", "Auth": "Client secret"},
                ]),
            },
            "issues": [
                "The absence of MFA is not the main question for a non-human workload identity.",
                "The application relies on a long-lived static client secret that has never been rotated.",
                "Key Vault administrative access should be validated against least privilege.",
                "Authentication design, credential protection, rotation, ownership, permissions and monitoring are the relevant control areas.",
            ],
            "questions": [
                "Why is a client secret used instead of managed identity or certificate authentication?",
                "What credential-rotation standard applies and does this secret comply?",
                "Who can retrieve or modify this secret in Key Vault?",
                "Are the API permissions necessary for the application's function?",
                "Are unusual service-principal sign-ins monitored and alerted?",
                "Who owns this identity and how is ownership recertified?",
            ],
            "severity": "High",
            "frameworks": {
                "DORA": "ICT risk-management controls around identity, access, secure configuration, protection and monitoring.",
                "NIS2": "Cybersecurity risk-management measures including access control, asset management and secure operation.",
                "ISO 27001": "Identity management, authentication information, access rights, privileged access, logging and monitoring.",
                "IT Risk": "IAM - workload identity - secrets management - least privilege - monitoring",
            },
            "remediation": "Prefer managed identity where technically feasible; otherwise strengthen credential lifecycle, restrict Key Vault access, confirm least privilege, document ownership and monitor workload sign-ins.",
        },

        "CLD-002 - Public cloud storage exposure": {
            "domain": "Cloud / Data protection",
            "difficulty": "Foundation",
            "learning_goal": "Learn the difference between public network reachability and anonymous/public data access.",
            "plain_story": (
                "A cloud storage account contains customer data. The storage service can currently be reached over the public network, "
                "but anonymous access to the files is disabled. Those are two different controls: reachable from the internet does not automatically "
                "mean anyone can read the data, but it increases the attack surface and means access restrictions matter even more."
            ),
            "glossary": [
                ("Object storage", "Cloud storage for files/objects, such as Azure Blob Storage or Amazon S3."),
                ("Public network access", "The service has a network endpoint reachable through the public network."),
                ("Anonymous access", "Whether someone can access data without authenticating."),
                ("Default network action", "What happens to network traffic that does not match a specific network rule."),
                ("Private endpoint", "A private network path to a cloud service that avoids public-network exposure."),
                ("RBAC", "Role-Based Access Control - permissions are granted through defined roles."),
                ("Encryption at rest", "Stored data is encrypted on disk/storage."),
                ("Secure transfer", "Connections are required to use encrypted transport such as HTTPS/TLS."),
            ],
            "screen_help": {
                "Storage configuration": [
                    ("Public network access", "Whether the service accepts connections through a public endpoint."),
                    ("Anonymous blob access", "Whether unauthenticated users can read blobs."),
                    ("Default network action", "Whether unmatched network traffic is allowed or denied."),
                    ("Encryption at rest", "Whether stored data is encrypted."),
                    ("Secure transfer required", "Whether encrypted network transport is mandatory."),
                ],
                "Data classification": [
                    ("Classification", "Sensitivity of the information stored."),
                    ("Retention", "How long the data is kept."),
                ],
                "Access assignments": [
                    ("Principal", "Identity/group allowed to access the storage."),
                    ("Role", "What that identity/group can do."),
                    ("Scope", "How broadly the permission applies."),
                ],
                "Logging status": [
                    ("Read / Write / Delete logs", "Whether activity is recorded."),
                    ("Retention", "How long logs remain available."),
                    ("Alert", "Whether suspicious patterns trigger detection."),
                ],
            },
            "context": (
                "A customer-analytics workload stores exported client files in cloud object storage. "
                "A scan reports that public-network access is enabled. The cloud team says there is no issue because anonymous access is disabled."
            ),
            "mission": "Understand what is exposed, what is not, and which controls you need to inspect before deciding whether the risk is acceptable.",

            "shadowing": [
                {
                    "step": "1. Separate network exposure from anonymous data access",
                    "senior": (
                        "I see Public network access: Enabled, but Anonymous blob access: Disabled. "
                        "So I do not say 'the data is public'. I say the service is reachable over the public network but still requires authentication."
                    ),
                    "why": "Public reachability and public/anonymous data access are different control questions.",
                    "next": "Now I check whether the network exposure is necessary and how access is controlled."
                },
                {
                    "step": "2. Check data sensitivity",
                    "senior": (
                        "The dataset is Confidential / Client PII. That increases the impact if access control or network restrictions fail."
                    ),
                    "why": "Risk depends on both likelihood/exposure and impact. Sensitive data raises the impact side.",
                    "next": "I inspect RBAC and who can read or modify the storage."
                },
                {
                    "step": "3. Review access assignments",
                    "senior": (
                        "I see an application identity with Contributor and a Data-Analytics-Team group with Reader access. "
                        "The table does not tell me whether every member still needs access, so I need membership and recertification evidence."
                    ),
                    "why": "A role name alone does not prove least privilege.",
                    "next": "Request group membership, business justification and the latest access review."
                },
                {
                    "step": "4. Review logging and monitoring",
                    "senior": (
                        "Read and write/delete operations are logged, which is positive. But Unusual external source alert is disabled. "
                        "So logging exists, but detection may be weak."
                    ),
                    "why": "Logging records activity; monitoring/alerting helps detect suspicious activity in time.",
                    "next": "Ask what detections exist for unusual source IPs, geographies, bulk reads or abnormal access."
                },
                {
                    "step": "5. Form a preliminary risk view",
                    "senior": (
                        "I would not say 'customer data is exposed to the internet'. I would say a public-network reachable storage account holds confidential PII, "
                        "so I need to validate network necessity, least privilege and detective controls before concluding whether the configuration is acceptable."
                    ),
                    "why": "Precise wording prevents overstating the evidence.",
                    "next": "Compare the current design with cloud security standards and approved architecture."
                },
            ],
            "guided_steps": [
                {
                    "question": "1. Can an anonymous internet user simply download the customer files?",
                    "hint": "Look at Anonymous blob access.",
                    "answer": "Not from the evidence provided. Anonymous access is disabled.",
                },
                {
                    "question": "2. Does that mean the storage service is not reachable over the public network?",
                    "hint": "Look at Public network access and Default network action.",
                    "answer": "No. Public network access is enabled and the default network action is Allow.",
                },
                {
                    "question": "3. Why does the data classification matter?",
                    "hint": "Look at the dataset stored here.",
                    "answer": "It contains confidential client PII, so network exposure and access control deserve stronger scrutiny.",
                },
                {
                    "question": "4. What access-control question would you ask next?",
                    "hint": "Look at Data-Analytics-Team.",
                    "answer": "Who is in the group, whether all members need access, and when the access was last reviewed.",
                },
                {
                    "question": "5. What detective-control gap can you already see?",
                    "hint": "Open Logging status.",
                    "answer": "Logging exists, but there is no alert for unusual external-source access.",
                },
            ],
            "evidence": {
                "Storage configuration": pd.DataFrame([
                    {"Setting": "Public network access", "Value": "Enabled"},
                    {"Setting": "Anonymous blob access", "Value": "Disabled"},
                    {"Setting": "Default network action", "Value": "Allow"},
                    {"Setting": "Encryption at rest", "Value": "Enabled (platform-managed key)"},
                    {"Setting": "Secure transfer required", "Value": "Enabled"},
                ]),
                "Data classification": pd.DataFrame([
                    {"Dataset": "customer_export_daily.csv", "Classification": "Confidential / Client PII", "Retention": "90 days"},
                ]),
                "Access assignments": pd.DataFrame([
                    {"Principal": "analytics-prod-mi", "Role": "Storage Blob Data Contributor", "Scope": "Container"},
                    {"Principal": "Data-Analytics-Team", "Role": "Storage Blob Data Reader", "Scope": "Storage account"},
                ]),
                "Logging status": pd.DataFrame([
                    {"Log": "Read operations", "Enabled": "Yes", "Retention": "30 days"},
                    {"Log": "Write/Delete operations", "Enabled": "Yes", "Retention": "30 days"},
                    {"Alert": "Unusual external source", "Enabled": "No"},
                ]),
            },
            "issues": [
                "Anonymous access is disabled, but public-network reachability still increases the attack surface.",
                "The broad reader group should be tested for least privilege and valid business need.",
                "Logging exists but detective monitoring for unusual external access is weak.",
                "Private connectivity or explicit network restrictions should be evaluated for confidential customer data.",
            ],
            "questions": [
                "Can the storage account be restricted to private endpoints or approved networks?",
                "Who is in Data-Analytics-Team and when was access last recertified?",
                "Are successful reads coming from unexpected IP addresses or geographies?",
                "What log-retention period is required by internal policy?",
                "Is data minimised/tokenised or additionally protected before storage?",
            ],
            "severity": "High",
            "frameworks": {
                "DORA": "Protection and prevention controls for ICT assets/data, secure configuration, logging and monitoring.",
                "NIS2": "Access control, cryptography, asset management and secure systems operation.",
                "ISO 27001": "Cloud services, access control, cryptography, logging, network security and data protection.",
                "IT Risk": "Cloud configuration - data protection - network exposure - RBAC - logging",
            },
            "remediation": "Restrict network exposure where feasible, revalidate access groups, strengthen monitoring, and align log retention and data-protection controls with policy.",
        },

        "TPRM-003 - Critical SaaS incident notified late": {
            "domain": "TPRM / DORA / Incident",
            "difficulty": "Guided",
            "learning_goal": "Connect vendor criticality, contractual requirements, resilience and regulatory incident management.",
            "plain_story": (
                "A bank depends on an external SaaS provider for customer onboarding. The provider went down for four hours and told the bank about it 36 hours later. "
                "Your job is not to fix the SaaS platform; it is to assess whether the vendor met its obligations and whether the bank now has its own incident/regulatory actions."
            ),
            "glossary": [
                ("Critical vendor", "A provider whose failure can materially disrupt an important business service."),
                ("RTO", "Recovery Time Objective - target maximum time to restore a service."),
                ("RCA", "Root Cause Analysis - explanation of why the incident happened."),
                ("Fourth party", "A supplier/subcontractor used by your direct vendor."),
                ("Right to audit", "Contractual ability to obtain assurance or inspect relevant controls."),
            ],
            "screen_help": {
                "Vendor timeline": [
                    ("Detection", "When the vendor first identified the incident."),
                    ("Service restored", "When operations returned."),
                    ("Bank notified", "When your organisation was informed."),
                ],
                "Contract clauses": [
                    ("Notification target", "Expected time for vendor notification."),
                    ("RTO", "Contractual recovery target."),
                    ("Right to audit", "Available assurance/escalation mechanism."),
                ],
                "Service profile": [
                    ("Criticality", "How important the provider is."),
                    ("Data", "Information handled by the vendor."),
                    ("Substitutability", "How easily the service can be replaced."),
                ],
            },
            "context": (
                "A critical SaaS provider supporting customer onboarding suffered an availability and security incident. "
                "Service was unavailable for 4 hours. The vendor notified the bank 36 hours after initial detection."
            ),
            "mission": "Compare actual events with contractual expectations and identify what the bank must still determine internally.",

            "shadowing": [
                {
                    "step": "1. Reconstruct the timeline",
                    "senior": (
                        "I start with facts and timestamps. Detection was on 21 Aug at 01:20, service restored at 06:03, and the bank was notified on 22 Aug at 13:30."
                    ),
                    "why": "Incident review starts with a reliable chronology.",
                    "next": "Compare those facts with contractual requirements."
                },
                {
                    "step": "2. Test the contract",
                    "senior": (
                        "The contract target says notification within 4 hours after confirmation and RTO is 2 hours. "
                        "The vendor missed both targets based on the evidence provided."
                    ),
                    "why": "TPRM converts incident facts into supplier-control and contractual questions.",
                    "next": "Now determine what we still do not know about the incident itself."
                },
                {
                    "step": "3. Think like incident management",
                    "senior": (
                        "I still need root cause, affected systems/data, confidentiality/integrity impact, containment, recovery assurance and whether a fourth party was involved."
                    ),
                    "why": "Availability duration alone is not enough to understand the full incident impact.",
                    "next": "Request RCA, impact assessment, containment evidence and corrective actions."
                },
                {
                    "step": "4. Separate vendor obligations from bank obligations",
                    "senior": (
                        "The vendor notifying us does not complete the bank's regulatory work. The bank must perform its own DORA classification and reporting assessment."
                    ),
                    "why": "A regulated entity cannot outsource its own regulatory responsibility to a supplier.",
                    "next": "Confirm whether internal incident governance and DORA classification were triggered."
                },
                {
                    "step": "5. Form a preliminary risk view",
                    "senior": (
                        "We have a critical supplier that breached notification and recovery expectations during a security/availability incident, "
                        "with important facts still missing. I would escalate and open formal remediation."
                    ),
                    "why": "Criticality, contractual breach and incomplete incident information together drive urgency.",
                    "next": "Track RCA, corrective actions, resilience improvements and internal regulatory actions."
                },
            ],
            "guided_steps": [
                {"question": "1. Did the vendor meet the 4-hour notification target?", "hint": "Compare detection and bank notification.", "answer": "No. Notification occurred roughly 36 hours after detection."},
                {"question": "2. Did the vendor meet the 2-hour RTO?", "hint": "Compare outage start and restoration.", "answer": "No. The outage lasted about four hours."},
                {"question": "3. Does vendor notification settle the bank's DORA obligations?", "hint": "Think about who is regulated.", "answer": "No. The bank must perform its own incident classification and reporting assessment."},
                {"question": "4. What major facts are still missing?", "hint": "Think cause, data, containment and subcontractors.", "answer": "Root cause, confidentiality/integrity impact, containment, data impact and fourth-party involvement."},
            ],
            "evidence": {
                "Vendor timeline": pd.DataFrame([
                    {"Event": "Vendor detection", "Time": "2026-08-21 01:20"},
                    {"Event": "Service unavailable", "Time": "2026-08-21 02:05"},
                    {"Event": "Service restored", "Time": "2026-08-21 06:03"},
                    {"Event": "Bank notified", "Time": "2026-08-22 13:30"},
                ]),
                "Contract clauses": pd.DataFrame([
                    {"Clause": "Security incident notification", "Requirement": "Without undue delay; target <= 4 hours after confirmation"},
                    {"Clause": "BCP/DR", "Requirement": "RTO 2 hours / annual test"},
                    {"Clause": "Right to audit", "Requirement": "Included"},
                ]),
                "Service profile": pd.DataFrame([
                    {"Criticality": "Critical", "Process": "Customer onboarding", "Data": "Client PII", "Substitutability": "Low"},
                ]),
            },
            "issues": [
                "Vendor notification exceeded the contractual target.",
                "The outage exceeded the contracted RTO.",
                "The bank still needs its own DORA incident-classification/reporting assessment.",
                "Root cause, affected data, containment and fourth-party involvement remain unknown.",
            ],
            "questions": [
                "What was the confirmed root cause and exact impact scope?",
                "Was confidentiality or integrity affected, or only availability?",
                "Why did vendor notification take 36 hours?",
                "Were any fourth parties involved?",
                "What corrective action follows from the RTO breach?",
                "Has the internal incident team completed DORA classification?",
            ],
            "severity": "Critical",
            "frameworks": {
                "DORA": "ICT incident management/reporting and ICT third-party risk management.",
                "NIS2": "Incident handling, continuity and supply-chain security may be relevant depending on entity scope.",
                "ISO 27001": "Supplier relationships, incident management and ICT readiness for business continuity.",
                "IT Risk": "Third-party incident - resilience - RTO - contract - escalation",
            },
            "remediation": "Open formal vendor remediation, require RCA and corrective actions, reassess resilience and notification controls, and complete internal regulatory classification.",
        },

        "CHG-004 - Developer self-approves production change": {
            "domain": "Application / Change management",
            "difficulty": "Foundation",
            "learning_goal": "Understand how a software change travels from developer to production and why independent approval matters.",
            "plain_story": (
                "A developer changed application code and pushed it into production. Automated tests passed, but the same person wrote the change, approved it and triggered deployment. "
                "The key concept is segregation of duties: one person should not normally control every critical step without an approved exception."
            ),
            "glossary": [
                ("Change ticket", "Record describing why a production change is needed, its risk and approvals."),
                ("Pull request (PR)", "Request to merge code changes into a controlled code branch."),
                ("CI/CD pipeline", "Automation that builds, tests and deploys software."),
                ("Production", "Live environment used by real customers/business processes."),
                ("Segregation of duties (SoD)", "Separating incompatible responsibilities to reduce error or abuse."),
                ("Rollback plan", "How to reverse a change if it fails."),
            ],
            "screen_help": {
                "Change ticket": [("Requester", "Who initiated the change."), ("Business approval", "Independent/business authorization."), ("Rollback plan", "Recovery option if change fails.")],
                "Pull request": [("Author", "Who wrote the code."), ("Approver", "Who approved merging it."), ("Tests", "Automated evidence that code passed defined checks.")],
                "Deployment": [("Triggered by", "Who started production deployment."), ("Pipeline gate", "Control point before production.")],
            },
            "context": (
                "A production change fixed a defect in a customer-facing application. The same developer created the change ticket, approved the pull request and triggered production deployment. "
                "The team says the change was low risk because automated tests passed."
            ),
            "mission": "Decide whether passing automated tests compensates for the lack of independent approval.",

            "shadowing": [
                {
                    "step": "1. Understand the change flow",
                    "senior": (
                        "A normal production change usually moves through request, code change, review/approval, testing and deployment. "
                        "Different tools may implement this flow, but the control intent is authorization, testing and separation of incompatible duties."
                    ),
                    "why": "Before reviewing evidence, you need the mental model of how code reaches production.",
                    "next": "Map each evidence item to one stage of that flow."
                },
                {
                    "step": "2. Trace who did what",
                    "senior": (
                        "The change ticket requester is dev.jmiller. The PR author is dev.jmiller. The PR approver is also dev.jmiller. "
                        "Production deployment was triggered by dev.jmiller."
                    ),
                    "why": "Control testing often starts by tracing identities across separate systems.",
                    "next": "Ask whether one person is allowed to control all of these steps."
                },
                {
                    "step": "3. Separate testing from approval",
                    "senior": (
                        "Automated tests and the security scan passed. That is useful evidence about technical checks, but it does not prove independent authorization."
                    ),
                    "why": "Different controls address different risks. Testing does not automatically compensate for missing segregation of duties.",
                    "next": "Check change policy and approved exception/standard-change rules."
                },
                {
                    "step": "4. Avoid premature findings",
                    "senior": (
                        "I suspect a segregation-of-duties issue, but before finalizing a finding I verify whether low-risk changes are allowed to use a documented exception or automated approval model."
                    ),
                    "why": "You test the actual control requirement, not your assumption of what the control should be.",
                    "next": "Request policy, pipeline configuration and any exception approval."
                },
                {
                    "step": "5. Form a preliminary risk view",
                    "senior": (
                        "The evidence shows one developer controlled request, approval and deployment. Unless policy explicitly allows this with a valid compensating control, "
                        "the change process may not provide independent authorization."
                    ),
                    "why": "That is a defensible risk statement tied to evidence and a control expectation.",
                    "next": "Assess frequency, scope and whether the pipeline can technically prevent self-approval."
                },
            ],
            "guided_steps": [
                {"question": "1. Who requested, approved and deployed the change?", "hint": "Compare the three evidence sets.", "answer": "The same developer, dev.jmiller."},
                {"question": "2. What control principle is weakened?", "hint": "Think incompatible responsibilities.", "answer": "Segregation of duties / independent authorization."},
                {"question": "3. Do passed tests prove the change was properly authorised?", "hint": "Testing and approval answer different questions.", "answer": "No. Tests support technical quality; they do not provide independent authorization."},
                {"question": "4. What would you ask before raising a finding?", "hint": "Policy and exceptions matter.", "answer": "What policy requires for low-risk changes and whether an approved exception/standard-change process exists."},
            ],
            "evidence": {
                "Change ticket": pd.DataFrame([
                    {"Ticket": "CHG-48219", "Requester": "dev.jmiller", "Risk": "Low", "Business approval": "None", "Rollback plan": "Documented", "Status": "Implemented"},
                ]),
                "Pull request": pd.DataFrame([
                    {"PR": "#9182", "Author": "dev.jmiller", "Approver": "dev.jmiller", "Automated tests": "Passed", "Security scan": "Passed"},
                ]),
                "Deployment": pd.DataFrame([
                    {"Environment": "Production", "Triggered by": "dev.jmiller", "Pipeline gate": "Manual", "Deployment": "Successful"},
                ]),
            },
            "issues": [
                "Segregation of duties is ineffective for this change.",
                "Automated testing does not itself provide independent authorization.",
                "The low-risk label matters only if policy explicitly allows an alternative control/exception.",
            ],
            "questions": [
                "What does policy require for low-risk production changes?",
                "Can the CI/CD platform prevent self-approval or self-deployment?",
                "Was there an approved exception?",
                "Who reviews production-change logs?",
                "How many similar changes occurred?",
            ],
            "severity": "High",
            "frameworks": {
                "DORA": "Controlled ICT change management.",
                "NIS2": "Secure development/maintenance and governance measures.",
                "ISO 27001": "Change management, segregation of duties, secure development and access rights.",
                "IT Risk": "SDLC - CI/CD - change approval - SoD",
            },
            "remediation": "Enforce independent approval/deployment gates, document valid exceptions and review recent production changes for similar bypasses.",
        },

        "IR-005 - Ransomware alert with incomplete containment evidence": {
            "domain": "Incident / Security operations",
            "difficulty": "Guided",
            "learning_goal": "Understand why isolating one infected endpoint may not be enough to conclude that an incident is contained.",
            "plain_story": (
                "Security tooling detected ransomware-like behaviour and possible credential theft. The laptop was isolated, which is good, but stolen credentials could still be used elsewhere. "
                "Before accepting 'contained', you need evidence that the attacker did not move laterally and that recovery is trustworthy."
            ),
            "glossary": [
                ("EDR", "Endpoint Detection and Response - security tooling monitoring laptops/servers."),
                ("Credential dumping", "Attempt to extract stored credentials/tokens from a system."),
                ("Host isolation", "Disconnecting an endpoint from normal network communication."),
                ("Lateral movement", "Attacker moving from one compromised system/account to others."),
                ("Containment", "Stopping the incident from spreading or causing further harm."),
                ("Restore validation", "Testing that backups can actually restore clean systems/data."),
            ],
            "screen_help": {
                "EDR timeline": [("Event", "Security behaviour observed."), ("Action", "Automated/manual response.")],
                "Incident ticket": [("Status", "Team's current incident conclusion."), ("Data impact", "Whether information exposure is known.")],
                "Evidence checklist": [("Attached", "Whether evidence exists to support a containment/recovery conclusion.")],
            },
            "context": (
                "EDR detected ransomware-like behaviour on a finance workstation. The endpoint was isolated 18 minutes later. "
                "The ticket says 'contained', but evidence of credential reset, lateral-movement review and backup validation is missing."
            ),
            "mission": "Challenge whether 'contained' is sufficiently evidenced.",

            "shadowing": [
                {
                    "step": "1. Read the detection timeline",
                    "senior": (
                        "The EDR detected suspicious encryption and then credential-dumping behaviour. The host was isolated 18 minutes after the first alert."
                    ),
                    "why": "The sequence tells me this may be more than malware on one laptop; credentials may also be compromised.",
                    "next": "Check whether the incident team investigated impact beyond the endpoint."
                },
                {
                    "step": "2. Challenge the word 'contained'",
                    "senior": (
                        "The ticket says Contained, but that is a conclusion. I need evidence supporting it. Host isolation is one containment action, not proof that the whole incident is contained."
                    ),
                    "why": "IT Risk should distinguish a status label from the evidence behind that status.",
                    "next": "Look for credential reset/revocation and lateral-movement investigation."
                },
                {
                    "step": "3. Follow the credential risk",
                    "senior": (
                        "Credential dumping means the attacker may have obtained credentials or tokens. Even after isolating the laptop, those credentials could potentially be used elsewhere."
                    ),
                    "why": "This is why identity evidence becomes part of an endpoint incident.",
                    "next": "Request identity logs, password/token revocation evidence and lateral-movement queries."
                },
                {
                    "step": "4. Check recovery assurance",
                    "senior": (
                        "Backup restore validation is also missing. Recovery is not only 'we have backups'; the organisation needs confidence that clean restoration actually works."
                    ),
                    "why": "Ransomware can affect recovery capability as well as production systems.",
                    "next": "Request backup integrity and restore-test evidence."
                },
                {
                    "step": "5. Form a preliminary risk view",
                    "senior": (
                        "I would keep this incident under active review. Endpoint isolation occurred, but identity compromise, lateral movement, data impact and recovery assurance are not yet evidenced."
                    ),
                    "why": "The risk conclusion follows from what is still unknown, not only what was already done.",
                    "next": "Close the evidence gaps before accepting the incident as fully contained/recovered."
                },
            ],
            "guided_steps": [
                {"question": "1. What did the EDR detect besides encryption behaviour?", "hint": "Look at 09:08.", "answer": "Credential-dumping behaviour."},
                {"question": "2. Why does that matter after the laptop is isolated?", "hint": "Credentials can exist outside the laptop.", "answer": "Compromised credentials could be used to access other systems."},
                {"question": "3. What evidence is missing for lateral movement?", "hint": "Look at the checklist.", "answer": "A lateral-movement query/review across identity, endpoint and network telemetry."},
                {"question": "4. What recovery evidence is missing?", "hint": "Look at backups.", "answer": "Backup integrity/restore validation."},
            ],
            "evidence": {
                "EDR timeline": pd.DataFrame([
                    {"Time": "09:02", "Event": "Suspicious encryption activity", "Action": "Alert generated"},
                    {"Time": "09:08", "Event": "Credential dumping behaviour", "Action": "Blocked"},
                    {"Time": "09:20", "Event": "Host isolated", "Action": "Completed"},
                ]),
                "Incident ticket": pd.DataFrame([
                    {"Priority": "P1", "Status": "Contained", "Affected asset": "FIN-WS-044", "User": "finance.ap", "Data impact": "Unknown"},
                ]),
                "Evidence checklist": pd.DataFrame([
                    {"Evidence": "Credential reset", "Attached": "No"},
                    {"Evidence": "Lateral movement query", "Attached": "No"},
                    {"Evidence": "Backup restore validation", "Attached": "No"},
                    {"Evidence": "EDR isolation confirmation", "Attached": "Yes"},
                ]),
            },
            "issues": [
                "Host isolation alone does not prove full containment after credential-dumping activity.",
                "Potential lateral movement and identity compromise remain unassessed.",
                "Recovery readiness is not evidenced because backup/restoration validation is missing.",
            ],
            "questions": [
                "Were potentially exposed credentials reset/revoked?",
                "Was lateral movement investigated?",
                "Was the execution path/root cause established?",
                "Were backups checked and restore-tested?",
                "Was sensitive data accessed or exfiltrated?",
                "Does the incident meet escalation/reporting thresholds?",
            ],
            "severity": "Critical",
            "frameworks": {
                "DORA": "ICT incident management, response, recovery, evidence and classification/reporting.",
                "NIS2": "Incident handling, continuity, access control and reporting.",
                "ISO 27001": "Incident management, logging, malware protection, backup and access management.",
                "IT Risk": "EDR - containment - credential compromise - lateral movement - recovery",
            },
            "remediation": "Keep containment under review until identity compromise, lateral movement, data impact and recovery evidence are validated.",
        },

        "ISO-006 - Access review control cannot prove completion": {
            "domain": "ISO 27001 / Control assurance",
            "difficulty": "Foundation",
            "learning_goal": "Learn the difference between 'the team says it did the control' and evidence that proves the control operated effectively.",
            "plain_story": (
                "Every quarter, someone should review who has access to an application and decide whether each person still needs it. "
                "The team has a list of users and an email saying the review is complete, but there is no record of the actual decisions."
            ),
            "glossary": [
                ("Access review", "Periodic confirmation that users still need their current permissions."),
                ("Population", "Complete list of users/access items that should be reviewed."),
                ("Operating effectiveness", "Evidence that a control actually operated as designed during the period."),
                ("Sign-off", "Traceable confirmation that an accountable reviewer completed the review."),
                ("Audit trail", "Evidence showing who did what and when."),
            ],
            "screen_help": {
                "Q2 user export": [("User", "Identity in scope."), ("Role", "Level/type of access."), ("Status", "Whether the account is active.")],
                "Detailed review sheet": [
                    ("Reviewer", "Who made the access decision."),
                    ("Decision", "Whether access should be retained, removed or changed."),
                    ("Review date", "When the decision was made."),
                    ("Action ticket", "Evidence used to track a required access change/removal."),
                    ("Current status", "Current account state after the review."),
                ],
                "Review artefacts": [("Population export", "Shows what should have been reviewed."), ("Detailed reviewer decisions", "Shows keep/remove/change decisions."), ("Removal / change execution evidence", "Evidence that required actions happened."), ("Reviewer sign-off", "Evidence of accountable completion.")],
            },
            "context": (
                "An application owner says quarterly access reviews are always completed. For Q2, the team has an exported user list and an email saying 'review complete', "
                "but no evidence of reviewer decisions, removals or a proper sign-off trail."
            ),
            "mission": "Determine whether the retained evidence is enough to conclude that the control operated effectively.",

            "shadowing": [
                {
                    "step": "1. Understand the control objective",
                    "senior": (
                        "The control says access should be periodically reviewed so users keep only the access they still need. "
                        "To test it, I need evidence of the population, the reviewer decision and any resulting action."
                    ),
                    "why": "Control testing starts with what the control is supposed to achieve.",
                    "next": "Check whether the evidence proves each part of that process."
                },
                {
                    "step": "2. Inspect the population",
                    "senior": (
                        "The Q2 export shows three active users and their roles. This tells me who was in scope, but it does not tell me whether anyone actually reviewed them."
                    ),
                    "why": "A population is evidence of scope, not evidence of execution.",
                    "next": "Look for reviewer decisions and timestamps."
                },
                {
                    "step": "3. Inspect reviewer decisions",
                    "senior": (
                        "The detailed review sheet shows one retained user, one admin with no decision, and one user marked Remove. "
                        "That already suggests the review was not fully completed."
                    ),
                    "why": "Per-user decisions are the core evidence that the control operated.",
                    "next": "For the Remove decision, verify whether the access was actually removed."
                },
                {
                    "step": "4. Close the action trail",
                    "senior": (
                        "The user marked Remove has no action ticket and is still Active in the population. "
                        "So even if the reviewer made a decision, I cannot prove the remediation was executed."
                    ),
                    "why": "A review control often includes both decision and follow-through.",
                    "next": "Request ticket/system evidence showing removal, plus proper reviewer sign-off."
                },
                {
                    "step": "5. Form a preliminary risk view",
                    "senior": (
                        "I cannot conclude operating effectiveness for Q2. The population exists, but one privileged user has no review decision and a removal decision lacks closure evidence."
                    ),
                    "why": "This conclusion is specific to what the retained evidence can and cannot prove.",
                    "next": "Raise an evidence/control-performance issue and require a complete auditable review trail."
                },
            ],
            "guided_steps": [
                {"question": "1. What does the user export prove?", "hint": "It is a population, not a decision log.", "answer": "It proves which accounts/roles were listed, but not that each access was reviewed."},
                {"question": "2. What evidence would show that actual decisions were made?", "hint": "Think approve/remove/change.", "answer": "Per-user reviewer decisions with timestamps/reviewer identity."},
                {"question": "3. If access should be removed, what evidence closes the loop?", "hint": "Decision is not the same as execution.", "answer": "Ticket/system log showing the access was actually removed or changed."},
                {"question": "4. Can 'review complete' by email alone establish operating effectiveness?", "hint": "Can an auditor reproduce what happened?", "answer": "Usually not with the evidence shown; it lacks a traceable decision/action trail."},
            ],
            "evidence": {
                "Q2 user export": pd.DataFrame([
                    {"User": "a.silva", "Role": "Viewer", "Status": "Active"},
                    {"User": "b.meyer", "Role": "Admin", "Status": "Active"},
                    {"User": "c.rossi", "Role": "Editor", "Status": "Active"},
                ]),
                "Detailed review sheet": pd.DataFrame([
                    {"User": "a.silva", "Role": "Viewer", "Reviewer": "j.smith", "Decision": "Retain", "Review date": "2026-07-03", "Action ticket": "-", "Current status": "Active"},
                    {"User": "b.meyer", "Role": "Admin", "Reviewer": "", "Decision": "", "Review date": "", "Action ticket": "", "Current status": "Active"},
                    {"User": "c.rossi", "Role": "Editor", "Reviewer": "j.smith", "Decision": "Remove", "Review date": "2026-07-03", "Action ticket": "Missing", "Current status": "Active"},
                ]),
                "Review artefacts": pd.DataFrame([
                    {"Artefact": "Population export", "Available": "Yes"},
                    {"Artefact": "Detailed reviewer decisions", "Available": "Partial"},
                    {"Artefact": "Removal / change execution evidence", "Available": "No"},
                    {"Artefact": "Reviewer sign-off", "Available": "Email only"},
                ]),
            },
            "issues": [
                "The population exists, but evidence does not show that each access was reviewed against business need.",
                "Operating effectiveness cannot be concluded from the retained evidence.",
                "The control may have been performed, but it is not auditable/reproducible as evidenced.",
            ],
            "questions": [
                "Who is the designated reviewer?",
                "Where are approve/remove decisions recorded?",
                "Can removals be traced to fulfilment tickets/system logs?",
                "Was the population complete at the review cut-off date?",
                "How are overdue reviewers escalated?",
            ],
            "severity": "Medium",
            "frameworks": {
                "DORA": "ICT control assurance, access management and governance.",
                "NIS2": "Access-control and governance measures.",
                "ISO 27001": "Access rights, identity management and documented evidence supporting control operation.",
                "IT Risk": "Control design vs operating effectiveness - access recertification - audit evidence",
            },
            "remediation": "Use a workflow retaining the population, reviewer, per-user decision, timestamp, required action and closure evidence.",
        },
    }

    case_names = list(practice_cases.keys())
    selected_case = st.selectbox("Select practice case", case_names, key="practice_case_selector")

    if selected_case not in practice_cases:
        st.error("The selected case could not be loaded. Please select another case.")
        st.stop()

    case = practice_cases[selected_case]
    case_id = selected_case.split(" - ")[0]

    meta1, meta2, meta3 = st.columns([1.25, .8, .8])
    meta1.metric("Domain", case["domain"])
    meta2.metric("Level", case["difficulty"])
    meta3.metric("Evidence sets", len(case["evidence"]))

    st.markdown(
        f"""
        <div class="console-card">
            <div class="console-kicker">Case File - {case_id}</div>
            <div class="console-title">{selected_case.split(' - ',1)[1]}</div>
            <div class="console-copy">{case['context']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs([
        "0 - Learn",
        "1 - Shadowing",
        "2 - Evidence",
        "3 - Guided",
        "4 - Independent",
        "5 - Framework Lens",
        "6 - Debrief",
    ])

    with tabs[0]:
        st.markdown("### Onboarding: what are you learning here?")
        st.info(case["learning_goal"])

        st.markdown("### The scenario in plain language")
        st.write(case["plain_story"])

        st.markdown("### Terms you need before reading the evidence")
        glossary_df = pd.DataFrame(case["glossary"], columns=["Term", "Meaning"])
        st.dataframe(glossary_df, use_container_width=True, hide_index=True)

        st.success(
            "Do not move to the assessment until the scenario above makes sense. "
            "The goal is to understand the technology first - not to guess a risk rating."
        )

    with tabs[1]:
        st.markdown("### Shadowing mode")
        st.caption(
            "Imagine you are sitting next to a senior IT Risk analyst. Follow the order of attention, not just the final answer."
        )

        for idx, item in enumerate(case["shadowing"], start=1):
            st.markdown(f"#### {item['step']}")
            st.write(item["senior"])
            st.markdown(f"**Why this matters:** {item['why']}")
            st.markdown(f"**What I would do next:** {item['next']}")
            if idx < len(case["shadowing"]):
                st.divider()

        st.info(
            "Shadowing rule: do not try to memorise the wording. Notice the sequence: understand the object, inspect the evidence, "
            "separate facts from assumptions, request missing evidence, then form a risk view."
        )

    with tabs[2]:
        st.markdown("### Evidence supplied by the IT / Security team")
        st.caption(
            "Each table below represents the kind of information you might receive from a real technical team. "
            "Open 'How to read this evidence' if the columns are unfamiliar."
        )

        for title, df in case["evidence"].items():
            st.markdown(f"#### {title}")
            st.dataframe(df, use_container_width=True, hide_index=True)

            with st.expander(f"How to read this evidence - {title}"):
                help_rows = case.get("screen_help", {}).get(title, [])
                if help_rows:
                    help_df = pd.DataFrame(help_rows, columns=["Field / concept", "What it means"])
                    st.dataframe(help_df, use_container_width=True, hide_index=True)
                else:
                    st.write("No additional explanation is required for this evidence set.")

            st.write("")

    guide_state_key = f"guide_{case_id}"
    if guide_state_key not in st.session_state:
        st.session_state[guide_state_key] = {}

    with tabs[3]:
        st.markdown("### Guided investigation")
        st.caption("Try each question before revealing the answer. This is the learning phase - using hints is expected.")

        for idx, step in enumerate(case["guided_steps"], start=1):
            st.markdown(f"**{step['question']}**")
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("Show hint", key=f"hint_{case_id}_{idx}"):
                    st.session_state[guide_state_key][f"hint_{idx}"] = True
            with c2:
                if st.button("Reveal explanation", key=f"answer_{case_id}_{idx}"):
                    st.session_state[guide_state_key][f"answer_{idx}"] = True

            if st.session_state[guide_state_key].get(f"hint_{idx}", False):
                st.info("Hint: " + step["hint"])
            if st.session_state[guide_state_key].get(f"answer_{idx}", False):
                st.success(step["answer"])
            st.divider()

        st.caption(
            "Once you can explain these answers in your own words, move to 'Your Assessment'. "
            "Later cases can remove this guidance as your technical confidence increases."
        )

    state_key = "practice_submitted_" + case_id.replace("-", "_")

    with tabs[4]:
        st.markdown("### Your independent assessment")
        st.caption(
            "Now act as the IT Risk reviewer. You do not need perfect technical language - write what you understand and what you would challenge."
        )

        observed = st.text_area(
            "What concerns or control gaps do you see?",
            height=130,
            key=f"obs_{case_id}",
            placeholder="Write the risk/control concern in your own words.",
        )
        questions = st.text_area(
            "What would you ask the engineer / control owner next?",
            height=150,
            key=f"q_{case_id}",
            placeholder="What additional evidence or explanation would you request?",
        )
        severity_answer = st.radio(
            "Preliminary severity",
            ["Low", "Medium", "High", "Critical"],
            horizontal=True,
            key=f"sev_{case_id}",
        )
        treatment = st.text_area(
            "Recommended remediation / next action",
            height=110,
            key=f"treat_{case_id}",
            placeholder="What should happen next?",
        )

        if st.button("Submit investigation", type="primary", key=f"submit_{case_id}"):
            st.session_state[state_key] = True
            st.session_state[f"saved_obs_{case_id}"] = observed
            st.session_state[f"saved_q_{case_id}"] = questions
            st.session_state[f"saved_treat_{case_id}"] = treatment
            st.session_state[f"saved_sev_{case_id}"] = severity_answer
            st.success("Investigation submitted. Framework Lens and Debrief are now unlocked.")

    with tabs[5]:
        st.markdown("### Regulatory / control-framework lens")
        st.caption("Frameworks come after the technical reasoning - they should support the risk view, not replace it.")

        if not st.session_state.get(state_key, False):
            st.warning("Submit your assessment first to unlock the framework mapping.")
        else:
            for name, mapping in case["frameworks"].items():
                st.markdown(
                    f"""
                    <div class="treatment-card">
                        <div class="treatment-title">{name}</div>
                        <div class="treatment-copy">{mapping}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tabs[6]:
        if not st.session_state.get(state_key, False):
            st.warning("Complete and submit 'Your Assessment' before revealing the debrief.")
        else:
            your_sev = st.session_state.get(f"saved_sev_{case_id}", "")
            if your_sev == case["severity"]:
                st.success(f"Severity alignment: {case['severity']}")
            else:
                st.warning(f"Your preliminary severity: {your_sev} - Model view: {case['severity']}")

            st.markdown("### Key issues")
            for item in case["issues"]:
                st.markdown(f"- {item}")

            st.markdown("### Questions an experienced IT Risk reviewer would pursue")
            for item in case["questions"]:
                st.markdown(f"- {item}")

            st.markdown("### Suggested remediation")
            st.info(case["remediation"])

            st.markdown("### Your submitted notes")
            st.write("**Observed risks / gaps**")
            st.write(st.session_state.get(f"saved_obs_{case_id}", "-") or "-")
            st.write("**Questions / evidence requested**")
            st.write(st.session_state.get(f"saved_q_{case_id}", "-") or "-")
            st.write("**Your remediation**")
            st.write(st.session_state.get(f"saved_treat_{case_id}", "-") or "-")

            st.caption(
                "Training note: framework mappings are intentionally high-level. Exact articles/controls should be validated against the organisation's approved framework and current regulatory interpretation."
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

    uploaded = st.file_uploader("Upload Excel workbook", type=["xlsx"])

    if uploaded:
        try:
            xls = pd.ExcelFile(uploaded)
            available = {s.strip().lower() for s in xls.sheet_names}
            required_for_upload = REQUIRED_SHEETS - {"findings"}
            missing = required_for_upload - available

            if missing:
                st.error("Missing required sheets: " + ", ".join(sorted(missing)))
                st.stop()

            sheets = {
                s.lower(): normalize_columns(pd.read_excel(xls, sheet_name=s))
                for s in xls.sheet_names
            }

            tabs = st.tabs(["Vendors", "Documents", "Subcontractors", "Requirements", "Findings"])
            mapping = [
                ("vendors", tabs[0]), ("documents", tabs[1]),
                ("subcontractors", tabs[2]), ("document_requirements", tabs[3]),
            ]
            for name, tab in mapping:
                with tab:
                    st.caption(f'{len(sheets[name]):,} records')
                    st.dataframe(sheets[name], use_container_width=True, hide_index=True)

            with tabs[4]:
                if "findings" in sheets:
                    st.dataframe(sheets["findings"], use_container_width=True, hide_index=True)
                else:
                    st.info("Findings are generated dynamically; no findings sheet was supplied.")

            st.divider()

            if st.button("Commit Dataset to TPRM Database", type="primary", use_container_width=True):
                for name in ["vendors", "documents", "subcontractors", "document_requirements"]:
                    save_table(sheets[name], name)
                if "findings" in sheets:
                    save_table(sheets["findings"], "findings")
                st.success("Dataset imported successfully.")

        except Exception as exc:
            st.error(f"Unable to process workbook: {exc}")
