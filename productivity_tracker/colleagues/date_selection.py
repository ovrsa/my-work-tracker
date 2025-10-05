from streamlit.delta_generator import DeltaGenerator

from ..controller import Controller
from ..app_state import AppState


def date_selection(
    gen: DeltaGenerator, app_state: AppState, controller: Controller
) -> None:

    gen.date_input(
        app_state.get_language().date_selection_date_input,
        key=app_state.key_date_selection.input,
    )
    gen.button(
        app_state.get_language().date_selection_button,
        key=app_state.key_date_selection.button,
        on_click=controller.click_today,
    )
