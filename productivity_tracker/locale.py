from pydantic import BaseModel, StrictStr


class Language(BaseModel):
    language: StrictStr
    # main
    main_page_title: StrictStr
    main_title: StrictStr
    # date_selection
    date_selection_date_input: StrictStr
    date_selection_button: StrictStr
    # job_addition_manually
    job_addition_manually_expander: StrictStr
    job_addition_manually_selectbox: StrictStr
    job_addition_manually_slider: StrictStr
    job_addition_manually_button: StrictStr
    # job_creation
    job_creation_expander: StrictStr
    job_creation_radio: StrictStr
    job_creation_selectbox: StrictStr
    job_creation_checkbox: StrictStr
    job_creation_text_input: StrictStr
    job_creation_button: StrictStr
    # job_logs
    job_logs_selectbox: StrictStr
    job_logs_slider: StrictStr
    job_logs_button: StrictStr
    # job_timer
    job_timer_selectbox: StrictStr
    job_timer_button_start: StrictStr
    job_timer_button_stop: StrictStr
    # note_area
    note_area_text_area: StrictStr
    note_area_button: StrictStr
    # TODO: timeline_chart
    # working_hours_schedule
    working_hours_schedule_slider: StrictStr
    # locale_selection
    language_selection_selectbox: StrictStr

    def __str__(self) -> str:
        return self.language


class LanguageEN(Language):
    def __init__(self) -> None:
        super().__init__(
            language="English",
            main_page_title="Work Report",
            main_title="Work Report",
            date_selection_date_input="Date",
            date_selection_button="Today",
            job_addition_manually_expander="Register a record manually",
            job_addition_manually_selectbox="What you did?",
            job_addition_manually_slider="When did you do?",
            job_addition_manually_button="Register",
            job_creation_expander="Create a job/category",
            job_creation_radio="Which do you register?",
            job_creation_selectbox="Which category does the job belong to?",
            job_creation_checkbox="Select no category",
            job_creation_text_input="Job/Category name",
            job_creation_button="Create",
            job_logs_selectbox="Job",
            job_logs_slider="Hours worked",
            job_logs_button="Revise",
            job_timer_selectbox="Which job do you start/stop?",
            job_timer_button_start="Start",
            job_timer_button_stop="Stop",
            note_area_text_area="Note",
            note_area_button="Save",
            working_hours_schedule_slider="How long do you plan to work today?",
            language_selection_selectbox="Language",
        )
