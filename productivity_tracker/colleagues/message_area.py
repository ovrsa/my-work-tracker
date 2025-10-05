from streamlit.delta_generator import DeltaGenerator

from ..controller import Controller
from ..app_state import AppState


def message_area(
    gen: DeltaGenerator,
    app_state: AppState,
    controller: Controller,
) -> None:
    info = app_state.get_state(app_state.key_message_area.info)
    if info:
        gen.info(info)

    warn = app_state.get_state(app_state.key_message_area.warn)
    if warn:
        gen.warning(warn)

    error = app_state.get_state(app_state.key_message_area.error)
    if error:
        gen.error(error)

    exception = app_state.get_state(app_state.key_message_area.exception)
    if exception:
        gen.exception(error)

    controller.draw_message()
