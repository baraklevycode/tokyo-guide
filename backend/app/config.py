"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings for the Tokyo Guide backend application."""

    # Groq API (free at console.groq.com)
    groq_api_key: str = ""

    # Supabase (free at supabase.com)
    supabase_url: str = ""
    supabase_key: str = ""

    # Frontend URL for CORS
    frontend_url: str = "http://localhost:3000"

    # Embedding model name
    embedding_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # Groq model name (llama-3.3-70b: free, 128K context, great Hebrew support)
    groq_model_name: str = "llama-3.3-70b-versatile"

    # RAG settings
    rag_match_threshold: float = 0.25
    rag_match_count: int = 8
    rag_max_completion_tokens: int = 4096
    rag_temperature: float = 0.7
    rag_top_p: float = 0.9

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
