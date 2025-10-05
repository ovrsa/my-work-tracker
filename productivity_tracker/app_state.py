from datetime import date
from enum import Enum
from typing import Any, List, cast

from pydantic import BaseModel, Field, PrivateAttr
from streamlit.runtime.state import SessionStateProxy

from . import locale
from .view_models import ProjectCategory, Task, WorkEntry


class KeyMessageArea(str, Enum):
    __base = "key_message_area"
    info = f"{__base}_info"
    warn = f"{__base}_warn"
    error = f"{__base}_error"
    exception = f"{__base}_exception"


class KeyDateSelection(str, Enum):
    __base = "date_selection"
    input = f"{__base}_date_input"
    button = f"{__base}_button_today"


class KeyWorkingHoursSchedule(str, Enum):
    __base = "working_hours_schedule"
    slider = f"{__base}_slider"


class KeyTaskTimer(str, Enum):
    __base = "task_timer"
    selectbox = f"{__base}_selectbox"
    selectbox_disabled = f"{selectbox}_disabled"
    button_start = f"{__base}_button_start"
    button_start_disabled = f"{button_start}_disabled"
    button_stop = f"{__base}_button_stop"
    button_stop_disabled = f"{button_stop}_disabled"


class KeyTimelineChart(str, Enum):
    __base = "timeline_chart"
    chart = f"{__base}_chart"


class KeyTaskAdditionManually(str, Enum):
    __base = "task_addition_manually"
    selectbox = f"{__base}_selectbox"
    selectbox_disabled = f"{selectbox}_disabled"
    slider = f"{__base}_slider"
    slider_disabled = f"{slider}_disabled"
    button = f"{__base}_button"
    button_disabled = f"{__base}_disabled"


class KeyTaskCreation(str, Enum):
    __base = "task_creation"
    radio = f"{__base}_radio"
    selectbox = f"{__base}_selectbox"
    selectbox_disabled = f"{selectbox}_disabled"
    checkbox = f"{__base}_checkbox"
    checkbox_disabled = f"{checkbox}_disabled"
    input = f"{__base}_input"
    button = f"{__base}_button"
    button_disabled = f"{button}_disabled"


class KeyTaskLogs(str, Enum):
    __base = "task_logs"
    selectbox = f"{__base}_selectbox"
    slider = f"{__base}_slider"
    button = f"{__base}_button"


class KeyLanguageSelection(str, Enum):
    __base = "language_selection"
    selectbox = f"{__base}_selectbox"


class RadioTaskCreation(str, Enum):
    job = "job"
    category = "category"

    @classmethod
    def get_values(cls) -> List[str]:
        return [e.value for e in cls]


class AppState(BaseModel):
    state: SessionStateProxy
    key_message_area: KeyMessageArea = Field(default_factory=lambda: KeyMessageArea)
    key_date_selection: KeyDateSelection = Field(default_factory=lambda: KeyDateSelection)
    key_working_hours_schedule: KeyWorkingHoursSchedule = Field(default_factory=lambda: KeyWorkingHoursSchedule)
    key_task_timer: KeyTaskTimer = Field(default_factory=lambda: KeyTaskTimer)
    key_timeline_chart: KeyTimelineChart = Field(default_factory=lambda: KeyTimelineChart)
    key_task_addition_manually: KeyTaskAdditionManually = Field(default_factory=lambda: KeyTaskAdditionManually)
    key_task_creation: KeyTaskCreation = Field(default_factory=lambda: KeyTaskCreation)
    key_task_logs: KeyTaskLogs = Field(default_factory=lambda: KeyTaskLogs)
    key_language_selection: KeyLanguageSelection = Field(default_factory=lambda: KeyLanguageSelection)

    task_creation_radio_values: List[str] = Field(default_factory=lambda: RadioTaskCreation.get_values())

    # NOTE: mediatorによって設定される
    __tasks: List[Task] = PrivateAttr()
    __work_entries: List[WorkEntry] = PrivateAttr()
    __work_entry_in_progress: WorkEntry | None = PrivateAttr()
    __project_categories: List[ProjectCategory] = PrivateAttr()
    __language: locale.Language = PrivateAttr()

    def init_state(self, key: str, value: Any) -> None:
        if key not in self.state:
            self.state[key] = value

    def set_state(self, key: str, value: Any, *, do_init: bool = False) -> None:
        if do_init:
            self.init_state(key, value)

        self.state[key] = value

    def get_state(self, key: str) -> Any:
        return self.state.get(key, None)

    def get_selected_date(self) -> date:
        return cast(date, self.get_state(self.key_date_selection.input))

    def set_tasks(self, tasks: List[Task]) -> None:
        self.__tasks = tasks

    def get_tasks(self) -> List[Task]:
        return self.__tasks

    def set_work_entries(self, work_entries: List[WorkEntry]) -> None:
        self.__work_entries = work_entries

    def get_work_entries(self) -> List[WorkEntry]:
        return self.__work_entries

    def set_work_entry_in_progress(self, work_entry: WorkEntry | None) -> None:
        self.__work_entry_in_progress = work_entry

    def get_work_entry_in_progress(self) -> WorkEntry | None:
        return self.__work_entry_in_progress

    def set_project_categories(self, project_categories: List[ProjectCategory]) -> None:
        self.__project_categories = project_categories

    def get_project_categories(self) -> List[ProjectCategory]:
        return self.__project_categories


    def set_language(self, language: locale.Language) -> None:
        self.__language = language

    def get_language(self) -> locale.Language:
        return self.__language

    def get_languages(self) -> List[locale.Language]:
        return [locale.LanguageEN()]

    model_config = {
        "arbitrary_types_allowed": True,
        "frozen": True,
    }
