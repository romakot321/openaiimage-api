from fastapi import FastAPI
from sqladmin import Admin
from starlette.datastructures import FormData, UploadFile
from starlette.requests import Request
import io

from .views import PromptCategoryView, TaskView, PromptView, TaskImageView, TaskItemView, PromptUserInputView
from .auth import authentication_backend
from app.db.tables import engine


class FixedAdmin(Admin):
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
                form_data.append((key, f))
            else:
                form_data.append((key, value))
        return FormData(form_data)


def attach_admin_panel(application: FastAPI):
    admin = FixedAdmin(application, engine.engine, authentication_backend=authentication_backend)

    admin.add_view(TaskView)
    admin.add_view(PromptView)
    admin.add_view(TaskImageView)
    admin.add_view(TaskItemView)
    admin.add_view(PromptUserInputView)
    admin.add_view(PromptCategoryView)

