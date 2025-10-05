from . import business_logic
from . import controller
from . import app_state
from . import locale
from . import view_models
from .data import entities
from .data import connection

# Import classes for forward reference resolution
from .app_state import AppState
from .business_logic import ProjectCategory, Task, WorkEntry
from .view_models import ProjectCategory as ViewProjectCategory, Task as ViewTask, WorkEntry as ViewWorkEntry

# Forward reference resolution
from . import controller
controller.Controller.model_rebuild()
