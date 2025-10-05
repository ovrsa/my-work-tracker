from typing import Any, Dict

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    # NOTE: https://docs.ponyorm.org/api_reference.html?highlight=create_db#supported-databases
    provider: str = "sqlite"
    filename: str = "/Users/kyo/development/Projects/my-work-tracker/sqlite.db"
    create_db: bool = True
    create_tables: bool = True

    def dict_bind(self) -> Dict[str, Any]:
        return self.model_dump(include={"provider", "filename", "create_db"})
