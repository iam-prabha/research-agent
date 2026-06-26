from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    nvidia_api_key: str
    tavily_api_key: str
    database_url: str
    redis_url: str = "redis://localhost:6379"
    cors_origins: str = "http://localhost:5173"

    plan_model: str = "meta/llama-3.1-8b-instruct"
    extract_model: str = "meta/llama-3.1-8b-instruct"
    synthesize_model: str = "meta/llama-3.1-70b-instruct"
    verify_model: str = "meta/llama-3.1-70b-instruct"

    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    max_search_rounds: int = 3

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
