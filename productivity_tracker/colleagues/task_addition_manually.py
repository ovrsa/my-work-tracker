from datetime import time
from typing import Tuple

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from ..controller import Controller
from ..app_state import AppState


def task_addition_manually(
    gen: DeltaGenerator,
    app_state: AppState,
    controller: Controller,
    *,
    default: Tuple[time, time] | None = (time(9, 0), time(18, 0)),
) -> None:

    with gen.expander(
        app_state.get_language().job_addition_manually_expander, expanded=True
    ):
        st.selectbox(
            app_state.get_language().job_addition_manually_selectbox,
            key=app_state.key_task_addition_manually.selectbox,
            options=app_state.get_tasks(),
            disabled=app_state.get_state(
                app_state.key_task_addition_manually.selectbox_disabled
            ),
        )
        st.slider(
            app_state.get_language().job_addition_manually_slider,
            key=app_state.key_task_addition_manually.slider,
            value=default,
            disabled=app_state.get_state(
                app_state.key_task_addition_manually.slider_disabled
            ),
        )
        st.button(
            app_state.get_language().job_addition_manually_button,
            key=app_state.key_task_addition_manually.button,
            on_click=controller.click_add_work_entry,
            disabled=app_state.get_state(
                app_state.key_task_addition_manually.button_disabled
            ),
        )
