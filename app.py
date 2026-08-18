import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

DB_NAME = "tprm_database.db"

REQUIRED_SHEETS = {
    "vendors",
    "documents",
    "subcontractors",
}


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    """Create a SQLite database connection."""
    return sqlite3.connect(DB_NAME)


def save_table(df: pd.DataFrame, table_name: str):
    """Replace a database table with the supplied DataFrame."""
    if df is None or df.empty:
        return

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


def load_data(table_name: str) -> pd.DataFrame:
    """Load a table from SQLite safely."""
    conn = get_connection()

    try:
        # Only allow known table names
        allowed_tables = {
            "vendors",
            "documents",
            "subcontractors",
        }

        if table_name not in allowed_tables:
            raise ValueError(f"Invalid table name: {table_name}")

        return pd.read_sql_query(
            f'SELECT * FROM "{table_name}"',
            conn,
        )

    except Exception as e:
        st.error(f"Could not load `{table_name}`: {e}")
        return pd.DataFrame()

    finally:
        conn.close()


def table_exists(table_name: str) -> bool:
    """Check whether a table exists in SQLite."""
    conn = get_connection()

    try:
        query = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name = ?
        """

        result = pd.read_sql_query(
            query,
            conn,
            params=(table_name,),
        )

        return not result.empty

    finally:
        conn.close()


# ============================================================
# DATA VALIDATION
# ============================================================

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize Excel column names."""
    df = df.copy()

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    return df


def validate_excel_sheets(sheet_names):
    """Validate required Excel sheets."""
    available = {name.strip().lower() for name in sheet_names}

    missing = REQUIRED_SHEETS - available

    return missing


# ============================================================
# RISK CALCULATIONS
# ============================================================

def calculate_vendor_metrics(
    vendors: pd.DataFrame,
    documents: pd.DataFrame,
    subcontractors: pd.DataFrame,
):
    """Calculate high-level TPRM metrics."""

    total_vendors = len(vendors)

    critical_vendors = 0
    if "criticality" in vendors.columns:
        critical_vendors = (
            vendors["criticality"]
            .astype(str)
            .str.lower()
            .eq("critical")
            .sum()
        )

    expired_documents = 0

    if not documents.empty and "expiry_date" in documents.columns:

        expiry_dates = pd.to_datetime(
            documents["expiry_date"],
            errors="coerce",
        )

        expired_documents = (
            expiry_dates < pd.Timestamp.today()
        ).sum()

    hidden_subcontractors = 0

    if not subcontractors.empty:
        if "disclosed_by_vendor" in subcontractors.columns:

            disclosed = (
                subcontractors["disclosed_by_vendor"]
                .astype(str)
                .str.lower()
                .isin(
                    [
                        "true",
                        "yes",
                        "1",
                        "disclosed",
                    ]
                )
            )

            hidden_subcontractors = (~disclosed).sum()

    return {
        "total_vendors": total_vendors,
        "critical_vendors": critical_vendors,
        "expired_documents": expired_documents,
        "hidden_subcontractors": hidden_subcontractors,
    }


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="TPRM Risk Lab",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ TPRM Risk Lab")

st.caption(
    "Third-Party Risk Management | Vendor, Documentation "
    "and Fourth-Party Risk Monitoring"
)


# ============================================================
# SIDEBAR
# ============================================================

menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "📥 Data Import",
        "🏢 Vendor Directory",
        "🔗 Fourth-Party Risk",
    ],
)

st.sidebar.divider()

st.sidebar.caption(
    "TPRM Risk Lab\n"
    "Vendor & Supply Chain Risk"
)


# ============================================================
# LOAD DATABASE
# ============================================================

vendors = load_data("vendors") if table_exists("vendors") else pd.DataFrame()
documents = load_data("documents") if table_exists("documents") else pd.DataFrame()
subcontractors = (
    load_data("subcontractors")
    if table_exists("subcontractors")
    else pd.DataFrame()
)


# ============================================================
# DASHBOARD
# ============================================================

