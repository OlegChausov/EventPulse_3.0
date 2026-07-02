from .ping import router as ping_router
from .register import router as register_router
from .profile import router as profile_router
from .login import router as login_router
from .logout import router as logout_router
from .profile import router as profile_router
from .profile_edit import router as profile_edit_router
from .profile_query_router import router as get_query_list_router
from .profile_query_router import router1 as query_form_router
from .profile_query_router import router2 as add_query_router
from .profile_query_router import router3 as deactivate_query_router
from .profile_query_router import router4 as query_bulk_action_router
from .profile_event_router import router as profile_event_router
from .profile_event_router import router1 as profile_event_router_to_dectivate_query
from .profile_event_router import router2 as profile_event_dectivate_router
from .profile_event_router import router3 as profile_event_bulk_action_router
from .oauth0 import router as oauth0_login_roter
from .oauth0 import router1 as oauth0_callback_roter


all_routers = [
ping_router,
register_router,
profile_router,
login_router,
logout_router,
profile_router,
profile_edit_router,
get_query_list_router,
query_form_router,
add_query_router,
deactivate_query_router,
profile_event_router,
profile_event_router_to_dectivate_query,
profile_event_dectivate_router,
profile_event_bulk_action_router,
query_bulk_action_router,
oauth0_login_roter,
oauth0_callback_roter,




]