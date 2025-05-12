import io
from fastapi import Request
from starlette.datastructures import FormData, UploadFile
from app.db.tables import Task, Prompt, TaskItem, TaskImage, PromptUserInput
from sqladmin import ModelView
from sqladmin.formatters import Markup
from wtforms import FileField
import base64


def format_image_url(model, attribute) -> Markup:
    return Markup(f'<img src="data:image/png;base64, {base64.b64encode(getattr(model, attribute)).decode()}" />')


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

    async def _handle_form_data(self, request: Request, obj = None) -> FormData:
        """
        Handle form data and modify in case of UploadFile.
        This is needed since in edit page
        there's no way to show current file of object.
        """

        form = await request.form()
        form_data: list[tuple[str, str | UploadFile]] = []
        for key, value in form.multi_items():
            if not isinstance(value, UploadFile):
                form_data.append((key, value))
                continue

            should_clear = form.get(key + "_checkbox")
            empty_upload = len(await value.read(1)) != 1
            await value.seek(0)
            if should_clear:
                form_data.append((key, UploadFile(io.BytesIO(b""))))
            elif empty_upload and obj and getattr(obj, key):
                f = getattr(obj, key)  # In case of update, imitate UploadFile
                form_data.append((key, UploadFile(filename="tmp.png", file=f.open())))
            else:
                form_data.append((key, value))
        return FormData(form_data)

    async def on_model_change(self, data: dict, model, is_created, request):
        if is_created:
            data['image'] = await data['image'].read()
            if not data['image']:
                data['image'] = None
        return data


class PromptUserInputView(ModelView, model=PromptUserInput):
    column_list = "__all__"
    column_searchable_list = [PromptUserInput.id]