if menu == "📊 Dashboard":

    st.header("📊 Executive Risk Dashboard")

    if vendors.empty:
        st.info(
            "No vendor data is currently available. "
            "Go to **Data Import** to upload your Excel file."
        )

    else:

        metrics = calculate_vendor_metrics(
            vendors,
            documents,
            subcontractors,
        )

        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Vendors",
            metrics["total_vendors"],
        )

        col2.metric(
            "Critical Vendors",
            metrics["critical_vendors"],
        )

        col3.metric(
            "Expired Documents",
            metrics["expired_documents"],
        )

        col4.metric(
            "Hidden Subcontractors",
            metrics["hidden_subcontractors"],
        )

        st.divider()

        # ----------------------------------------------------
        # VENDOR CRITICALITY
        # ----------------------------------------------------

        left, right = st.columns(2)

        with left:

            st.subheader("Vendor Criticality")

            if "criticality" in vendors.columns:

                criticality_counts = (
                    vendors["criticality"]
                    .fillna("Unknown")
                    .value_counts()
                )

                st.bar_chart(criticality_counts)

            else:
                st.warning(
                    "The `criticality` column was not found."
                )

        # ----------------------------------------------------
        # DOCUMENT STATUS
        # ----------------------------------------------------

        with right:

            st.subheader("Document Status")

            if (
                not documents.empty
                and "status" in documents.columns
            ):

                status_counts = (
                    documents["status"]
                    .fillna("Unknown")
                    .value_counts()
                )

                st.bar_chart(status_counts)

            else:

                st.info(
                    "No document status information available."
                )

        st.divider()

        # ----------------------------------------------------
        # HIGH RISK VENDORS
        # ----------------------------------------------------

        st.subheader("⚠️ Vendors Requiring Attention")

        if "criticality" in vendors.columns:

            high_risk = vendors[
                vendors["criticality"]
                .astype(str)
                .str.lower()
                .isin(
                    [
                        "critical",
                        "high",
                    ]
                )
            ]

            if not high_risk.empty:

                st.dataframe(
                    high_risk,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.success(
                    "No Critical or High criticality vendors found."
                )


# ============================================================
# DATA IMPORT
# ============================================================

elif menu == "📥 Data Import":

    st.header("📥 Bulk Data Import")

    st.write(
        "Upload an Excel workbook containing the TPRM datasets."
    )

    uploaded_file = st.file_uploader(
        "Upload Excel workbook",
        type=["xlsx"],
    )

    if uploaded_file:

        try:

            xls = pd.ExcelFile(uploaded_file)

            missing = validate_excel_sheets(
                xls.sheet_names
            )

            if missing:

                st.error(
                    "Missing required sheets: "
                    + ", ".join(sorted(missing))
                )

            else:

                st.success(
                    "Excel workbook validated successfully."
                )

                sheets_data = {}

                tabs = st.tabs(
                    xls.sheet_names
                )

                for tab, sheet_name in zip(
                    tabs,
                    xls.sheet_names,
                ):

                    df = pd.read_excel(
                        xls,
                        sheet_name=sheet_name,
                    )

                    df = normalize_columns(df)

                    sheets_data[
                        sheet_name.lower()
                    ] = df

                    with tab:

                        st.write(
                            f"### {sheet_name}"
                        )

                        st.caption(
                            f"{len(df):,} rows"
                        )

                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True,
                        )

                st.divider()

                if st.button(
                    "💾 Commit Data to Database",
                    type="primary",
                    use_container_width=True,
                ):

                    for (
                        sheet_name,
                        df,
                    ) in sheets_data.items():

                        save_table(
                            df,
                            sheet_name,
                        )

                    st.success(
                        "✅ Data successfully imported."
                    )

                    st.cache_data.clear()

        except Exception as e:

            st.error(
                f"Unable to process Excel file: {e}"
            )


# ============================================================
# VENDOR DIRECTORY
# ============================================================

