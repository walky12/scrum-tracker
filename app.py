import streamlit as st
import psycopg2

st.title("Scrum Tracker Debug Mode")

def get_connection():
    if "supabase" in st.secrets:
        return psycopg2.connect(st.secrets["supabase"]["postgresql://postgres:Flask@747412@db.xpifntjiohkaucensrpu.supabase.co:5432/postgres"])
    else:
        return psycopg2.connect("postgresql://postgres:Monkey@aws-0-us-west-2.pooler.supabase.com:6543/postgres")

try:
    conn = get_connection()
    st.success("Successfully connected to Supabase!")
    conn.close()
except Exception as e:
    st.error(f"Connection failed: {e}")
