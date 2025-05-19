from fastapi import FastAPI
import logging
from sqladmin import Admin
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.config import settings
#import src.core.logging_setup

from src.db.engine import engine
from src.tasks.presentation.admin import TaskAdmin
from src.tasks.presentation.api import router as tasks_router
# from src.contexts.presentation.admin import ContextAdmin
from src.contexts.presentation.api import router as contexts_router
from src.models.presentation.admin import ModelAdmin, ModelUserInputsAdmin, ModelCategoryAdmin
from src.models.presentation.api import router as models_router

from src.integration.infrastructure.external_api.openai.fake import FakeOpenAIAdapter
from src.integration.presentation.dependencies import get_openai_adapter

logger = logging.getLogger(__name__)


def setup_test_env(app: FastAPI):
    app.dependency_overrides[get_openai_adapter] = lambda: FakeOpenAIAdapter()


app = FastAPI(title=settings.PROJECT_NAME)

Instrumentator().instrument(app).expose(app, endpoint='/metrics', include_in_schema=False)

app.include_router(tasks_router, tags=["Task"], prefix="/api/task")
app.include_router(models_router, tags=["Model"], prefix="/api/model")
app.include_router(contexts_router, tags=["Context"], prefix="/api/context")


admin = Admin(app, engine)
admin.add_view(TaskAdmin)
admin.add_view(ModelAdmin)
admin.add_view(ModelUserInputsAdmin)
admin.add_view(ModelCategoryAdmin)


if settings.ENVIRONMENT == "test":
    setup_test_env(app)
