from telegram.ext import Application, CommandHandler

from .admin import (
    add_course,
    add_group,
    delete_course,
    delete_group,
    edit_course,
    edit_group,
    list_courses,
    list_groups,
)
from .starting import help
from .user import main_menu_handler, registration_handler


def register_handler(app: Application) -> None:
    app.add_handler(registration_handler())
    app.add_handler(main_menu_handler())
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("add_group", add_group))
    app.add_handler(CommandHandler("groups", list_groups))
    app.add_handler(CommandHandler("edit_group", edit_group))
    app.add_handler(CommandHandler("delete_group", delete_group))
    app.add_handler(CommandHandler("add_subject", add_course))
    app.add_handler(CommandHandler("subjects", list_courses))
    app.add_handler(CommandHandler("edit_subject", edit_course))
    app.add_handler(CommandHandler("delete_subject", delete_course))
