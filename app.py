import streamlit as st
import psycopg2
import pandas as pd
from datetime import date

st.title("Scrum Tracker")

# Function to get connection using your Streamlit secrets
def get_connection():
    return psycopg2.connect(st.secrets["supabase"]["connection_string"])

# 1. Ensure table includes assigned_person, area_responsibility, and task_date
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scrum_tasks (
            id SERIAL PRIMARY KEY,
            task_name TEXT NOT NULL,
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

# 2. Form to Add a New Task
st.subheader("Add a New Scrum Task")
with st.form("task_form"):
    task_name = st.text_input("Task Description")
    assigned_person = st.text_input("Assigned To")
    area_responsibility = st.text_input("Area of Responsibility")
    task_date = st.date_input("Date", value=date.today())
    status = st.selectbox("Status", ["To Do", "In Progress", "Done"])
    submit_button = st.form_submit_button("Add Task")

    if submit_button and task_name:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO scrum_tasks (task_name, assigned_person, area_responsibility, task_date, status) VALUES (%s, %s, %s, %s, %s);",
                (task_name, assigned_person, area_responsibility, task_date, status)
            )
            conn.commit()
            cur.close()
            conn.close()
            st.success(f"Added task: '{task_name}' successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to insert data: {e}")

# 3. View, Edit, Modify, and Delete Data
st.subheader("Current Sprint Tasks (Edit / Delete)")

try:
    conn = get_connection()
    df = pd.read_sql("SELECT id, task_name, assigned_person, area_responsibility, task_date, status FROM scrum_tasks ORDER BY id ASC;", conn)
    conn.close()

    if not df.empty:
        # Use st.data_editor to allow inline modifications, updates, and row deletions
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            key="scrum_editor",
            use_container_width=True,
            hide_index=True
        )

        if st.button("Save Changes to Database"):
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

                # Update modified or add new rows
                for _, row in edited_df.iterrows():
                    if pd.notna(row['id']) and int(row['id']) in original_ids:
                        # Update existing row
                        cur.execute(
                            """UPDATE scrum_tasks 
                               SET task_name = %s, assigned_person = %s, area_responsibility = %s, task_date = %s, status = %s 
                               WHERE id = %s;""",
                            (row['task_name'], row['assigned_person'], row['area_responsibility'], row['task_date'], row['status'], int(row['id']))
                        )
                    elif pd.isna(row['id']) or row['id'] == '':
                        # Insert new row added directly inside the editor
                        if row['task_name']:
                            cur.execute(
                                """INSERT INTO scrum_tasks (task_name, assigned_person, area_responsibility, task_date, status) 
                                   VALUES (%s, %s, %s, %s, %s);""",
                                (row['task_name'], row['assigned_person'], row['area_responsibility'], row['task_date'], row['status'])
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
        st.info("No tasks found. Add a task above to get started!")

except Exception as e:
    st.error(f"Failed to load data: {e}")
