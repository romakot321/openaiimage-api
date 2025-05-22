from sqladmin import ModelView

from src.users.infrastructure.db.orm import UserDB


class UserAdmin(ModelView, model=UserDB):
    name = "User"
    column_list = [UserDB.id, UserDB.external_id, UserDB.app_bundle, UserDB.tokens, UserDB.created_at]
    column_default_sort = [(UserDB.created_at, True)]
    column_labels = {UserDB.external_id: "user_id", UserDB.id: "internal id"}
