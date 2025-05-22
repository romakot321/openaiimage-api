from sqladmin import ModelView

from src.tasks.infrastructure.db.orm import TaskDB


class TaskAdmin(ModelView, model=TaskDB):
    name = "Task"
    column_list = [TaskDB.id, TaskDB.error]
