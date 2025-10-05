from __future__ import annotations

from datetime import date, datetime
from typing import List, cast

try:
    from typing import TypeAlias
except ImportError:
    # For Python < 3.10
    from typing_extensions import TypeAlias

from pony.orm import (
    Database,
    LongStr,
    Optional,
    PrimaryKey,
    Required,
    Set,
    composite_key,
)
from pony.orm.core import CacheIndexError

from .connection import DatabaseSingleton

Date: TypeAlias = date
DateTime: TypeAlias = datetime

db: Database = DatabaseSingleton.get_instance()


class CRUDException(Exception):
    pass


class DataAlreadyExistsError(CRUDException):
    def __init__(self, entity: db.Entity) -> None:
        message = f"{entity} is already exists."
        super().__init__(message)


class ProjectCategory(db.Entity):  # type: ignore[misc]
    _table_ = "project_categories"
    name = PrimaryKey(str)
    tasks = Set("Task")

    @classmethod
    def insert(cls, name: str) -> None:
        """Insert a project category to the database.

        Args:
            name (str): Project category name

        Raises:
            CRUDException: Occurs when instantiate by the same primary keys name within same transaction
        """
        try:
            cls(name=name)
        except CacheIndexError as error:
            raise CRUDException from error

    @classmethod
    def select_all(cls) -> List[ProjectCategory]:
        """Select all project categories from the database.

        Returns:
            List[ProjectCategory]: All project categories ordered by category name
        """
        return cast(
            List[ProjectCategory],
            cls.select().order_by(lambda x: x.name)[:],
        )

    @classmethod
    def select_one_by_name(cls, name: str) -> ProjectCategory | None:
        """Select a project category by name from the database.

        Args:
            name (str): Project category name

        Returns:
            ProjectCategory | None: Returns None if there is no such object.
        """
        return cast(ProjectCategory | None, cls.get(name=name))


class Task(db.Entity):  # type: ignore[misc]
    _table_ = "tasks"
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    project_category = Optional("ProjectCategory")
    work_entries = Set("WorkEntry")
    composite_key(name, project_category)

    # TODO: docstring修正
    @classmethod
    def insert(cls, name: str, project_category: ProjectCategory | None = None) -> None:
        """Insert a task to the database.
        Establish a relationship between task and project category if project category is given as argument.

        Raises CRUDException explicitly when trying to insert task whose project category is None and that is already inserted to the database the database.
        Because most database's composite unique constraints does not work when either of them is None.

        Args:
            name (str): Task name
            project_category (ProjectCategory | None): Project category

        Raises:
            CRUDException:
                - Occurs when instantiate by the same composite keys within same transaction
                - Occurs when trying to instantiate by the same task name that is already inserted to the database if project category is None
        """
        db_task: Task | None
        if project_category is None:
            db_task = cls.get(lambda x: x.name == name and x.project_category is None)
        else:
            db_task = cls.get(lambda x: x.name == name and x.project_category == project_category)
        if db_task is not None:
            raise DataAlreadyExistsError(db_task)

        try:
            cls(name=name, project_category=project_category)
        except CacheIndexError as error:
            raise CRUDException from error

    @classmethod
    def select_all(cls) -> List[Task]:
        """Select all tasks from the database.

        Returns:
            List[Task]: All tasks ordered by project category name and task name
        """
        return cast(
            List[Task],
            cls.select().order_by(lambda x: (x.project_category.name, x.name))[:],
        )

    @classmethod
    def select_one_by_id(cls, __id: int) -> Task | None:
        """Select a task by id from the database.

        Args:
            __id (int): Task id

        Returns:
            Task | None: Returns None if there is no such object.
        """
        return cast(Task | None, cls.get(id=__id))


class WorkEntry(db.Entity):  # type: ignore[misc]
    _table_ = "work_entries"
    id = PrimaryKey(int, auto=True)
    task = Required("Task")
    start = Required(datetime, precision=6)
    end = Optional(datetime, precision=6)

    @classmethod
    def insert(cls, task: Task, start: DateTime, end: DateTime | None = None) -> None:
        """Insert a work entry to the database.

        Args:
            task (Task): Task
            start (datetime): Start datetime
            end (datetime | None): End datetime
        """
        cls(task=task, start=start, end=end)

    @classmethod
    def update(
        cls,
        work_entry: WorkEntry,
        task: Task,
        start: DateTime,
        end: DateTime | None,
    ) -> None:
        """Update work entry in the database

        Args:
            work_entry (WorkEntry): Work entry
            task (Task): Task
            start (datetime): Start datetime
            end (datetime | None): End datetime
        """
        work_entry.task = task
        work_entry.start = start
        work_entry.end = end

    @classmethod
    def update_end(cls, work_entry: WorkEntry, end: DateTime | None) -> None:
        """Update work entry's end datetime in the database.

        Args:
            work_entry (WorkEntry): Work entry
            end (datetime | None): End datetime
        """
        cls.update(work_entry, work_entry.task, work_entry.start, end)

    @classmethod
    def select_all_finished_by_date(cls, __date: Date) -> List[WorkEntry]:
        """Select all finished work entries filtered by date from the database.

        Returns:
            List[WorkEntry]: All finished work entries filtered by date, and ordered by start datetime and id
        """
        return cast(
            List[WorkEntry],
            cls.select(
                lambda w: w.start.date() == __date and w.end.date() == __date
            ).order_by(lambda x: (x.start, x.id))[:],
        )

    @classmethod
    def select_one_by_id(cls, __id: int) -> WorkEntry | None:
        """Select a work entry by id from the database.

        Args:
            __id (int): Work entry id

        Returns:
            WorkEntry | None: Returns None if there is no such object.
        """

        return cast(WorkEntry | None, cls.get(id=__id))

    @classmethod
    def select_one_in_progress_by_date(cls, __date: Date) -> WorkEntry | None:
        """Select an in progress work entry by date from the database.

        In progress work entry is equal to the end column has None.

        Args:
            __date (int): Date

        Returns:
            WorkEntry | None: Returns None if there is no such object.
        """

        return cast(
            WorkEntry | None,
            cls.get(lambda w: w.start.date() == __date and w.end is None),
        )

    # FIXME: comment out
    # @classmethod
    # def count_overlap_forward(cls, start: DateTime) -> int:
    #     # FIXME: 実装
    #     pass

    # @classmethod
    # def count_overlap_inward(cls, start: DateTime, end: DateTime) -> int:
    #     # FIXME: 実装
    #     pass

    # @classmethod
    # def count_overlap_backward(cls, end: DateTime) -> int:
    #     CURRENT_DATETIME: Final[datetime] = datetime.now()
    #     # fmt: off
    #     query = [
    #         "SELECT",
    #             "COUNT(*)",
    #         "FROM (",
    #             "SELECT",
    #                 f"{cls.start.column},",
    #                 "CASE",
    #                     f"WHEN {cls.end.column} is NULL THEN $CURRENT_DATETIME",
    #                     f"ELSE {cls.end.column}",
    #                     "END",
    #                     f"AS replaced_end",
    #             f"FROM {cls._table_}",
    #             "WHERE",
    #                 f"$end > {cls.start.column}",
    #                 f"AND $end <= replaced_end"
    #         ")",
    #     ]
    #     # fmt: on

    #     return db.select(" ".join(query))[0]

