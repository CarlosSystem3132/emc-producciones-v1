"""Configuración de pruebas: API completa contra SQLite local."""
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

DB_PATH = Path("/home/work/.openclaw/workspace/.openclaw/tmp/test_emc.db")
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"
os.environ["JWT_SECRET"] = "secreto-de-pruebas-123"
os.environ["WEBHOOK_SECRET"] = "webhook-de-pruebas-123"
os.environ["SEED_ADMIN_EMAIL"] = "admin@test.com"
os.environ["SEED_ADMIN_PASSWORD"] = "Admin123*"
if DB_PATH.exists():
    DB_PATH.unlink()

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.base import Base, engine  # noqa: E402
from app.main import app  # noqa: E402

API = "/api/v1"


@pytest.fixture(scope="session")
def client():
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="session")
def admin_headers(client):
    r = client.post(f"{API}/auth/login", json={"email": "admin@test.com", "password": "Admin123*"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="session")
def ejecutivo_headers(client, admin_headers):
    """Crea un ejecutivo de prueba y devuelve sus headers + su id."""
    r = client.post(
        f"{API}/users",
        headers=admin_headers,
        json={
            "nombre_completo": "Ejecutivo Prueba",
            "email": "ejecutivo@test.com",
            "password": "Ejecutivo123*",
            "rol": "ejecutivo",
            "whatsapp": "+591 70000001",
            "cargo": "Ejecutivo",
        },
    )
    assert r.status_code == 201, r.text
    ejecutivo_id = r.json()["id"]
    r = client.post(f"{API}/auth/login", json={"email": "ejecutivo@test.com", "password": "Ejecutivo123*"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}", "_id": ejecutivo_id}


@pytest.fixture()
def zona_stands(client, admin_headers):
    """Crea una zona con dos stands NUEVOS por test (aislamiento) y devuelve
    (zona_id, stand1_id, stand2_id)."""
    import uuid as _uuid
    sufijo = _uuid.uuid4().hex[:6]
    r = client.post(
        f"{API}/inventario/zonas",
        headers=admin_headers,
        json={"nombre": f"Zona {sufijo}", "tipo": "interior", "capacidad": 2},
    )
    assert r.status_code == 201, r.text
    zona_id = r.json()["id"]
    ids = []
    for codigo in (f"T-{sufijo}-1", f"T-{sufijo}-2"):
        r = client.post(
            f"{API}/inventario/stands",
            headers=admin_headers,
            json={"codigo": codigo, "zona_id": zona_id, "tipo": "stand", "precio_base": 1000},
        )
        assert r.status_code == 201, r.text
        ids.append(r.json()["id"])
    return zona_id, ids[0], ids[1], (f"T-{sufijo}-1", f"T-{sufijo}-2")
