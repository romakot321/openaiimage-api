from sqladmin import ModelView

from src.models.infrastructure.db.orm import ModelDB


class ModelAdmin(ModelView, model=ModelDB):
    column_list = [ModelDB.title, ModelDB.image]
    column_searchable_list = [ModelDB.id, ModelDB.title]
    column_default_sort = [(ModelDB.created_at, True)]

