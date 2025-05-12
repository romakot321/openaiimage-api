from fastapi import UploadFile
from app.db.tables import Task, Prompt, TaskItem, TaskImage, PromptUserInput
from sqladmin import ModelView
from sqladmin.formatters import Markup
from wtforms import FileField


def format_image_url(model, attribute) -> Markup:
    return Markup(f'<img src="{getattr(model, attribute)}" />')


class TaskView(ModelView, model=Task):
    column_list = "__all__"
    column_searchable_list = [Task.id, Task.user_id, Task.app_bundle]
    column_default_sort = [(Task.created_at, True)]


class TaskImageView(ModelView, model=TaskImage):
    column_list = "__all__"
    column_searchable_list = [TaskImage.id]
    column_default_sort = [(TaskImage.created_at, True)]


class TaskItemView(ModelView, model=TaskItem):
    column_list = "__all__"
    column_searchable_list = [TaskItem.id]


class PromptView(ModelView, model=Prompt):
    column_list = [Prompt.title, Prompt.image, Prompt.text]
    column_searchable_list = [Prompt.id, Prompt.title]
    column_default_sort = [(Prompt.created_at, True)]
    column_formatters = {"image": format_image_url}
    column_formatters_detail = {"image": format_image_url}
    form_overrides = dict(image=FileField)

    async def on_model_change(self, data: dict, model, is_created, request):
        if is_created:
            data['image'] = await data['image'].read()
            if not data['image']:
                data['image'] = None
        return data


class PromptUserInputView(ModelView, model=PromptUserInput):
    column_list = "__all__"
    column_searchable_list = [PromptUserInput.id]
