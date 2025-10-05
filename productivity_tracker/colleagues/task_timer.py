from streamlit.delta_generator import DeltaGenerator

from ..controller import Controller
from ..app_state import AppState


# TODO: 現在の実行状況も確認できると良い
def task_timer(
    gen: DeltaGenerator,
    app_state: AppState,
    controller: Controller,
) -> None:

    gen.selectbox(
        app_state.get_language().job_timer_selectbox,
        key=app_state.key_task_timer.selectbox,
        options=app_state.get_tasks(),
        disabled=app_state.get_state(app_state.key_task_timer.selectbox_disabled),
    )
    gen.button(
        app_state.get_language().job_timer_button_start,
        key=app_state.key_task_timer.button_start,
        disabled=app_state.get_state(app_state.key_task_timer.button_start_disabled),
        on_click=controller.click_start_task,
    )
    gen.button(
        app_state.get_language().job_timer_button_stop,
        key=app_state.key_task_timer.button_stop,
        disabled=app_state.get_state(app_state.key_task_timer.button_stop_disabled),
        on_click=controller.click_stop_task,
    )