elif menu == "🏢 Vendor Directory":

    st.header("🏢 Vendor Directory")

    if vendors.empty:

        st.warning(
            "No vendors found. "
            "Please import your Excel file first."
        )

    else:

        # ----------------------------------------------------
        # FILTERS
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            if "criticality" in vendors.columns:

                criticalities = sorted(
                    vendors["criticality"]
                    .dropna()
                    .astype(str)
                    .unique()
                )

                selected_criticality = st.selectbox(
                    "Criticality",
                    ["All"] + criticalities,
                )

            else:

                selected_criticality = "All"

        with col2:

            search = st.text_input(
                "🔎 Search Vendor",
                placeholder="Vendor name...",
            )

        filtered = vendors.copy()

        if selected_criticality != "All":

            filtered = filtered[
                filtered["criticality"]
                .astype(str)
                .eq(selected_criticality)
            ]

        if search and "name" in filtered.columns:

            filtered = filtered[
                filtered["name"]
                .astype(str)
                .str.contains(
                    search,
                    case=False,
                    na=False,
                )
            ]

        st.caption(
            f"Showing {len(filtered):,} of "
            f"{len(vendors):,} vendors"
        )

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # DOCUMENT COMPLIANCE
        # ----------------------------------------------------

        st.divider()

        st.subheader("📄 Document Compliance")

        if documents.empty:

            st.info(
                "No document records found."
            )

        elif "vendor_id" in documents.columns:

            vendor_columns = [
                col
                for col in [
                    "vendor_id",
                    "name",
                ]
                if col in vendors.columns
            ]

            df_docs = documents.merge(
                vendors[vendor_columns],
                on="vendor_id",
                how="left",
            )

            display_columns = [
                col
                for col in [
                    "name",
                    "doc_type",
                    "status",
                    "expiry_date",
                ]
                if col in df_docs.columns
            ]

            st.dataframe(
                df_docs[display_columns],
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.warning(
                "Documents table does not contain `vendor_id`."
            )


# ============================================================
# FOURTH-PARTY RISK
# ============================================================

elif menu == "🔗 Fourth-Party Risk":

    st.header("🔗 Fourth-Party & Subcontractor Risk")

    st.write(
        "Identify subcontractors and potential hidden "
        "fourth-party dependencies across the vendor ecosystem."
    )

    if subcontractors.empty:

        st.warning(
            "No subcontractor data found."
        )

    elif vendors.empty:

        st.warning(
            "Vendor data is required to map subcontractors."
        )

    else:

        required_sub_columns = {
            "parent_vendor_id",
            "subcontractor_name",
        }

        missing_columns = (
            required_sub_columns
            - set(subcontractors.columns)
        )

        if missing_columns:

            st.error(
                "Missing subcontractor columns: "
                + ", ".join(sorted(missing_columns))
            )

        else:

            merged = subcontractors.merge(
                vendors[
                    [
                        "vendor_id",
                        "name",
                    ]
                ],
                left_on="parent_vendor_id",
                right_on="vendor_id",
                how="left",
            )

            # ------------------------------------------------
            # DISCLOSURE ANALYSIS
            # ------------------------------------------------

            if "disclosed_by_vendor" in merged.columns:

                disclosed = (
                    merged["disclosed_by_vendor"]
                    .astype(str)
                    .str.lower()
                    .isin(
                        [
                            "true",
                            "yes",
                            "1",
                            "disclosed",
                        ]
                    )
                )

                hidden_count = (~disclosed).sum()

                col1, col2 = st.columns(2)

                col1.metric(
                    "Total Subcontractors",
                    len(merged),
                )

                col2.metric(
                    "Undisclosed / Hidden",
                    hidden_count,
                )

                st.divider()

                if hidden_count > 0:

                    st.error(
                        f"🚨 {hidden_count} subcontractor(s) "
                        "were not disclosed by the primary vendor."
                    )

            # ------------------------------------------------
            # SUBCONTRACTOR TABLE
            # ------------------------------------------------

            st.subheader(
                "Subcontractor Dependency Map"
            )

            for _, row in merged.iterrows():

                disclosed_value = str(
                    row.get(
                        "disclosed_by_vendor",
                        "",
                    )
                ).lower()

                is_disclosed = disclosed_value in {
                    "true",
                    "yes",
                    "1",
                    "disclosed",
                }

                if is_disclosed:

                    status = "🟢 Disclosed"

                else:

                    status = "🔴 Hidden / Undisclosed"

                vendor_name = row.get(
                    "name",
                    "Unknown Vendor",
                )

                subcontractor_name = row.get(
                    "subcontractor_name",
                    "Unknown",
                )

                with st.expander(
                    f"{vendor_name} → "
                    f"{subcontractor_name} | "
                    f"{status}"
                ):

                    service = row.get(
                        "service_provided",
                        "Not specified",
                    )

                    st.write(
                        f"**Service:** {service}"
                    )

                    st.write(
                        f"**Disclosure Status:** "
                        f"{status}"
                    )
