import streamlit as st
import psycopg2

def get_connection():
    # If running on Streamlit Cloud, it uses secrets. Otherwise, falls back to local.
    if "supabase" in st.secrets:
        return psycopg2.connect(st.secrets["supabase"]["postgresql://postgres:Flask@747412@db.xpifntjiohkaucensrpu.supabase.co:5432/postgres"])
    else:
        return psycopg2.connect(
            dbname="scrum_tracker",
            user="postgres",
            password="Monkey",
            host="localhost",
            port="5432"
        )
