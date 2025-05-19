from sqladmin import ModelView

from src.models.infrastructure.db.orm import ModelCategoryDB, ModelDB, ModelUserInputDB


class ModelAdmin(ModelView, model=ModelDB):
    name = "Models"
    column_list = [ModelDB.title, ModelDB.image]
    column_searchable_list = [ModelDB.id, ModelDB.title]
    column_default_sort = [(ModelDB.created_at, True)]


class ModelUserInputsAdmin(ModelView, model=ModelUserInputDB):
    name = "Models inputs"
    column_list = "__all__"
    column_searchable_list = [ModelUserInputDB.id, ModelUserInputDB.prompt_id]


class ModelCategoryAdmin(ModelView, model=ModelCategoryDB):
    name = "Models categories"
    column_list = "__all__"
    column_searchable_list = [ModelCategoryDB.name]
    column_default_sort = [(ModelCategoryDB.created_at, True)]

