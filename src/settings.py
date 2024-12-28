from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    dataset_url: str

    class Config:
        env_file = ".env"


settings = Settings()
