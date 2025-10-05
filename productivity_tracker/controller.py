from datetime import date, datetime
from typing import Any

from pydantic import BaseModel

from . import locale, business_logic as logic, app_state
from .config import DatabaseSettings
from .data.connection import DatabaseSingleton

# init database
settings = DatabaseSettings()
db = DatabaseSingleton.get_instance()
db.bind(**settings.dict_bind())
db.generate_mapping(create_tables=settings.create_tables)


class Controller(BaseModel):
    app_state: "AppState"

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)

        # 日付の初期化・取得
        self.app_state.init_state(self.app_state.key_date_selection.input, date.today())
        selected_date: date = self.app_state.get_selected_date()

        # DBからデータを取得してapp_stateにセット
        self.app_state.set_tasks(logic.Task.acquire_all())
        self.app_state.set_work_entries(
            logic.WorkEntry.acquire_all_finished_by_date(selected_date)
        )
        self.app_state.set_work_entry_in_progress(
            logic.WorkEntry.acquire_one_in_progress_by_date(selected_date)
        )
        self.app_state.set_project_categories(logic.ProjectCategory.acquire_all())

        # 言語設定
        self.app_state.set_language(locale.LanguageEN())

        # 初期化
        self.__init_message_area()

        # 状態変更
        self.__change_state_task_timer()
        self.__change_state_task_creation()
        self.__change_state_task_addition_manually()

    def __change_state_task_timer(self) -> None:
        disabled_selectbox: bool = True
        disabled_button_start: bool = True
        disabled_button_stop: bool = True

        # Determine whether each widget is disabled or not
        job_record_in_progress = self.app_state.get_work_entry_in_progress()
        jobs = self.app_state.get_tasks()
        selected_date = self.app_state.get_selected_date()
        if jobs != []:
            if job_record_in_progress is not None:
                # Set the working job to the selectbox
                self.app_state.set_state(
                    self.app_state.key_task_timer.selectbox,
                    job_record_in_progress.task,
                    do_init=True,
                )
                disabled_button_stop = False
            else:
                disabled_selectbox = False
                if selected_date == datetime.now().date():
                    disabled_button_start = False

        # Set disable or not
        self.app_state.set_state(
            self.app_state.key_task_timer.selectbox_disabled,
            disabled_selectbox,
            do_init=True,
        )
        self.app_state.set_state(
            self.app_state.key_task_timer.button_start_disabled,
            disabled_button_start,
            do_init=True,
        )
        self.app_state.set_state(
            self.app_state.key_task_timer.button_stop_disabled,
            disabled_button_stop,
            do_init=True,
        )

    def __change_state_task_creation(self) -> None:
        # Initialize
        self.app_state.init_state(
            self.app_state.key_task_creation.radio,
            app_state.RadioTaskCreation.job.value,
        )
        self.app_state.init_state(self.app_state.key_task_creation.checkbox, True)
        self.app_state.init_state(self.app_state.key_task_creation.checkbox_disabled, True)

        disabled_selectbox = True
        disabled_checkbox = True
        disabled_button = True

        value_radio = self.app_state.get_state(self.app_state.key_task_creation.radio)
        value_checkbox = self.app_state.get_state(self.app_state.key_task_creation.checkbox)
        categories = self.app_state.get_project_categories()
        match value_radio:
            case app_state.RadioTaskCreation.job.value:
                if categories != []:
                    if not value_checkbox:
                        disabled_selectbox = False
                    disabled_checkbox = False
            case app_state.RadioTaskCreation.category.value:
                pass
            case _:
                # TODO: handle error properly
                raise Exception("!?!?!?")

        value_input = self.app_state.get_state(self.app_state.key_task_creation.input)
        if value_input:
            disabled_button = False

        self.app_state.set_state(
            self.app_state.key_task_creation.selectbox_disabled,
            disabled_selectbox,
            do_init=True,
        )
        self.app_state.set_state(
            self.app_state.key_task_creation.checkbox_disabled,
            disabled_checkbox,
            do_init=True,
        )
        self.app_state.set_state(
            self.app_state.key_task_creation.button_disabled, disabled_button, do_init=True
        )

    def __change_state_task_addition_manually(self) -> None:
        disabled_selectbox = True
        disabled_slider = True
        disabled_button = True

        selected_date = self.app_state.get_selected_date()
        if selected_date == datetime.now().date():
            disabled_selectbox = False
            disabled_slider = False
            disabled_button = False

        self.app_state.set_state(
            self.app_state.key_task_addition_manually.selectbox_disabled,
            disabled_selectbox,
            do_init=True,
        )
        self.app_state.set_state(
            self.app_state.key_task_addition_manually.slider_disabled,
            disabled_slider,
            do_init=True,
        )
        self.app_state.set_state(
            self.app_state.key_task_addition_manually.button_disabled,
            disabled_button,
            do_init=True,
        )

    def __init_message_area(self) -> None:
        self.app_state.init_state(self.app_state.key_message_area.info, None)
        self.app_state.init_state(self.app_state.key_message_area.warn, None)
        self.app_state.init_state(self.app_state.key_message_area.error, None)
        self.app_state.init_state(self.app_state.key_message_area.exception, None)

    def __set_error(self, error: Exception) -> None:
        self.app_state.set_state(self.app_state.key_message_area.error, error)

    def click_today(self) -> None:
        self.app_state.set_state(self.app_state.key_date_selection.input, date.today())

    def click_start_task(self) -> None:
        job = self.app_state.get_state(self.app_state.key_task_timer.selectbox)
        logic.WorkEntry.start(job.id)

    def click_stop_task(self) -> None:
        job_record_in_progress = self.app_state.get_work_entry_in_progress()
        if job_record_in_progress is None:
            raise Exception("!?!?!?")
        logic.WorkEntry.stop(job_record_in_progress.id)

    def click_create_task_or_category(self) -> None:
        value_radio = self.app_state.get_state(self.app_state.key_task_creation.radio)
        value_input = self.app_state.get_state(self.app_state.key_task_creation.input)
        value_category = self.app_state.get_state(self.app_state.key_task_creation.selectbox)
        value_checkbox = self.app_state.get_state(self.app_state.key_task_creation.checkbox)

        try:
            match value_radio:
                case app_state.RadioTaskCreation.job.value:
                    if value_checkbox:
                        logic.Task.register(value_input)
                    else:
                        logic.Task.register(value_input, value_category.name)
                case app_state.RadioTaskCreation.category.value:
                    logic.ProjectCategory.register(value_input)
                case _:
                    # TODO: handle error properly
                    raise Exception("!?!?!?")
        except logic.LogicException as error:
            self.__set_error(error)

    def click_add_work_entry(self) -> None:
        job = self.app_state.get_state(self.app_state.key_task_addition_manually.selectbox)
        start_time, end_time = self.app_state.get_state(
            self.app_state.key_task_addition_manually.slider
        )
        try:
            logic.WorkEntry.register(
                job.id,
                datetime.combine(self.app_state.get_selected_date(), start_time),
                datetime.combine(self.app_state.get_selected_date(), end_time),
            )
        except logic.LogicException as error:
            self.__set_error(error)

    def click_edit_work_entry(
        self, key_selectbox: str, key_slider: str, job_record_id: int
    ) -> None:
        job = self.app_state.get_state(key_selectbox)
        time_start, time_end = self.app_state.get_state(key_slider)
        try:
            logic.WorkEntry.revise(
                job_record_id,
                job.id,
                datetime.combine(self.app_state.get_selected_date(), time_start),
                datetime.combine(self.app_state.get_selected_date(), time_end),
            )
        except logic.LogicException as error:
            self.__set_error(error)

    def draw_message(self) -> None:
        self.app_state.set_state(self.app_state.key_message_area.info, None)
        self.app_state.set_state(self.app_state.key_message_area.warn, None)
        self.app_state.set_state(self.app_state.key_message_area.error, None)
        self.app_state.set_state(self.app_state.key_message_area.exception, None)

    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
        copy_on_model_validation = False


