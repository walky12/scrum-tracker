import streamlit as st
import psycopg2
import pandas as pd
from datetime import date

def get_connection():
    return psycopg2.connect(
        dbname="scrum_tracker",
        user="postgres",
        password="Monkey",  # Replace with your actual PostgreSQL password
        host="localhost",
        port="5432"
    )

st.title("Local Scrum Responsibility Tracker")

# Sidebar for adding entries
st.sidebar.header("Log Responsibility")
with st.sidebar.form("scrum_form"):
    resp_date = st.date_input("Date", date.today())
    responsibility = st.text_area("Responsibility")
    area = st.text_input("Area")
    assigned_by = st.text_input("Assigned By")
    assigned_to = st.text_input("Assigned To")
    status = st.selectbox("Status", ["In Progress", "Completed", "Blocked"])
    submitted = st.form_submit_button("Save Entry")

    if submitted:
        if responsibility and assigned_to:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO daily_responsibilities (assignment_date, responsibility, area, assigned_by, assigned_to, status) VALUES (%s, %s, %s, %s, %s, %s)",
                (resp_date, responsibility, area, assigned_by, assigned_to, status)
            )
            conn.commit()
            cur.close()
            conn.close()
            st.sidebar.success("Saved successfully!")
            st.rerun()
        else:
            st.sidebar.error("Please fill out the responsibility and assignee fields.")

# Main area for viewing, editing, and deleting records
st.header("Activity Log & Management")
conn = get_connection()
df = pd.read_sql("SELECT id, assignment_date, responsibility, area, assigned_by, assigned_to, status FROM daily_responsibilities ORDER BY assignment_date DESC", conn)
conn.close()

if not df.empty:
    search_name = st.text_input("Search by 'Assigned To':")
    if search_name:
        df = df[df['assigned_to'].str.contains(search_name, case=False, na=False)]
    
    st.info("💡 You can edit cells directly in the table below. To delete rows, select the checkbox next to the row(s) and press Delete/Backspace.")
    
    # Interactive data editor allowing inline modifications and row deletions
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        key="data_editor",
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", disabled=True),
            "assignment_date": st.column_config.DateColumn("Date"),
            "status": st.column_config.SelectboxColumn("Status", options=["In Progress", "Completed", "Blocked"])
        }
    )

    if st.button("Save Changes to Database"):
        conn = get_connection()
        cur = conn.cursor()
        
        # 1. Handle Updates to existing rows
        current_ids = set(df['id'])
        edited_ids = set(edited_df['id'])
        
        for _, row in edited_df.iterrows():
            if row['id'] in current_ids:
                cur.execute(
                    """UPDATE daily_responsibilities 
                       SET assignment_date = %s, responsibility = %s, area = %s, assigned_by = %s, assigned_to = %s, status = %s 
                       WHERE id = %s""",
                    (row['assignment_date'], row['responsibility'], row['area'], row['assigned_by'], row['assigned_to'], row['status'], row['id'])
                )
        
        # 2. Handle Deletions (rows present in original df but missing in edited_df)
        deleted_ids = current_ids - edited_ids
        for del_id in deleted_ids:
            cur.execute("DELETE FROM daily_responsibilities WHERE id = %s", (del_id,))
            
        conn.commit()
        cur.close()
        conn.close()
        st.success("Database updated successfully!")
        st.rerun()
else:
    st.info("No records found yet. Use the sidebar to log your first entry.")