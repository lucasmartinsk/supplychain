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
# TPRM RISK LAB — V3
# Vendor Risk • Evidence • Findings • Fourth Parties • Sample Docs
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
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM — "SIGNAL ROOM"
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

    .stApp { background:#0b0f14; color:#dde3ea; }
    .block-container { max-width:1520px; padding-top:1.3rem; padding-bottom:3.5rem; }

    /* Sidebar console */
    section[data-testid="stSidebar"] {
        background:#0e131a;
        border-right:1px solid #1c2531;
    }
    section[data-testid="stSidebar"] * { color:#aeb9c7; }
    section[data-testid="stSidebar"] label { color:#7d8b9c; }

    h1,h2,h3 { color:#f3f6f9; letter-spacing:-.02em; }

    .brand {
        padding:.6rem 0 1.15rem;
        border-bottom:1px solid #1c2531;
        margin-bottom:1.1rem;
    }
    .brand-mark {
        display:inline-flex; width:30px; height:30px;
        align-items:center; justify-content:center;
        border:1px solid #ffb020; border-radius:6px;
        background:#1a1406; color:#ffb020; font-size:.95rem;
        margin-right:.5rem; vertical-align:middle;
    }
    .brand-title {
        color:#f3f6f9; font-size:1.05rem; font-weight:800;
        letter-spacing:.04em; vertical-align:middle;
    }
    .brand-subtitle {
        color:#5f6c7d; font-size:.68rem; margin-top:.4rem;
        letter-spacing:.06em; text-transform:uppercase;
    }

    .page-kicker {
        color:#ffb020; font-size:.68rem; font-weight:800;
        letter-spacing:.16em; text-transform:uppercase;
        font-family:'JetBrains Mono', monospace;
    }
    .page-title { font-size:1.9rem; font-weight:800; margin:.15rem 0; color:#f3f6f9; }
    .page-subtitle { color:#7d8b9c; font-size:.88rem; margin-bottom:1.3rem; }

    /* Cards — sharp corners, hairline borders, no drop-shadow soup */
    .metric-card, .section-card, .console-card {
        background:#11161d;
        border:1px solid #1e2732;
        border-radius:6px;
    }
    .metric-card { padding:.95rem 1rem; position:relative; overflow:hidden; }
    .metric-card::before {
        content:""; position:absolute; left:0; top:0; bottom:0; width:3px;
        background:#ffb020;
    }
    .metric-label {
        color:#7d8b9c; font-size:.66rem; font-weight:800;
        text-transform:uppercase; letter-spacing:.09em;
    }
    .metric-value {
        color:#f3f6f9; font-size:1.7rem; font-weight:800; margin-top:.3rem;
        font-family:'JetBrains Mono', monospace;
    }
    .metric-note { color:#5f6c7d; font-size:.72rem; margin-top:.15rem; }

    .section-card { padding:1.1rem 1.2rem; margin-bottom:1rem; }
    .section-title {
        font-size:.76rem; font-weight:800; color:#dde3ea;
        margin-bottom:.7rem; letter-spacing:.08em; text-transform:uppercase;
        font-family:'JetBrains Mono', monospace;
    }

    .console-card {
        padding:1.2rem 1.3rem; margin-bottom:1rem;
        background:linear-gradient(135deg,#0f1621 0%,#141c2a 100%);
        border-color:#22304a;
    }
    .console-kicker {
        color:#5b8fd6; font-size:.64rem; font-weight:800;
        letter-spacing:.14em; text-transform:uppercase;
        font-family:'JetBrains Mono', monospace;
    }
    .console-title { color:#f3f6f9; font-size:1.2rem; font-weight:800; margin:.2rem 0; }
    .console-copy { color:#8fa0b8; font-size:.82rem; line-height:1.55; }
    .console-score {
        color:#ffffff; font-size:2.5rem; line-height:1; font-weight:800;
        font-family:'JetBrains Mono', monospace;
    }
    .console-score-label {
        color:#5f6c7d; font-size:.64rem; font-weight:700;
        letter-spacing:.08em; text-transform:uppercase;
    }

    .signal {
        display:flex; align-items:center; justify-content:space-between; gap:.7rem;
        padding:.58rem .7rem; border:1px solid #1e2732; border-radius:5px;
        background:#0e131a; margin-bottom:.45rem;
    }
    .signal-name { color:#aeb9c7; font-size:.78rem; font-weight:600; }
    .signal-value {
        color:#f3f6f9; font-size:.78rem; font-weight:700;
        font-family:'JetBrains Mono', monospace;
    }

    .risk-critical { color:#e5544a; }
    .risk-high { color:#e08e3e; }
    .risk-medium { color:#d6b23e; }
    .risk-low { color:#4caf7d; }

    /* Badges: small rectangles with a left tick, not full pills — audit-console feel */
    .badge {
        display:inline-flex; align-items:center; gap:.35rem;
        padding:.22rem .5rem; border-radius:4px;
        font-size:.65rem; font-weight:800; letter-spacing:.03em;
        font-family:'JetBrains Mono', monospace;
        border:1px solid transparent;
    }
    .badge::before { content:""; width:6px; height:6px; border-radius:1px; display:inline-block; }
    .badge-critical { background:#1f1210; color:#e5544a; border-color:#3a1f1c; }
    .badge-critical::before { background:#e5544a; }
    .badge-high { background:#201509; color:#e08e3e; border-color:#3a2712; }
    .badge-high::before { background:#e08e3e; }
    .badge-medium { background:#1e1a09; color:#d6b23e; border-color:#3a3012; }
    .badge-medium::before { background:#d6b23e; }
    .badge-low { background:#0f1c15; color:#4caf7d; border-color:#1c3626; }
    .badge-low::before { background:#4caf7d; }
    .badge-received,.badge-closed,.badge-compliant { background:#0f1c15; color:#4caf7d; border-color:#1c3626; }
    .badge-received::before,.badge-closed::before,.badge-compliant::before { background:#4caf7d; }
    .badge-pending,.badge-in-progress { background:#1e1a09; color:#d6b23e; border-color:#3a3012; }
    .badge-pending::before,.badge-in-progress::before { background:#d6b23e; }
    .badge-expired,.badge-missing,.badge-open,.badge-undisclosed { background:#1f1210; color:#e5544a; border-color:#3a1f1c; }
    .badge-expired::before,.badge-missing::before,.badge-open::before,.badge-undisclosed::before { background:#e5544a; }
    .badge-active { background:#0d1a26; color:#5b8fd6; border-color:#1c3552; }
    .badge-active::before { background:#5b8fd6; }
    .badge-under-review { background:#1e1a09; color:#d6b23e; border-color:#3a3012; }
    .badge-under-review::before { background:#d6b23e; }
    .badge-terminated { background:#171b21; color:#7d8b9c; border-color:#232b36; }
    .badge-terminated::before { background:#7d8b9c; }

    .finding {
        border-left:3px solid #e5544a; background:#150f0e;
        padding:.7rem .9rem; border-radius:0 5px 5px 0; margin-bottom:.5rem;
    }
    .finding.medium { border-left-color:#d6b23e; background:#15130a; }
    .finding.low { border-left-color:#4caf7d; background:#0d1610; }
    .finding-title { font-weight:700; color:#dde3ea; }
    .finding-detail { color:#7d8b9c; font-size:.78rem; margin-top:.12rem; }

    .score-box { background:#0e131a; border:1px solid #1e2732; border-radius:6px; padding:1.15rem; }
    .score-number {
        font-size:2.5rem; font-weight:800; color:#f3f6f9;
        font-family:'JetBrains Mono', monospace;
    }

    .driver-row {
        display:flex; justify-content:space-between; padding:.45rem 0;
        border-bottom:1px solid #1a212b; font-size:.81rem;
    }
    .driver-row:last-child { border-bottom:0; }
    .driver-name { color:#aeb9c7; }
    .driver-score { font-weight:700; color:#f3f6f9; font-family:'JetBrains Mono', monospace; }

    .risk-flow { display:grid; grid-template-columns:1fr auto 1fr auto 1fr; gap:.45rem; margin:.2rem 0 1rem; }
    .risk-node { border:1px solid #1e2732; border-radius:5px; padding:.75rem; background:#0e131a; }
    .risk-node-label { color:#5f6c7d; font-size:.62rem; font-weight:800; text-transform:uppercase; letter-spacing:.08em; }
    .risk-node-value { color:#f3f6f9; font-size:1.05rem; font-weight:700; margin-top:.15rem; font-family:'JetBrains Mono', monospace; }
    .risk-arrow { display:flex; align-items:center; color:#3a4656; font-weight:900; }

    .treatment-card {
        border:1px solid #1e2732; border-radius:5px; background:#0e131a;
        padding:.78rem .9rem; margin-bottom:.5rem;
    }
    .treatment-title { color:#dde3ea; font-weight:700; font-size:.79rem; }
    .treatment-copy { color:#7d8b9c; font-size:.74rem; margin-top:.15rem; line-height:1.45; }

    .attention-row {
        display:grid; grid-template-columns:1.6fr .7fr .55fr; gap:.8rem; align-items:center;
        padding:.7rem 0; border-bottom:1px solid #1a212b;
    }
    .attention-row:last-child { border-bottom:0; }
    .attention-name { color:#dde3ea; font-weight:700; font-size:.79rem; }
    .attention-meta { color:#7d8b9c; font-size:.69rem; }
    .attention-score { text-align:right; font-weight:800; color:#f3f6f9; font-family:'JetBrains Mono', monospace; }

    .doc-preview-frame {
        border:1px solid #1e2732; border-radius:5px; overflow:hidden; margin-top:.5rem;
    }

    .sample-card {
        border:1px solid #1e2732; border-radius:6px; background:#11161d;
        padding:1rem; margin-bottom:.8rem;
    }
    .sample-title { color:#dde3ea; font-weight:700; font-size:.88rem; }
    .sample-copy { color:#7d8b9c; font-size:.76rem; margin-top:.2rem; }

    .sidebar-caption { color:#5f6c7d; font-size:.68rem; margin-top:1.4rem; line-height:1.55; }
    div[data-testid="stDataFrame"] { border:1px solid #1e2732; border-radius:6px; overflow:hidden; }
    .stButton > button { border-radius:5px; font-weight:700; border-color:#2a3444; }
    button[kind="primary"] { background:#ffb020; border-color:#ffb020; color:#0b0f14; }
    button[kind="primary"]:hover { background:#e6a01c; border-color:#e6a01c; color:#0b0f14; }
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


@st.cache_data(ttl=30)
def load_data(table_name):
    allowed = {
        "vendors", "documents", "subcontractors",
        "document_requirements", "findings", "document_files",
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


# ============================================================
# MOCK / ILLUSTRATIVE SAMPLE DOCUMENTS
# ============================================================

MOCK_TEMPLATES = {
    "ISO 27001 Certificate": {
        "heading": "CERTIFICATE OF REGISTRATION",
        "subheading": "ISO/IEC 27001:2022 — Information Security Management System",
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
        "subheading": "Independent Service Auditor's Report — Security, Availability, Confidentiality",
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
            "Section II — Description of the System   ................ page 4",
            "Section III — Trust Services Criteria & Controls ......... page 9",
            "Section IV — Tests of Controls and Results ............... page 15",
        ],
    },
    "DPA": {
        "heading": "DATA PROCESSING AGREEMENT",
        "subheading": "Annex to the Master Services Agreement — GDPR Art. 28",
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
    legal document of any kind — every page carries a disclaimer.
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
    c.drawCentredString(0, 0, "SAMPLE — ILLUSTRATIVE ONLY")
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
    silently as 'Missing' — the two mean different things for
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

def risk_engine(vendor, documents, subcontractors, requirements):
    v = vendor.iloc[0]

    criticality = str(v.get("criticality", "Low")).lower()
    data_access = str(v.get("data_accessed", "None")).lower()

    criticality_score = {
        "critical": 30, "high": 22, "medium": 12, "low": 4,
    }.get(criticality, 5)

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

    compliance = compliance_engine(vendor, documents, requirements)

    evidence_gap = (
        len(compliance["missing"]) * 7
        + len(compliance["expired"]) * 6
        + len(compliance["pending"]) * 3
    )
    evidence_score = min(20, evidence_gap)

    vendor_id = v["vendor_id"]
    subs = subcontractors[
        subcontractors["parent_vendor_id"] == vendor_id
    ] if not subcontractors.empty else pd.DataFrame()

    hidden = 0
    if not subs.empty and "disclosed_by_vendor" in subs.columns:
        hidden = sum(not truthy(x) for x in subs["disclosed_by_vendor"])

    fourth_party_score = min(15, hidden * 8)

    contract_days = days_to_contract_end(v.get("contract_end_date"))

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

    vendor_status = str(v.get("status", "")).lower()
    status_score = 5 if vendor_status in {"under review", "terminated"} else 0

    score = min(
        100,
        criticality_score + data_score + evidence_score
        + fourth_party_score + contract_score + status_score,
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
        "score": score, "level": level, "drivers": drivers,
        "compliance": compliance, "hidden_subcontractors": hidden,
        "contract_days": contract_days,
    }


# ============================================================
# FINDINGS ENGINE
# ============================================================

def generate_findings(vendor, documents, subcontractors, requirements):
    result = risk_engine(vendor, documents, subcontractors, requirements)
    v = vendor.iloc[0]
    findings = []

    for doc in result["compliance"]["missing"]:
        findings.append({
            "vendor_id": v["vendor_id"], "vendor_name": v["name"],
            "severity": "High", "finding_type": "Missing Evidence",
            "description": f"Required document missing: {doc}",
        })
    for doc in result["compliance"]["expired"]:
        findings.append({
            "vendor_id": v["vendor_id"], "vendor_name": v["name"],
            "severity": "High", "finding_type": "Expired Evidence",
            "description": f"Required document expired: {doc}",
        })
    for doc in result["compliance"]["pending"]:
        findings.append({
            "vendor_id": v["vendor_id"], "vendor_name": v["name"],
            "severity": "Medium", "finding_type": "Pending Evidence",
            "description": f"Required document pending: {doc}",
        })
    if result["hidden_subcontractors"]:
        findings.append({
            "vendor_id": v["vendor_id"], "vendor_name": v["name"],
            "severity": "High", "finding_type": "Fourth-Party Risk",
            "description": (
                f'{result["hidden_subcontractors"]} undisclosed '
                "subcontractor relationship(s) identified."
            ),
        })
    if result["contract_days"] is not None:
        if result["contract_days"] < 0:
            findings.append({
                "vendor_id": v["vendor_id"], "vendor_name": v["name"],
                "severity": "High", "finding_type": "Contract",
                "description": "Contract has expired.",
            })
        elif result["contract_days"] <= 90:
            findings.append({
                "vendor_id": v["vendor_id"], "vendor_name": v["name"],
                "severity": "Medium", "finding_type": "Contract",
                "description": f'Contract expires in {result["contract_days"]} days.',
            })

    return findings


# ============================================================
# LOAD DATA
# ============================================================

ensure_document_files_table()

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
            <span class="brand-mark">◆</span>
            <span class="brand-title">TPRM RISK LAB</span>
        </div>
        <div class="brand-subtitle">Third-Party Risk Intelligence</div>
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
            "Vendor": vendor["name"], "Risk": r["level"], "Score": r["score"],
            "Compliance": r["compliance"]["percentage"], "Hidden": r["hidden_subcontractors"],
            "Findings": len(generate_findings(pd.DataFrame([vendor]), documents, subcontractors, requirements)),
        })

    register = pd.DataFrame(results)

    critical = int((vendors["criticality"].astype(str).str.lower() == "critical").sum())
    high_risk = int(register["Risk"].isin(["Critical", "High"]).sum())
    avg_compliance = int(register["Compliance"].mean())
    total_hidden = int(register["Hidden"].sum())
    open_findings = int(register["Findings"].sum())

    overall = (
        "Critical" if high_risk >= 8
        else "High" if high_risk >= 4
        else "Medium" if high_risk >= 1
        else "Low"
    )

    score_proxy = int(register["Score"].mean()) if not register.empty else 0
    st.markdown(
        f"""
        <div class="console-card">
            <div class="console-kicker">Executive Signal · Portfolio Posture</div>
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
                    <div class="console-score">{score_proxy}</div>
                    <div class="console-score-label">Avg. Risk Score / 100</div>
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
        ].sort_values("Score", ascending=False).head(6)

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
                                {row["Risk"]} risk · Evidence {row["Compliance"]}% ·
                                {row["Findings"]} finding(s)
                            </div>
                        </div>
                        <div>{badge(row["Risk"])}</div>
                        <div class="attention-score">{row["Score"]}</div>
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
        crit = st.selectbox("Criticality", ["All", "Critical", "High", "Medium", "Low"])
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
                <div class="console-kicker">Vendor Risk Profile · {v["status"]}</div>
                <div style="display:flex;justify-content:space-between;gap:2rem;align-items:center;">
                    <div>
                        <div class="console-title">{v["name"]}</div>
                        <div class="console-copy">
                            {v["service_type"]} · {v["data_accessed"]}<br>
                            Criticality: <strong>{v["criticality"]}</strong>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <div class="console-score">{risk["score"]}</div>
                        <div class="console-score-label">Risk Score / 100</div>
                        <div style="margin-top:.4rem;">{badge(risk["level"])}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        inherent_score = risk["drivers"][0][1] + risk["drivers"][1][1]
        residual_score = risk["score"]

        st.markdown(
            f"""
            <div class="section-card">
                <div class="section-title">Risk Lifecycle</div>
                <div class="risk-flow">
                    <div class="risk-node">
                        <div class="risk-node-label">Inherent Risk</div>
                        <div class="risk-node-value">{inherent_score}/50</div>
                    </div>
                    <div class="risk-arrow">→</div>
                    <div class="risk-node">
                        <div class="risk-node-label">Controls / Evidence</div>
                        <div class="risk-node-value">{risk["compliance"]["percentage"]}% coverage</div>
                    </div>
                    <div class="risk-arrow">→</div>
                    <div class="risk-node">
                        <div class="risk-node-label">Current Exposure</div>
                        <div class="risk-node-value">{residual_score}/100</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        left, right = st.columns([1.05, .95])
        with left:
            st.markdown(
                '<div class="section-card"><div class="section-title">Risk Drivers</div>',
                unsafe_allow_html=True,
            )
            for name, value, maximum in risk["drivers"]:
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
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown(
                '<div class="section-card"><div class="section-title">Contract & Operational Context</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div class="signal"><span class="signal-name">Criticality</span><span class="signal-value">{v["criticality"]}</span></div>
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
                    st.warning(f"Contract expires in {days} days.")
                else:
                    st.success(f"{days} days remaining.")
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
                with st.expander(f"Attach / view file — {doc}"):
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
        st.markdown("</div>", unsafe_allow_html=True)

        generated = generate_findings(vendor, documents, subcontractors, requirements)

        st.markdown(
            '<div class="section-card"><div class="section-title">Recommended Risk Treatment</div>',
            unsafe_allow_html=True,
        )
        if risk["compliance"]["missing"] or risk["compliance"]["expired"]:
            treatment_title = "Mitigate — remediate evidence gaps"
            treatment_copy = (
                "Prioritize missing or expired evidence before risk acceptance. "
                "Request current artifacts, validate scope and record remediation evidence."
            )
        elif risk["hidden_subcontractors"]:
            treatment_title = "Mitigate — investigate fourth-party exposure"
            treatment_copy = (
                "Obtain the complete subcontractor chain, validate disclosure and "
                "assess whether the dependency changes the vendor's risk posture."
            )
        elif risk["contract_days"] is not None and risk["contract_days"] <= 90:
            treatment_title = "Mitigate — contract review"
            treatment_copy = (
                "Trigger contract-owner review and confirm renewal, termination "
                "and right-to-audit considerations before expiry."
            )
        elif risk["level"] in ["Critical", "High"]:
            treatment_title = "Mitigate / Accept — governance decision required"
            treatment_copy = (
                "Risk remains above the lower-risk bands. Document treatment, "
                "owner and due date; escalate for formal risk acceptance where appropriate."
            )
        else:
            treatment_title = "Monitor — maintain evidence posture"
            treatment_copy = (
                "No immediate high-severity gap is generated by the current model. "
                "Continue periodic monitoring and evidence refresh."
            )

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
                        <div class="finding-title">{f["severity"]} · {f["finding_type"]}</div>
                        <div class="finding-detail">{f["description"]}</div>
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
            "Vendor": vendor["name"], "Criticality": vendor["criticality"],
            "Risk": r["level"], "Score": r["score"],
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
    view = register[register["Risk"].isin(selected)].sort_values("Score", ascending=False)
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
                "Description": f["description"], "Status": "Open", "Owner": "TPRM",
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
                <div class="finding-title">{row["name"]} → {row["subcontractor_name"]}</div>
                <div class="finding-detail">
                    {row["service_provided"]} · {row["criticality"]} primary vendor · Undisclosed relationship
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
        "Assess whether required evidence is present, valid and current — and attach the actual files.",
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
        attach_tag = " · file attached" if attached is not None else ""
        st.markdown(
            f"""
            <div class="signal">
                <span class="signal-name">{doc}{attach_tag}</span>
                <span>{badge(status_)}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander(f"Attach / view file — {doc}"):
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
        "⚠️ These are fictional, generated examples for training purposes only — "
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
        model = risk_engine(vendor, documents, subcontractors, requirements)
        actual_risk = model["level"]
        actual_fourth = "Yes" if model["hidden_subcontractors"] > 0 else "No"

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
            st.error(f"Risk level: your answer was {answer_risk}; model assessment is {actual_risk}.")

        if fourth_correct:
            st.success(f"✓ Fourth-party answer correct: {actual_fourth}")
        else:
            st.error(f"Fourth-party risk: your answer was {answer_fourth}; model assessment is {actual_fourth}.")

        if evidence_correct:
            st.success("✓ Evidence issue identification is correct.")
        else:
            st.warning("Evidence issue identification differs from the model.")

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
