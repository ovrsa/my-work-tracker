from datetime import time
from typing import Tuple

from streamlit.delta_generator import DeltaGenerator

from ..app_state import AppState


def working_hours_schedule(
    gen: DeltaGenerator,
    app_state: AppState,
    *,
    default: Tuple[time, time] | None = (time(9, 0), time(18, 0)),
) -> None:
    gen.slider(
        app_state.get_language().working_hours_schedule_slider,
        key=app_state.key_working_hours_schedule.slider,
        value=default,
    )
