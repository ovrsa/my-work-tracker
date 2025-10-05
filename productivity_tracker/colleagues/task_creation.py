import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from ..controller import Controller
from ..app_state import AppState


def task_creation(
    gen: DeltaGenerator,
    app_state: AppState,
    controller: Controller,
) -> None:

    with gen.expander(app_state.get_language().job_creation_expander):
        st.radio(
            app_state.get_language().job_creation_radio,
            key=app_state.key_task_creation.radio,
            options=app_state.task_creation_radio_values,
            horizontal=True,
        )
        st.selectbox(
            app_state.get_language().job_creation_selectbox,
            key=app_state.key_task_creation.selectbox,
            options=app_state.get_project_categories(),
            disabled=app_state.get_state(app_state.key_task_creation.selectbox_disabled),
        )
        st.checkbox(
            app_state.get_language().job_creation_checkbox,
            key=app_state.key_task_creation.checkbox,
            disabled=app_state.get_state(app_state.key_task_creation.checkbox_disabled),
            # on_change=controller.change_checkbox_not_select_category,
        )
        st.text_input(
            app_state.get_language().job_creation_text_input,
            key=app_state.key_task_creation.input,
        )
        st.button(
            app_state.get_language().job_creation_button,
            key=app_state.key_task_creation.button,
            on_click=controller.click_create_task_or_category,
            disabled=app_state.get_state(app_state.key_task_creation.button_disabled),
        )
