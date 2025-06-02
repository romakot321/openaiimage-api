from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging
from loguru import logger
from sqladmin import Admin
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.config import settings
from src.core.admin import authentication_backend
import src.core.logging_setup

from src.db.engine import engine
from src.tasks.presentation.admin import TaskAdmin
from src.tasks.presentation.api import router as tasks_router
from src.tasks.presentation.api import public_router as tasks_public_router
from src.tasks.presentation.api_v2 import router as tasks_v2_router
from src.tasks.presentation.api_v2 import public_router as tasks_public_v2_router
from src.auth.presentation.api import router as auth_router
from src.users.presentation.api import router as user_router
from src.users.presentation.admin import UserAdmin
# from src.contexts.presentation.admin import ContextAdmin
from src.contexts.presentation.api import router as contexts_router
from src.models.presentation.admin import ModelAdmin, ModelUserInputsAdmin, ModelCategoryAdmin
from src.models.presentation.api import router as models_router

from src.integration.infrastructure.external_api.openai.fake import FakeOpenAIAdapter
from src.integration.presentation.dependencies import get_openai_adapter


def setup_test_env(app: FastAPI):
    app.dependency_overrides[get_openai_adapter] = lambda: FakeOpenAIAdapter()


app = FastAPI(title=settings.PROJECT_NAME)

Instrumentator().instrument(app).expose(app, endpoint='/metrics', include_in_schema=False)

app.include_router(tasks_router, tags=["Task"], prefix="/api/task")
app.include_router(tasks_public_router, tags=["Task"], prefix="/api/task")
app.include_router(models_router, tags=["Model"], prefix="/api/model")
app.include_router(contexts_router, tags=["Context"], prefix="/api/context")
app.mount("/storage", StaticFiles(directory="storage"))

app.include_router(tasks_v2_router, tags=["Task V2"], prefix="/api/v2/task")
app.include_router(tasks_public_v2_router, tags=["Task V2"], prefix="/api/v2/task")
app.include_router(auth_router, tags=["Auth"], prefix="/api/v2/auth")
app.include_router(user_router, tags=["User"], prefix="/api/v2/user")


admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(TaskAdmin)
admin.add_view(ModelAdmin)
admin.add_view(ModelUserInputsAdmin)
admin.add_view(ModelCategoryAdmin)
admin.add_view(UserAdmin)


if settings.ENVIRONMENT == "test":
    setup_test_env(app)
