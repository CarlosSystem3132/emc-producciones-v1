"""Configuración central del backend (carga variables desde .env)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    app_name: str = "EMC Producciones API"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # Base de datos
    database_url: str = "postgresql+psycopg://emc_user:cambiar_esta_contraseña@localhost:5432/emc_producciones"

    # JWT
    jwt_secret: str = "cambiar_por_una_clave_larga_y_segura"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # n8n (webhook de automatizaciones: Gmail / WhatsApp)
    n8n_webhook_url: str = ""
    n8n_notif_webhook_url: str = ""        # ← NUEVO: notificaciones a ejecutivos
    webhook_secret: str = ""

    # CORS: orígenes permitidos separados por coma (frontend Astro)
    cors_origins: str = (
        "http://localhost:4321,https://www.expoinmobiliariayconstruccion.com"
    )

    # Router de IA gratuito con failover (services/ia_router.py)
    # Orden: gemini → groq → openrouter → deepseek → FAQ local
    ia_gemini_key: str = ""
    ia_gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    ia_gemini_model: str = "gemini-2.5-flash"
    ia_groq_key: str = ""
    ia_groq_base_url: str = "https://api.groq.com/openai/v1"
    ia_groq_model: str = "llama-3.3-70b-versatile"
    ia_openrouter_key: str = ""
    ia_openrouter_base_url: str = "https://openrouter.ai/api/v1"
    ia_openrouter_model: str = "meta-llama/llama-3.3-70b-instruct:free"

    # DeepSeek (opcional, al final de la cadena del router)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    # Usuario administrador inicial (seed)
    seed_admin_email: str = "admin@emcproducciones.com"
    seed_admin_password: str = "Admin123*"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
