from pydantic import BaseSettings, Field


class Config(BaseSettings):
    # Database
    db_user: str = Field(None, env="DB_USER")
    db_pass: str = Field(None, env="DB_PASS")
    db_host: str = Field(None, env="DB_HOST")
    db_port: int = Field(5432, env="DB_PORT")
    db_database: str = Field(None, env="DB_DATABASE")

    # Logging
    logging_level: str = Field("INFO", env="LOGGING_LEVEL")
    logging_show_timestamps: bool = Field(False, env="LOGGING_SHOW_TIMESTAMPS")
    logging_enable_colour: bool = Field(False, env="LOGGING_ENABLE_COLOUR")
    logging_show_splash: bool = Field(False, env="LOGGING_SHOW_SPLASH")

    development_mode: bool = Field(False, env="DEVELOPMENT_MODE")


config = Config()
