from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'DMS Email Monitor'
    debug: bool = False
    secret_key: str = 'changeme'
    allowed_origins: list[str] = Field(default_factory=lambda: ['http://localhost:5173', 'http://localhost:3000'])
    database_url: str = 'sqlite+aiosqlite:///./dms_email.db'
    redis_url: str = 'redis://localhost:6379/0'
    azure_openai_endpoint: str = 'https://gaebtesting1.openai.azure.com'
    azure_openai_api_key: str = 'changeme'
    azure_openai_deployment: str = 'gpt-5.4-mini-ravi'
    azure_openai_api_version: str = '2024-08-01-preview'
    slr_white_minutes: int = 4
    slr_yellow_minutes: int = 8
    email_poll_interval_seconds: int = 30
    max_emails_per_poll: int = 50
    uploads_path: Path = Path('uploads/attachments')
    import_allowed_roots: list[Path] = Field(default_factory=lambda: [Path.cwd(), Path('/tmp')])
    jwt_expire_minutes: int = 60
    refresh_expire_minutes: int = 60 * 24
    import_batch_size: int = 500

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_origins(cls, value: Any) -> Any:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [item.strip() for item in value.split(',') if item.strip()]
        return value

    @field_validator('import_allowed_roots', mode='before')
    @classmethod
    def parse_import_roots(cls, value: Any) -> Any:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = [item.strip() for item in value.split(',') if item.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_path.mkdir(parents=True, exist_ok=True)
    settings.import_allowed_roots = [Path(path).expanduser().resolve() for path in settings.import_allowed_roots]
    return settings
