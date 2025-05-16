from typing import Annotated

from fastapi import Depends

from backend.src.models.domain.interfaces.model_uow import IModelUnitOfWork
from backend.src.models.infrastructure.db.unit_of_work import PGModelUnitOfWork


def get_model_uow() -> IModelUnitOfWork:
    return PGModelUnitOfWork()


ModelUoWDepend = Annotated[IModelUnitOfWork, Depends(get_model_uow)]
