import gradio as gr
from fastapi import FastAPI
import uvicorn
from typing import List
import pandas as pd

def add_task(task_name,current_data):
    if not task_name:
        return current_data,current_data
    new_id=len(current_data)+1
    new_row=[new_id, task_name, "Pending"]
    updated_data=current_data + [new_row]
    return updated_data, updated_data
def delete_task(row_index,current_data):
    if row_index is None:
        return current_data,current_data
    # remove the task with the given row_index
    new_data=list(current_data)
    if 0 <= row_index < len(new_data):
        new_data.pop(row_index)
    return new_data, new_data
def toggle_status(evt:gr.SelectData,current_data):
    row,col=evt.index
    new_data=list(current_data)
    if col==2:
        current_status=new_data[row][2]
        new_status="Completed" if current_status=="Pending" else "Pending"
        new_data[row][2]=new_status
    return new_data, new_data
# the ui
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("## To-Do App with FastAPI and Gradio")
    # task state
    task_state=gr.State(value=[[1,"Sample Task","Pending"]])
    # imputs
    with gr.Row():
     txt_input = gr.Textbox(show_label=False, placeholder="Enter new task...", scale=4)
     btn_add = gr.Button("Add Task", variant="primary", scale=1)
    # 3. THE VIEW (Read)
    table = gr.Dataframe(
        headers=["ID", "Task", "Status"],
        value=[[1, "Learn Gradio", "Pending"], [2, "Build App", "Pending"]],
        interactive=False, 
        label="Click a status to toggle it. Select a row to delete it."
    )

    # 4. THE CONTROLS (Update/Delete)
    with gr.Row():
        btn_delete = gr.Button("Delete Selected Row", variant="stop")
        # We need a hidden text box to store which row is currently selected
        selected_row_index = gr.Number(value=-1, visible=False)

    # --- EVENTS ---

    # A. Create
    btn_add.click(fn=add_task, inputs=[txt_input, task_state], outputs=[task_state, table])
    
    # B. Update (Toggle Status)
    table.select(fn=toggle_status, inputs=[task_state], outputs=[task_state, table])

    # C. Delete Logic
    # 1. When user selects a cell, we capture the row index into our hidden variable
    def get_index(evt: gr.SelectData):
        return evt.index[0]
    
    table.select(fn=get_index, inputs=None, outputs=selected_row_index)
    
    # 2. When delete button is clicked, use that hidden index to remove the item
    btn_delete.click(fn=delete_task, inputs=[selected_row_index, task_state], outputs=[task_state, table])
demo.launch()
    