from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER:     str
    DB_PASSWORD: str
    DB_NAME:     str
    DB_HOST:     str
    DB_PORT:     str

    OLLAMA_HOST:  str
    OLLAMA_MODEL: str

    EMBEDDING_MODEL: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()