#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os

import streamlit as st
from bson import ObjectId
from dotenv import load_dotenv
from streamlit_extras.add_vertical_space import add_vertical_space

from mongo_client import MongoDBConnection
from utils.custom_logger import initialize_logging

# Load environment variables
load_dotenv()

# Setup logging
logger = initialize_logging(filename='main', console_level='DEBUG')


def main():
    # App title and layout
    st.set_page_config(page_title="Advanced To-Do Manager", layout="wide")
    st.title("🚀 Advanced To-Do Manager")

    with MongoDBConnection(os.getenv('MONGO_PROJECT_DB')) as db_connection:
        # Sidebar for navigation
        st.sidebar.title("🔧 Navigation")
        option = st.sidebar.selectbox("Select Action", ["Add Task", "View Tasks", "Update Task", "Delete Task"])
        add_vertical_space()

        if option == "Add Task":
            st.subheader("📝 Add a New Task")
            task_name = st.text_input("Task Name")
            task_description = st.text_area("Task Description")
            task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
            due_date = st.date_input("Due Date", datetime.date.today())

            if st.button("Add Task"):
                if task_name:
                    task_data = {
                        'name': task_name,
                        'description': task_description,
                        'priority': task_priority,
                        'due_date': datetime.datetime.combine(due_date, datetime.datetime.min.time()),
                        'completed': False
                    }
                    task_id = db_connection.create_document('tasks', task_data)
                    st.success(f"Task added with ID: {task_id}")
                    logger.info(f"Task added: {task_name}, ID: {task_id}")
                else:
                    st.error("Task Name is required")

        elif option == "View Tasks":
            st.subheader("📋 View All Tasks")
            search = st.text_input("Search by Task Name")
            filter_priority = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High"], index=0)
            show_completed = st.checkbox("Show Completed Tasks")

            # Fetch tasks based on filters
            query = {}
            if search:
                query['name'] = {'$regex': search, '$options': 'i'}
            if filter_priority != "All":
                query['priority'] = filter_priority
            if not show_completed:
                query['completed'] = False

            tasks = db_connection.db['tasks'].find(query)
            for task in tasks:
                st.markdown(f"""
                **ID**: {task['_id']}
                - **Name**: {task['name']}
                - **Description**: {task['description']}
                - **Priority**: {task['priority']}
                - **Due Date**: {task['due_date'].strftime('%Y-%m-%d')}
                - **Completed**: {"✅" if task['completed'] else "❌"}
                """)
                st.write("---")

        elif option == "Update Task":
            st.subheader("✏️ Update a Task")
            task_id = st.text_input("Task ID")
            new_description = st.text_area("New Description")
            new_priority = st.selectbox("New Priority", ["Low", "Medium", "High"])
            new_due_date = st.date_input("New Due Date", datetime.date.today())
            completed = st.checkbox("Mark as Completed")

            if st.button("Update Task"):
                if task_id:
                    update_data = {
                        'description': new_description,
                        'priority': new_priority,
                        'due_date': datetime.datetime.combine(new_due_date, datetime.datetime.min.time()),
                        'completed': completed
                    }
                    modified_count = db_connection.update_document('tasks', {'_id': ObjectId(task_id)}, update_data)
                    if modified_count:
                        st.success(f"Task updated successfully")
                        logger.info(f"Task updated: ID {task_id}")
                    else:
                        st.error("No Task found with the provided ID")
                else:
                    st.error("Task ID and New Description are required")

        elif option == "Delete Task":
            st.subheader("❌ Delete a Task")
            task_id = st.text_input("Task ID to delete")
            if st.button("Delete Task"):
                if task_id:
                    deleted_count = db_connection.delete_document('tasks', {'_id': ObjectId(task_id)})
                    if deleted_count:
                        st.success(f"Task deleted successfully")
                        logger.info(f"Task deleted: ID {task_id}")
                    else:
                        st.error("No Task found with the provided ID")
                else:
                    st.error("Task ID is required")


if __name__ == "__main__":
    main()
