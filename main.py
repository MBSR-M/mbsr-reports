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


class TaskManager:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def add_task(self, task_name, task_description, task_priority, due_date):
        if task_name:
            task_data = {
                'name': task_name,
                'description': task_description,
                'priority': task_priority,
                'due_date': datetime.datetime.combine(due_date, datetime.datetime.min.time()),
                'completed': False
            }
            task_id = self.db_connection.create_document('tasks', task_data)
            logger.info(f"Task added: {task_name}, ID: {task_id}")
            return f"Task added with ID: {task_id}"
        else:
            raise ValueError("Task Name is required")

    def update_task(self, task_id, new_description, new_priority, new_due_date, completed):
        if task_id:
            update_data = {
                'description': new_description,
                'priority': new_priority,
                'due_date': datetime.datetime.combine(new_due_date, datetime.datetime.min.time()),
                'completed': completed
            }
            modified_count = self.db_connection.update_document('tasks', {'_id': ObjectId(task_id)}, update_data)
            if modified_count:
                logger.info(f"Task updated: ID {task_id}")
                return "Task updated successfully"
            else:
                raise ValueError("No Task found with the provided ID")
        else:
            raise ValueError("Task ID and New Description are required")

    def delete_task(self, task_id):
        if task_id:
            deleted_count = self.db_connection.delete_document('tasks', {'_id': ObjectId(task_id)})
            if deleted_count:
                logger.info(f"Task deleted: ID {task_id}")
                return "Task deleted successfully"
            else:
                raise ValueError("No Task found with the provided ID")
        else:
            raise ValueError("Task ID is required")

    def view_tasks(self, search, filter_priority, show_completed):
        query = {}
        if search:
            query['name'] = {'$regex': search, '$options': 'i'}
        if filter_priority != "All":
            query['priority'] = filter_priority
        if not show_completed:
            query['completed'] = False
        return self.db_connection.db['tasks'].find(query)


class App:
    def __init__(self):
        self.task_manager = None

    def setup(self):
        st.set_page_config(page_title="System Integration", layout="wide", page_icon="⚙️")
        st.title("🚀 System Integration")

        # Create MongoDB connection
        with MongoDBConnection(os.getenv('MONGO_PROJECT_DB')) as db_connection:
            self.task_manager = TaskManager(db_connection)

            # Sidebar for navigation
            st.sidebar.title("🔧 Navigation")
            option = st.sidebar.selectbox("Select Action", ["Add Task", "View Tasks", "Update Task", "Delete Task"])
            add_vertical_space()

            # Action handling
            if option == "Add Task":
                self.show_add_task()
            elif option == "View Tasks":
                self.show_view_tasks()
            elif option == "Update Task":
                self.show_update_task()
            elif option == "Delete Task":
                self.show_delete_task()

    def show_add_task(self):
        st.subheader("📝 Add a New Task")
        task_name = st.text_input("Task Name")
        task_description = st.text_area("Task Description")
        task_priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        due_date = st.date_input("Due Date", datetime.date.today())

        if st.button("Add Task"):
            try:
                message = self.task_manager.add_task(task_name, task_description, task_priority, due_date)
                st.success(message)
            except ValueError as e:
                st.error(str(e))

    def show_view_tasks(self):
        st.subheader("📋 View All Tasks")
        search = st.text_input("Search by Task Name")
        filter_priority = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High"], index=0)
        show_completed = st.checkbox("Show Completed Tasks")

        tasks = self.task_manager.view_tasks(search, filter_priority, show_completed)
        st.dataframe(tasks)

    def show_update_task(self):
        st.subheader("✏️ Update a Task")
        task_id = st.text_input("Task ID")
        new_description = st.text_area("New Description")
        new_priority = st.selectbox("New Priority", ["Low", "Medium", "High"])
        new_due_date = st.date_input("New Due Date", datetime.date.today())
        completed = st.checkbox("Mark as Completed")

        if st.button("Update Task"):
            try:
                message = self.task_manager.update_task(task_id, new_description, new_priority, new_due_date, completed)
                st.success(message)
            except ValueError as e:
                st.error(str(e))

    def show_delete_task(self):
        st.subheader("❌ Delete a Task")
        task_id = st.text_input("Task ID to delete")
        if st.button("Delete Task"):
            try:
                message = self.task_manager.delete_task(task_id)
                st.success(message)
            except ValueError as e:
                st.error(str(e))


if __name__ == "__main__":
    app = App()
    app.setup()
