from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    DB_URL: str
    SECRET_KEY_JWT: str
    ALGORITHM: str
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    REDIS_DOMAIN: str
    REDIS_PORT: int
    REDIS_PASSWORD: str | None
    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    @field_validator('ALGORITHM')
    @classmethod
    def validate_algorithm(cls, v):
        if v not in ['HS256']:
            raise ValueError('algorithm must be HS256')
        return v

    model_config = ConfigDict(extra='ignore', env_file='.env', env_file_encoding='utf-8') # noqa

config = Config()