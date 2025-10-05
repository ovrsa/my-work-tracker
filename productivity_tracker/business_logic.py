from datetime import date, datetime
from typing import Final, List

from pony.orm import db_session
from pony.orm.core import TransactionIntegrityError

from . import view_models
from .data import entities as models

# register >  update > delete > acquire-many > acquire-one


class LogicException(Exception):
    pass


class ProjectCategory:
    @staticmethod
    def register(name: str) -> None:
        """Register a project category

        Args:
            name (str): Project category name

        Raises:
            LogicException: Occurs when trying to register same project category name
        """
        try:
            with db_session(serializable=True, strict=True):
                models.ProjectCategory.insert(name)
        except TransactionIntegrityError as error:
            raise LogicException from error

    @staticmethod
    @db_session(serializable=True, strict=True)  # type: ignore[misc]
    def acquire_all() -> List[view_models.ProjectCategory]:
        """Acquire all project categories and convert to view model

        Returns:
            List[view_models.ProjectCategory]: All project categories
        """

        db_categories = models.ProjectCategory.select_all()

        return [
            view_models.ProjectCategory.from_orm(db_category) for db_category in db_categories
        ]


class Task:
    @staticmethod
    def register(task_name: str, category_name: str | None = None) -> None:
        """Register a task.

        Args:
            task_name (str): Task name
            category_name (str | None): Category name

        Raises:
            LogicException:
                - Occurs when trying to register same combination of task name and category name.
                - Occurs when category is specified but not found in the database.
        """

        try:
            with db_session(serializable=True, strict=True):
                if category_name is None:
                    models.Task.insert(task_name, None)
                    return

                db_project_category = models.ProjectCategory.select_one_by_name(category_name)
                if db_project_category is None:
                    raise LogicException("Project category is specified, but not found.")
                models.Task.insert(task_name, db_project_category)

        except (TransactionIntegrityError, models.CRUDException) as error:
            raise LogicException(error) from error

    @staticmethod
    @db_session(serializable=True, strict=True)  # type: ignore[misc]
    def acquire_all() -> List[view_models.Task]:
        """Acquire all tasks and convert to view model

        Returns:
            List[view_models.Task]: All tasks
        """

        db_tasks = models.Task.select_all()
        return [view_models.Task.from_orm(db_task) for db_task in db_tasks]


