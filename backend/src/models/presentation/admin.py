from sqladmin import ModelView
from sqladmin.formatters import Markup

from src.models.infrastructure.db.orm import ModelCategoryDB, ModelDB, ModelUserInputDB
import wtforms


def format_image_url_in_detail(model, attribute) -> Markup:
    if getattr(model, attribute) is None:
        return Markup("<div></div>")
    return Markup(
        f'<img style="width: 100%; max-width: 300px;" src="/{getattr(model, attribute)}" />'
    )


def format_image_url_in_list(model, attribute) -> Markup:
    if getattr(model, attribute) is None:
        return Markup("<div></div>")
    return Markup(
        f'<img style="width: 100%; max-width: 80px;" src="/{getattr(model, attribute)}" />'
    )


def format_text(model, attribute) -> Markup:
    return Markup(
        f'<p style="width: 100%; max-width: 100%; text-wrap: wrap;">{getattr(model, attribute)}</p>'
    )


class ModelAdmin(ModelView, model=ModelDB):
    name = "Model"
    column_list = [
        ModelDB.image,
        ModelDB.title,
        ModelDB.category_name,
        ModelDB.position,
        ModelDB.enabled,
        ModelDB.tasks_count,
    ]
    column_searchable_list = [ModelDB.id, ModelDB.title]
    column_default_sort = [(ModelDB.created_at, True)]
    column_sortable_list = [ModelDB.position, ModelDB.created_at, ModelDB.tasks_count]

    column_formatters = {"image": format_image_url_in_list}
    column_labels = {
        ModelDB.image: "Превью",
        ModelDB.category_name: "Категория",
        ModelDB.tasks_count: "Генераций",
        ModelDB.title: "Название",
        ModelDB.enabled: "Активна",
        ModelDB.position: "Позиция",
    }
    column_formatters_detail = {
        "image": format_image_url_in_detail,
        "text": format_text,
    }
    form_overrides = {"text": wtforms.TextAreaField}
    form_excluded_columns = [ModelDB.category_name, ModelDB.category, ModelDB.tasks]
    page_size = 50


class ModelUserInputsAdmin(ModelView, model=ModelUserInputDB):
    name = "Models input"
    column_list = "__all__"
    column_searchable_list = [ModelUserInputDB.id]


class ModelCategoryAdmin(ModelView, model=ModelCategoryDB):
    name = "Models categorie"

    column_list = [ModelCategoryDB.name, ModelCategoryDB.position, ModelCategoryDB.enabled]
    column_labels = {
        ModelCategoryDB.name: "Название",
        ModelCategoryDB.position: "Позиция",
        ModelCategoryDB.enabled: "Активна",
    }
    column_searchable_list = [ModelCategoryDB.name, ModelCategoryDB.position]
    column_default_sort = [(ModelCategoryDB.position, False)]
