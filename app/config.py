from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings, case_sensitive=False):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_path: str
    jwt_expire_minutes: int
    jwt_secret: str
    jwt_algo:str


settings = Settings()