class WorkEntry:
    @classmethod
    def __replace_second_0(cls, __datetime: datetime) -> datetime:
        """Set second and microsecond to 0.

        Args:
            __datetime (datetime): Datetime

        Returns:
            datetime: Datetime
        """
        return __datetime.replace(second=0, microsecond=0)

    @classmethod
    def __judge_if_can_upsert_and_get_task(
        cls, task_id: int, start: datetime, end: datetime | None = None
    ) -> models.Task:
        """Judge if work entry can be upcert and returns the task if so.

        This private function must be used inside db_session.

        Args:
            task_id (int): Task id
            start (datetime): Start time
            end (datetime | None, optional): End time

        Raises:
            LogicException:  Occurs when future time is set for start datetime or end datetime.
            LogicException:  Occurs when specified task id cannot be found.
            LogicException:  Occurs when end datetime is smaller than equal to start datetime.
            LogicException:  Occurs when start and end are not same dates.

        Returns:
            models.Task: Task
        """
        # TODO: 登録期間で重なりがないかの検証を加える
        CURRENT_DATETIME: Final[datetime] = datetime.now()
        if start > CURRENT_DATETIME:
            raise LogicException("Start time cannot be set at future time.")

        db_task = models.Task.select_one_by_id(task_id)
        if db_task is None:
            raise LogicException(f"Task(id={task_id}) cannot be found.")

        if end is not None:
            if end > CURRENT_DATETIME:
                raise LogicException("End time cannot be set at future time.")
            if end <= start:
                raise LogicException("End time must be greater than start time.")
            if start.date() != end.date():
                raise LogicException("Start and end must be same dates.")

        return db_task
    @classmethod
    @db_session(serializable=True, strict=True)  # type: ignore[misc]
    def register(cls, job_id: int, start: datetime, end: datetime) -> None:
        """Register a job record.

        Args:
            job_id (int): Job ID
            start (datetime): Start datetime
            end (datetime): End datetime

        Raises:
            LogicException: See __judge_if_can_upsert_and_get_task()
        """
        # TODO: マルチタスクを禁止するため、start - endの時間で重なりがあるものがあればその旨をエラーにする。

        start = cls.__replace_second_0(start)
        end = cls.__replace_second_0(end)
        db_task= cls.__judge_if_can_upsert_and_get_task(job_id, start, end)
        models.WorkEntry.insert(db_task, start, end)

    @classmethod
    @db_session(serializable=True, strict=True)  # type: ignore[misc]
    def revise(
        cls, work_entry_id: int, job_id: int, start: datetime, end: datetime
    ) -> None:
        """Revise the job record specified by id.

        Args:
            work_entry_id (int): Job record id
            job_id (int): Job id
            start (datetime): Start datetime
            end (datetime): End datetime

        Raises:
            LogicException: Occurs when job record specified job id cannot be found.
            LogicException: See __judge_if_can_upcert_and_get_job()
        """
        # TODO: 終了したジョブを開始するのに変更できるようにendでnullableを許容する

        db_work_entry = models.WorkEntry.select_one_by_id(work_entry_id)
        if db_work_entry is None:
            raise LogicException(f"WorkEntry(id={work_entry_id}) cannot be found")

        start = cls.__replace_second_0(start)
        end = cls.__replace_second_0(end)
        db_task = WorkEntry.__judge_if_can_upsert_and_get_task(job_id, start, end)
        models.WorkEntry.update(db_work_entry, db_task, start, end)

    @classmethod
    @db_session(serializable=True, strict=True)  # type: ignore[misc]
    def start(cls, job_id: int) -> None:
        """Start a job record specified by job id.

        Args:
            job_id (int): Job id

        Raises:
            LogicException: Occurs when one job has been already started.
            LogicException: See __judge_if_can_upsert_and_get_task()
        """
        current_datetime = datetime.now()
        work_entry_in_progress = models.WorkEntry.select_one_in_progress_by_date(
            current_datetime.date()
        )
        if work_entry_in_progress is not None:
            raise LogicException(
                f"WorkEntry(id={work_entry_in_progress.id}) is already started."
            )

        start = cls.__replace_second_0(datetime.now())
        db_task= cls.__judge_if_can_upsert_and_get_task(job_id, start, None)
        models.WorkEntry.insert(db_task, start)

    @classmethod
    @db_session(serializable=True, strict=True)  # type: ignore[misc]
    def stop(cls, work_entry_id: int) -> None:
        """Stop a job record specified by job record id.

        Args:
            work_entry_id (int): Job record id

        Raises:
            LogicException: Occurs when job record specified job id cannot be found.
            LogicException: Occurs when the job was already stopped.
        """

        current_datetime = datetime.now()
        db_work_entry = models.WorkEntry.select_one_by_id(work_entry_id)
        if db_work_entry is None:
            raise LogicException(f"WorkEntry(id={work_entry_id}) cannot be found.")
        if db_work_entry.end is not None:
            raise LogicException(f"WorkEntry(id={work_entry_id}) is already stopped.")

        models.WorkEntry.update_end(db_work_entry, current_datetime)

    # TODO: docstring
    @classmethod
    @db_session(serializable=True, strict=True)  # type: ignore[misc]
    def acquire_all_finished_by_date(cls, __date: date) -> List[view_models.WorkEntry]:
        db_work_entries = models.WorkEntry.select_all_finished_by_date(__date)
        return [
            view_models.WorkEntry.from_orm(db_work_entry)
            for db_work_entry in db_work_entries
        ]

    # TODO: docstring
    @classmethod
    @db_session(serializable=True, strict=True)  # type: ignore[misc]
    def acquire_one_in_progress_by_date(
        cls, __date: date
    ) -> view_models.WorkEntry | None:
        db_work_entry = models.WorkEntry.select_one_in_progress_by_date(__date)
        if db_work_entry is None:
            return None

        return view_models.WorkEntry.from_orm(db_work_entry)

