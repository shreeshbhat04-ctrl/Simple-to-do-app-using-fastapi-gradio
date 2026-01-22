import streamlit as st
from fastapi import FastAPI
import uvicorn
import pandas as pd
import datetime
from threading import Thread

# FastAPI app
app = FastAPI()

# Shared data storage
tasks_data = []

# API endpoints
@app.get("/api/tasks")
def get_tasks():
    return tasks_data

@app.post("/api/tasks")
def add_task_api(task_name: str, target_date: str = "", target_time: str = ""):
    new_id = len(tasks_data) + 1
    new_task = {
        "id": new_id,
        "task": task_name,
        "status": "Pending",
        "target_date": target_date,
        "target_time": target_time,
        "result": ""
    }
    tasks_data.append(new_task)
    return {"message": "Task added", "task": new_task}

def check_completion(target_time_str, actual_time_str):
    try:
        target = datetime.datetime.strptime(target_time_str, "%Y-%m-%d %H:%M")
        actual = datetime.datetime.strptime(actual_time_str, "%Y-%m-%d %H:%M")
        diff = actual - target
        if diff.total_seconds() <= 0:
            return "Success"
        else:
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            return f"Late by {hours}h {minutes}m"
    except:
        return ""

# Streamlit UI
st.set_page_config(page_title="To-Do App", layout="wide")
st.markdown("## To-Do App with FastAPI and Streamlit")

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# Input form
st.subheader("Add New Task")
col1, col2, col3, col4 = st.columns(4)

with col1:
    task_name = st.text_input("Task Name", placeholder="Enter task...")

with col2:
    target_date = st.date_input("Target Date")

with col3:
    target_time = st.time_input("Target Time")

with col4:
    if st.button("➕ Add Task", use_container_width=True):
        if task_name:
            new_id = len(st.session_state.tasks) + 1
            new_task = {
                "ID": new_id,
                "Task": task_name,
                "Status": "Pending",
                "Target Date": target_date.strftime("%Y-%m-%d"),
                "Target Time": target_time.strftime("%H:%M"),
                "Result": ""
            }
            st.session_state.tasks.append(new_task)
            tasks_data.append(new_task)
            st.rerun()

# Display tasks
st.subheader("Tasks")
if st.session_state.tasks:
    df = pd.DataFrame(st.session_state.tasks)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Task actions
    st.subheader("Task Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        task_index = st.selectbox("Select Task", range(len(st.session_state.tasks)), 
                                   format_func=lambda i: st.session_state.tasks[i]["Task"])
    
    with col2:
        if st.button("✅ Mark Complete"):
            if st.session_state.tasks[task_index]["Status"] == "Pending":
                completed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                target_date = st.session_state.tasks[task_index]["Target Date"]
                target_time = st.session_state.tasks[task_index]["Target Time"]
                
                if target_date and target_time:
                    result = check_completion(f"{target_date} {target_time}", completed_time)
                    st.session_state.tasks[task_index]["Result"] = result
                
                st.session_state.tasks[task_index]["Status"] = "Completed"
                st.rerun()
    
    with col3:
        if st.button("Delete Task"):
            st.session_state.tasks.pop(task_index)
            st.rerun()
else:
    st.info("No tasks yet. Add one above!")

# Run FastAPI in background
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="critical")

if __name__ == "__main__":
    #Start FastAPI in background thread (optional)
    thread = Thread(target=run_fastapi, daemon=True)
    thread.start()
    pass

