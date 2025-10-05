from datetime import datetime, time
from typing import Tuple, TypedDict

import pandas as pd
from plotly import express as px
from streamlit.delta_generator import DeltaGenerator

from ..app_state import AppState


class FigDict(TypedDict):
    job_id: int
    job: str
    start: datetime
    end: datetime
    status: str


def timeline_chart(
    gen: DeltaGenerator,
    app_state: AppState,
) -> None:

    work_entries = app_state.get_work_entries()
    work_entry_in_progress = app_state.get_work_entry_in_progress()

    dict_work_entries = [
        FigDict(
            # TODO: 長い場合に備えてリミット設けて...表記
            job_id=work_entry.task.id,
            job=str(work_entry.task),
            start=work_entry.start,
            end=work_entry.end,  # type: ignore[typeddict-item]
            status="Finished",
        )
        for work_entry in work_entries
    ]

    if work_entry_in_progress is not None:
        dict_work_entry = FigDict(
            # TODO: 長い場合に備えてリミット設けて...表記
            job_id=work_entry_in_progress.task.id,
            job=str(work_entry_in_progress.task),
            start=work_entry_in_progress.start,
            end=datetime.now(),
            status="InProgress",
        )
        dict_work_entries.append(dict_work_entry)

    if dict_work_entries == []:
        return

    df = pd.DataFrame(dict_work_entries)

    fig = px.timeline(
        df,
        x_start="start",
        x_end="end",
        y="job",
        color="status",
    )
    fig.update_yaxes(autorange="reversed")

    selected_date = app_state.get_selected_date()
    scheduled_working_time: Tuple[time, time] = app_state.get_state(
        app_state.key_working_hours_schedule.slider
    )
    scheduled_working_datetime = (
        datetime.combine(selected_date, scheduled_working_time[0]),
        datetime.combine(selected_date, scheduled_working_time[1]),
    )
    fig.add_vline(x=scheduled_working_datetime[0])
    fig.add_vline(x=scheduled_working_datetime[1])
    gen.plotly_chart(
        fig, key=app_state.key_timeline_chart.chart, use_container_width=True
    )
