import streamlit as st
import psycopg2

st.title("Scrum Tracker Debug Mode")

def get_connection():
    # Correctly reference the section and the key name
    return psycopg2.connect(st.secrets["supabase"]["connection_string"])

try:
    conn = get_connection()
    st.success("Successfully connected to Supabase!")
    conn.close()
except Exception as e:
    st.error(f"Connection failed: {e}")
