import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from ..controller import Controller
from ..app_state import AppState


def task_logs(
    gen: DeltaGenerator,
    app_state: AppState,
    controller: Controller,
) -> None:
    for i, work_entry in enumerate(app_state.get_work_entries()):
        key_selectbox = f"{app_state.key_task_logs.selectbox}_{i}"
        key_slider = f"{app_state.key_task_logs.slider}_{i}"
        key_button = f"{app_state.key_task_logs.button}_{i}"

        with gen.expander(str(work_entry), expanded=False):
            st.selectbox(
                app_state.get_language().job_logs_selectbox,
                key=key_selectbox,
                options=app_state.get_tasks(),
                index=app_state.get_tasks().index(work_entry.task),
            )

            time_start = work_entry.start.time()
            time_end = work_entry.end.time()
            st.slider(
                app_state.get_language().job_logs_slider,
                key=key_slider,
                value=(time_start, time_end),
            )
            st.button(
                app_state.get_language().job_logs_button,
                key=key_button,
                on_click=controller.click_edit_work_entry,
                args=(key_selectbox, key_slider, work_entry.id),
            )
