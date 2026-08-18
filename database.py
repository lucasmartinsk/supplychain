import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect('supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendors (
            vendor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            service_type TEXT,
            data_accessed TEXT,
            criticality TEXT,
            onboarded_date DATE,
            contract_end_date DATE,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def init_docs_table():
    conn = sqlite3.connect('supply_chain.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_id INTEGER,
            doc_type TEXT,
            status TEXT,
            expiry_date DATE,
            FOREIGN KEY(vendor_id) REFERENCES vendors(vendor_id)
        )
    ''')
    conn.commit()
    conn.close()

def add_vendor(name, service_type, data_accessed, criticality, onboarded_date, contract_end_date, status):
    conn = sqlite3.connect('supply_chain.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vendors (name, service_type, data_accessed, criticality, onboarded_date, contract_end_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, service_type, data_accessed, criticality, onboarded_date, contract_end_date, status))
    conn.commit()
    conn.close()

def get_all_vendors():
    conn = sqlite3.connect('supply_chain.db')
    df = pd.read_sql_query("SELECT * FROM vendors", conn)
    conn.close()
    return df

def delete_vendor(vendor_id):
    conn = sqlite3.connect('supply_chain.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vendors WHERE vendor_id = ?", (vendor_id,))
    conn.commit()
    conn.close()

def add_document(vendor_id, doc_type, status, expiry_date):
    conn = sqlite3.connect('supply_chain.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO documents (vendor_id, doc_type, status, expiry_date)
        VALUES (?, ?, ?, ?)
    ''', (vendor_id, doc_type, status, expiry_date))
    conn.commit()
    conn.close()

def get_documents_by_vendor(vendor_id):
    conn = sqlite3.connect('supply_chain.db')
    df = pd.read_sql_query("SELECT * FROM documents WHERE vendor_id = ?", conn, params=(vendor_id,))
    conn.close()
    return df