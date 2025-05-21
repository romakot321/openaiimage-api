from sqladmin import ModelView
from sqladmin.formatters import Markup

from src.models.infrastructure.db.orm import ModelCategoryDB, ModelDB, ModelUserInputDB
import wtforms


def format_image_url(model, attribute) -> Markup:
    return Markup(f'<img style="width: 100%; max-width: 300px;" src="/storage/{getattr(model, attribute)}" />')


class ModelAdmin(ModelView, model=ModelDB):
    name = "Models"
    column_list = [ModelDB.title, ModelDB.image]
    column_searchable_list = [ModelDB.id, ModelDB.title]
    column_default_sort = [(ModelDB.created_at, True)]

    column_formatters = {"image": format_image_url}
    column_formatters_detail = {"image": format_image_url}
    form_overrides = {"text": wtforms.TextAreaField}


class ModelUserInputsAdmin(ModelView, model=ModelUserInputDB):
    name = "Models inputs"
    column_list = "__all__"
    column_searchable_list = [ModelUserInputDB.id, ModelUserInputDB.prompt_id]


class ModelCategoryAdmin(ModelView, model=ModelCategoryDB):
    name = "Models categories"
    column_list = "__all__"
    column_searchable_list = [ModelCategoryDB.name]
    column_default_sort = [(ModelCategoryDB.created_at, True)]

