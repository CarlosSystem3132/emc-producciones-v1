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
    webhook_secret: str = ""

    # Usuario administrador inicial (seed)
    seed_admin_email: str = "admin@emcproducciones.com"
    seed_admin_password: str = "Admin123*"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
