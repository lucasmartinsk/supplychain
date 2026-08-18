import streamlit as st
import pandas as pd
from database import save_excel_table, load_data

st.set_page_config(page_title="TPRM Risk Lab", layout="wide")

st.title("🛡️ TPRM Risk Lab - Third-Party Risk Management")
st.write("Manage vendors, track missing documentation, and map third-party supply chain risks.")

# Sidebar Navigation
menu = st.sidebar.selectbox("Navigation", ["Dashboard & Import", "Vendor Directory", "Subcontractor Chain (MOVEit Analysis)"])

if menu == "Dashboard & Import":
    st.header("📥 Bulk Import (Excel Upload)")
    st.info("Upload your structured Excel file containing the sheets: `vendors`, `documents`, and `subcontractors`.")
    
    uploaded_file = st.file_uploader("Upload your file (.xlsx)", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            xls = pd.ExcelFile(uploaded_file)
            
            st.success("File successfully detected! Processing sheets...")
            
            # Preview and save each sheet
            tabs = st.tabs(xls.sheet_names)
            
            sheets_data = {}
            for i, sheet_name in enumerate(xls.sheet_names):
                df = pd.read_excel(xls, sheet_name=sheet_name)
                sheets_data[sheet_name] = df
                with tabs[i]:
                    st.write(f"Preview of **{sheet_name}** ({len(df)} rows):")
                    st.dataframe(df, use_container_width=True)
                    
            if st.button("Commit Data to Database"):
                for sheet_name, df in sheets_data.items():
                    save_excel_table(df, sheet_name)
                st.success("✅ All tables were successfully imported and saved to the database!")
                
        except Exception as e:
            st.error(f"Error processing the file. Ensure the sheets are named correctly (`vendors`, `documents`, `subcontractors`). Details: {e}")

elif menu == "Vendor Directory":
    st.header("📋 Registered Vendors")
    
    df_vendors = load_data('vendors')
    df_docs = load_data('documents')
    
    if not df_vendors.empty:
        # Criticality Filter
        criticality_filter = st.selectbox("Filter by Criticality", ["All"] + list(df_vendors['criticality'].unique()))
        
        if criticality_filter != "All":
            df_filtered = df_vendors[df_vendors['criticality'] == criticality_filter]
        else:
            df_filtered = df_vendors
            
        st.dataframe(df_filtered, use_container_width=True)
        
        st.subheader("📄 Document Compliance Status")
        if not df_docs.empty:
            # Merge documents with vendor names for easy readability
            df_merged = df_docs.merge(df_vendors[['vendor_id', 'name']], on='vendor_id', how='left')
            st.dataframe(df_merged[['name', 'doc_type', 'status', 'expiry_date']], use_container_width=True)
        else:
            st.warning("No documents found in the database.")
    else:
        st.warning("No vendors found. Please upload your Excel file in the 'Dashboard & Import' section first.")

elif menu == "Subcontractor Chain (MOVEit Analysis)":
    st.header("🔗 Fourth-Party & Subcontractor Mapping")
    st.write("Critical analysis focused on uncovering hidden subcontractors (Lessons learned from the MOVEit supply chain incident).")
    
    df_subs = load_data('subcontractors')
    df_vendors = load_data('vendors')
    
    if not df_subs.empty and not df_vendors.empty:
        df_sub_merged = df_subs.merge(df_vendors[['vendor_id', 'name']], left_on='parent_vendor_id', right_on='vendor_id', how='left')
        
        st.warning("⚠️ Vendors with **undisclosed** subcontractors represent high compliance risks and hidden shadow IT vectors.")
        
        for index, row in df_sub_merged.iterrows():
            disclosure_status = "🟢 Disclosed" if row['disclosed_by_vendor'] else "🔴 Hidden / Discovered Internally"
            with st.expander(f"Parent Vendor: {row['name']} ➔ Subcontractor: {row['subcontractor_name']} ({disclosure_status})"):
                st.write(f"**Service Provided:** {row['service_provided']}")
                st.write(f"**Disclosed by Primary Vendor?** {row['disclosed_by_vendor']}")
    else:
        st.warning("No subcontractor data loaded in the system.")
