def test_chat_log_without_fields_uses_message_only(app, mocker):
    from backend.chat import _log

    logger = mocker.patch.object(app, "logger")

    with app.app_context():
        _log("info", "chat event")

    logger.log.assert_called_once_with(20, "%s", "chat event")


def test_recipe_log_without_fields_uses_message_only(app, mocker):
    from backend.recipe import _log

    logger = mocker.patch.object(app, "logger")

    with app.app_context():
        _log("warning", "recipe event")

    logger.log.assert_called_once_with(30, "%s", "recipe event")


def test_user_log_without_fields_uses_message_only(app, mocker):
    from backend.user import _log

    logger = mocker.patch.object(app, "logger")

    with app.app_context():
        _log("error", "user event")

    logger.log.assert_called_once_with(40, "%s", "user event")
