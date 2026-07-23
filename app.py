import streamlit as st
import psycopg2

st.title("Scrum Tracker")

# Function to get connection using your Streamlit secrets
def get_connection():
    return psycopg2.connect(st.secrets["supabase"]["connection_string"])

# 1. Form to Add New Data
st.subheader("Add a New Scrum Task")
with st.form("task_form"):
    task_name = st.text_input("Task Description")
    status = st.selectbox("Status", ["To Do", "In Progress", "Done"])
    submit_button = st.form_submit_button("Add Task")

    if submit_button and task_name:
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO scrum_tasks (task_name, status) VALUES (%s, %s);",
                (task_name, status)
            )
            conn.commit()
            cur.close()
            conn.close()
            st.success(f"Added task: '{task_name}' successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to insert data: {e}")

# 2. View/Query Data from Supabase
st.subheader("Current Sprint Tasks")
try:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, task_name, status FROM scrum_tasks ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if rows:
        for row in rows:
            st.write(f"**ID {row[0]}**: {row[1]} — *Status: {row[2]}*")
    else:
        st.info("No tasks added yet. Use the form above to add your first task!")

except Exception as e:
    st.error(f"Failed to fetch data: {e}")
