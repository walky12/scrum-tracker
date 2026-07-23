import streamlit as st
import psycopg2

st.title("Scrum Tracker Debug Mode")

def get_connection():
    # This pulls the exact string you saved in Streamlit Cloud Secrets
    return psycopg2.connect(st.secrets["supabase"]["postgresql://postgres:Flask@747412@db.xpifntjiohkaucensrpu.supabase.co:5432/postgres"])

try:
    conn = get_connection()
    st.success("Successfully connected to Supabase!")
    conn.close()
except Exception as e:
    st.error(f"Connection failed: {e}")
