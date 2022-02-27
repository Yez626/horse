from sqladmin import Admin, ModelAdmin

from joj.horse.models import *  # noqa: F403

# from sqladmin.models import ModelAdminMeta


# from starlette.requests import Request


# class UserAdmin(ModelAdmin, model=User):
#     def is_accessible(self, request: Request) -> bool:
#         # Do any check you need with the incoming request; for example check headers
#         return True

#     def is_visible(self, request: Request) -> bool:
#         # Do any check you need with the incoming request; for example check headers
#         return True


class UserAdmin(ModelAdmin, model=User):  # type: ignore # noqa: F405
    pass


class DomainAdmin(ModelAdmin, model=Domain):  # type: ignore # noqa: F405
    pass


def register_admin_models(admin: Admin) -> None:
    # print(UserAdmin.__bases__)
    # print(UserAdmin.__dict__)
    # g = type("UserAdmin", (ModelAdmin,), {})
    # print(g.__bases__)
    # print(g.__dict__)
    admin.register_model(UserAdmin)
    admin.register_model(DomainAdmin)
