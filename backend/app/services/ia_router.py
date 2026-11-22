"""Router de IA con failover entre proveedores gratuitos (2026).

Cadena de proveedores (en orden de intento):

1. Google Gemini  — cuota diaria generosa, sin tarjeta.
2. Groq           — rápido (Llama), sin tarjeta.
3. OpenRouter     — modelos gratuitos (`:free`).
4. DeepSeek       — opcional (solo si hay API key).

Cuando un proveedor devuelve 429 / cuota agotada, se marca como «agotado»
temporalmente y el router pasa al siguiente. Si todos fallan, los servicios
devuelven None y el sistema cae a la FAQ local (nunca se rompe el chat).

Todos los proveedores usan la interfaz compatible con OpenAI
(`/chat/completions`), por lo que basta con cambiar base_url + key + modelo.

Los contadores viven en memoria: sirven para una instancia (Render free,
Railway, VPS). No contienen datos sensibles.
"""
import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from app.core.config import settings

# Minutos que un proveedor queda fuera de servicio tras agotar su cuota
MINUTOS_BLOQUEO_429 = 60
MINUTOS_BLOQUEO_CONFIG = 720  # errores de auth/config: 12 h (evita spam)


@dataclass
class Proveedor:
    nombre: str
    base_url: str
    api_key: str
    modelo: str
    agotado_hasta: float = 0.0  # epoch seconds
    exitos: int = 0
    limites_alcanzados: int = 0
    errores: int = 0
    ultimo_error: str | None = None

    def disponible(self) -> bool:
        return bool(self.api_key) and time.time() >= self.agotado_hasta

    def estado(self) -> dict:
        ahora = time.time()
        if not self.api_key:
            situacion = "sin_api_key"
        elif self.agotado_hasta > ahora:
            situacion = "agotado"
        else:
            situacion = "disponible"
        return {
            "proveedor": self.nombre,
            "modelo": self.modelo,
            "situacion": situacion,
            "exitos": self.exitos,
            "limites_alcanzados": self.limites_alcanzados,
            "ultimo_error": self.ultimo_error,
        }


@dataclass
class _Cadena:
    """Cadena de proveedores con estado compartido entre llamadas."""
    proveedores: list[Proveedor] = field(default_factory=list)


_cadena = _Cadena()


def _cargar_proveedores() -> list[Proveedor]:
    if _cadena.proveedores:
        return _cadena.proveedores

    candidatos = [
        ("gemini", settings.ia_gemini_base_url, settings.ia_gemini_key, settings.ia_gemini_model),
        ("groq", settings.ia_groq_base_url, settings.ia_groq_key, settings.ia_groq_model),
        ("openrouter", settings.ia_openrouter_base_url, settings.ia_openrouter_key, settings.ia_openrouter_model),
        ("deepseek", settings.deepseek_base_url, settings.deepseek_api_key, settings.deepseek_model),
    ]
    _cadena.proveedores = [
        Proveedor(nombre=n, base_url=b.rstrip("/"), api_key=k, modelo=m)
        for n, b, k, m in candidatos
        if k  # solo proveedores con API key configurada
    ]
    return _cadena.proveedores


def generar(
    mensajes: list[dict],
    *,
    max_tokens: int = 500,
    temperature: float = 0.3,
) -> tuple[str, str] | None:
    """Genera texto con el primer proveedor disponible.

    Devuelve (texto, nombre_proveedor) o None si todos fallan/agotados."""
    proveedores = _cargar_proveedores()

    for proveedor in proveedores:
        if not proveedor.disponible():
            continue

        payload = {
            "model": proveedor.modelo,
            "messages": mensajes,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        try:
            req = urllib.request.Request(
                f"{proveedor.base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {proveedor.api_key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            contenido = data["choices"][0]["message"]["content"]
            texto = str(contenido).strip()
            if texto:
                proveedor.exitos += 1
                return texto, proveedor.nombre
            proveedor.errores += 1
            proveedor.ultimo_error = "respuesta vacía"
        except urllib.error.HTTPError as exc:
            detalle = ""
            try:
                detalle = exc.read().decode("utf-8")[:200]
            except Exception:
                pass
            if exc.code == 429:
                # Cuota agotada: se marca y se prueba el siguiente proveedor
                proveedor.limites_alcanzados += 1
                proveedor.ultimo_error = "429 cuota/rate limit"
                proveedor.agotado_hasta = time.time() + MINUTOS_BLOQUEO_429 * 60
            elif exc.code in (401, 403):
                # API key inválida: bloquear largo rato y registrar
                proveedor.errores += 1
                proveedor.ultimo_error = f"{exc.code} auth inválida"
                proveedor.agotado_hasta = time.time() + MINUTOS_BLOQUEO_CONFIG * 60
            else:
                proveedor.errores += 1
                proveedor.ultimo_error = f"{exc.code} {detalle}"
        except (urllib.error.URLError, OSError, KeyError, IndexError, ValueError) as exc:
            proveedor.errores += 1
            proveedor.ultimo_error = str(exc)[:200]

    return None


def estado() -> list[dict]:
    """Estado de la cadena de proveedores (para diagnóstico)."""
    return [p.estado() for p in _cargar_proveedores()]
