from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic_settings import BaseSettings
from loguru import logger
from contextlib import asynccontextmanager
from fastapi_utils.tasks import repeat_every

from app.db.admin import attach_admin_panel
from app.services.task import TaskService


class ProjectSettings(BaseSettings):
    LOCAL_MODE: bool = False


def register_exception(application):
    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        # or logger.error(f'{exc}')
        logger.debug(f'{exc}')
        content = {'status_code': 422, 'message': exc_str, 'data': None}
        return JSONResponse(
            content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


def register_cors(application):
    application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


@repeat_every(seconds=15, wait_first=15, raise_exceptions=True)
async def process_requests():
    async with TaskService() as task_service:
        await task_service.process_requests()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await process_requests()
    yield


def init_web_application():
    project_settings = ProjectSettings()
    application = FastAPI(
        title="Task api",
        openapi_url='/openapi.json',
        docs_url='/docs',
        redoc_url='/redoc',
        lifespan=lifespan
    )

    if project_settings.LOCAL_MODE:
        register_exception(application)
        register_cors(application)

    from app.routes.task import router as task_router
    from app.routes.model import router as model_router
    from app.routes.context import router as context_router

    application.include_router(task_router)
    application.include_router(model_router)
    application.include_router(context_router)
    # application.mount("/static", StaticFiles(directory="static"), name="static")

    attach_admin_panel(application)

    return application


def run() -> FastAPI:
    logger.disable("sqlalchemy_service")
    application = init_web_application()
    return application


fastapi_app = run()
