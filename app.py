import streamlit as st
from datetime import date
import database as db

st.set_page_config(page_title="Supply Chain Risk Manager", layout="wide")

# Initialize database tables
db.init_db()
db.init_docs_table()

# Business logic: Required documents per criticality
REQUIREMENTS = {
    "Critical": ["ISO 27001", "SOC 2", "DPA", "BCP/DRP", "Right-to-Audit"],
    "High": ["ISO 27001", "SOC 2", "DPA"],
    "Medium": ["DPA", "SLA"],
    "Low": ["Basic Contract"]
}

st.title("Supply Chain & 4th-Party Risk Manager")

menu = ["Vendor Registry", "Document Checklist", "Subcontractor Map", "Dashboard"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Vendor Registry":
    st.header("Vendor Registry")
    
    tab_list, tab_add = st.tabs(["View Vendors", "Add Vendor"])
    
    with tab_add:
        st.subheader("Register New Vendor")
        with st.form("vendor_form"):
            col1, col2 = st.columns(2)
            name = col1.text_input("Vendor Name")
            service_type = col2.text_input("Service Type (e.g., File Transfer, Cloud)")
            
            col3, col4 = st.columns(2)
            data_accessed = col3.selectbox("Data Accessed", ["Client PII", "Employee Data", "Financials", "None"])
            criticality = col4.selectbox("Criticality", ["Critical", "High", "Medium", "Low"])
            
            col5, col6, col7 = st.columns(3)
            onboarded_date = col5.date_input("Onboarded Date", date.today())
            contract_end_date = col6.date_input("Contract End Date", date.today())
            status = col7.selectbox("Status", ["Active", "Under Review", "Terminated"])
            
            submitted = st.form_submit_button("Save Vendor")
            
            if submitted:
                if name.strip():
                    db.add_vendor(
                        name, service_type, data_accessed, criticality,
                        str(onboarded_date), str(contract_end_date), status
                    )
                    st.success(f"Vendor '{name}' successfully added.")
                    st.rerun()
                else:
                    st.error("Vendor name cannot be empty.")

    with tab_list:
        st.subheader("Existing Vendors")
        df = db.get_all_vendors()
        
        if df.empty:
            st.info("No vendors registered yet.")
        else:
            st.dataframe(df, use_container_width=True)
            
            st.divider()
            st.subheader("Delete Vendor")
            vendor_ids = df['vendor_id'].tolist()
            selected_id = st.selectbox("Select Vendor ID to Delete", vendor_ids)
            
            if st.button("Delete Selected Vendor"):
                db.delete_vendor(selected_id)
                st.warning(f"Vendor ID {selected_id} deleted.")
                st.rerun()

elif choice == "Document Checklist":
    st.header("Document Checklist & Compliance")
    vendors_df = db.get_all_vendors()
    
    if vendors_df.empty:
        st.warning("No vendors registered. Please add a vendor in the Vendor Registry first.")
    else:
        vendor_name = st.selectbox("Select Vendor", vendors_df['name'].tolist())
        selected_vendor = vendors_df[vendors_df['name'] == vendor_name].iloc[0]
        
        v_id = selected_vendor['vendor_id']
        v_crit = selected_vendor['criticality']
        
        st.write(f"**Criticality Level:** {v_crit}")
        required_docs = REQUIREMENTS.get(v_crit, [])
        
        with st.expander("Add Document for this Vendor"):
            doc_type = st.selectbox("Document Type", required_docs)
            doc_status = st.selectbox("Status", ["Received", "Pending", "Expired"])
            expiry_date = st.date_input("Expiry Date", date.today())
            
            if st.button("Save Document"):
                db.add_document(int(v_id), doc_type, doc_status, str(expiry_date))
                st.success("Document added successfully.")
                st.rerun()

        docs_df = db.get_documents_by_vendor(v_id)
        received_docs = docs_df['doc_type'].tolist() if not docs_df.empty else []
        
        st.subheader("Compliance Status")
        for req in required_docs:
            if req in received_docs:
                st.success(f"✅ {req} - Received")
            else:
                st.error(f"❌ {req} - Missing")

elif choice == "Subcontractor Map":
    st.header("Subcontractor Map (Phase 3)")

elif choice == "Dashboard":
    st.header("Dashboard (Phase 4)")