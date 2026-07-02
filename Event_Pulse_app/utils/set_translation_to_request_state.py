from fastapi import Request
from Event_Pulse_app.models import User
from Event_Pulse_app.utils.translations import translations



def set_translation_to_request_state(user: User, request: Request):
    lang_from_db = user.preffered_lang
    if request.state.lang != lang_from_db:
        request.state.lang = lang_from_db
        request.state.t = translations.get(lang_from_db, translations["RU"])