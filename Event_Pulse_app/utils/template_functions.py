
from starlette.templating import Jinja2Templates

from Event_Pulse_app.config import TEMPLATES_DIR

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
