import streamlit as st

from productivity_tracker import colleagues as col
from productivity_tracker.controller import Controller
from productivity_tracker.app_state import AppState

# --------- init context & controller -------------- #
app_state = AppState(
    state=st.session_state,
)
controller = Controller(app_state=app_state)

# --------- init streamlit-------------- #
st.set_page_config(page_title=app_state.get_language().main_page_title, layout="wide")

# ダークモードをデフォルトに設定
st.markdown("""
<style>
    .stApp {
        color-scheme: dark;
    }
    .stApp > header {
        background-color: transparent;
    }
    .stApp > div > div > div > div > div > div {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

# --------- construct -------------- #
# TODO: configで読み込んで配置をカスタマイズできるようにする
row_0 = st.columns([9, 1])
row_1 = st.columns([1])
row_2 = st.columns([1, 1])
row_3 = st.columns([2, 1])
row_4 = st.columns([1, 1])

row_0[0].title(app_state.get_language().main_title)
col.message_area(row_1[0], app_state, controller)
col.date_selection(row_2[0], app_state, controller)
col.working_hours_schedule(row_2[1], app_state)
col.timeline_chart(
    row_3[0],
    app_state,
)
col.task_timer(
    row_3[1],
    app_state,
    controller,
)

col.task_addition_manually(
    row_3[1],
    app_state,
    controller,
)
col.task_creation(
    row_3[1],
    app_state,
    controller,
)
col.task_logs(
    row_4[0],
    app_state,
    controller,
)
