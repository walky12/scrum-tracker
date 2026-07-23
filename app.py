import streamlit as st
import psycopg2
import pandas as pd
from datetime import date

st.set_page_config(page_title="Responsibility Tracker", layout="wide")
st.title("📌 Daily Scrum Responsibility Tracker")
st.caption("Track action items and delegated tasks so nothing gets forgotten over time.")

# Function to get connection using your Streamlit secrets
def get_connection():
    return psycopg2.connect(st.secrets["supabase"]["connection_string"])

# 1. Ensure table structure exists
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scrum_tasks (
            id SERIAL PRIMARY KEY,
            task_name TEXT NOT NULL,
            assigned_by TEXT,
            assigned_person TEXT,
            area_responsibility TEXT,
            task_date DATE,
            status TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
except Exception as e:
    st.error(f"Table setup failed: {e}")

# 2. Clean Form to Add New Responsibility Item
with st.container():
    st.subheader("➕ Add New Responsibility Item")
    
    with st.form("task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            task_name = st.text_input("Responsibility / Action Item Description")
            assigned_by = st.text_input("Assigned By (e.g., Arjun)")
            assigned_person = st.text_input("Assigned To")
            
        with col2:
            area_responsibility = st.text_input("Area of Responsibility")
            task_date = st.date_input("Date Assigned", value=date.today())
            status = st.selectbox("Status", ["Open", "In Progress", "Completed", "Pending Review"])
            
        submit_button = st.form_submit_button("Save Responsibility Item", use_container_width=True)

        if submit_button:
            if task_name.strip():
                try:
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        """INSERT INTO scrum_tasks 
                           (task_name, assigned_by, assigned_person, area_responsibility, task_date, status) 
                           VALUES (%s, %s, %s, %s, %s, %s);""",
                        (task_name, assigned_by, assigned_person, area_responsibility, task_date, status)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success("Successfully recorded responsibility item!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to insert data: {e}")
            else:
                st.warning("Please fill out the responsibility description before submitting.")

st.markdown("---")

# 3. View, Edit, and Delete Existing Data Section
st.subheader("📋 Tracked Responsibilities & Follow-ups")
st.caption("Update statuses or edit details directly in the table below, then click **Save Changes to Database**.")

try:
    conn = get_connection()
    df = pd.read_sql("SELECT id, task_name, assigned_by, assigned_person, area_responsibility, task_date, status FROM scrum_tasks ORDER BY id ASC;", conn)
    conn.close()

    if not df.empty:
        # Configure data editor with a dropdown for status and num_rows="fixed" to remove the `+` button at the bottom
        edited_df = st.data_editor(
            df,
            num_rows="fixed",
            column_config={
                "status": st.column_config.SelectboxColumn(
                    "Status",
                    help="Update the status of the responsibility",
                    options=["Open", "In Progress", "Completed", "Pending Review"],
                    required=True
                )
            },
            key="scrum_editor",
            use_container_width=True,
            hide_index=True
        )

        if st.button("💾 Save Changes to Database", type="primary"):
            conn = get_connection()
            cur = conn.cursor()
            try:
                # Find deleted rows by comparing IDs
                current_ids = set(edited_df['id'].dropna())
                original_ids = set(df['id'])
                deleted_ids = original_ids - current_ids

                # Delete removed rows from database
                for del_id in deleted_ids:
                    cur.execute("DELETE FROM scrum_tasks WHERE id = %s;", (int(del_id),))

                # Update modified rows
                for _, row in edited_df.iterrows():
                    if pd.notna(row['id']) and int(row['id']) in original_ids:
                        cur.execute(
                            """UPDATE scrum_tasks 
                               SET task_name = %s, assigned_by = %s, assigned_person = %s, area_responsibility = %s, task_date = %s, status = %s 
                               WHERE id = %s;""",
                            (row['task_name'], row['assigned_by'], row['assigned_person'], row['area_responsibility'], row['task_date'], row['status'], int(row['id']))
                        )

                conn.commit()
                cur.close()
                conn.close()
                st.success("Changes saved successfully to Supabase!")
                st.rerun()
            except Exception as e:
                conn.rollback()
                cur.close()
                conn.close()
                st.error(f"Failed to update database: {e}")
    else:
        st.info("No responsibility items tracked yet. Use the form above to add your first item!")

except Exception as e:
    st.error(f"Failed to load data: {e}")
