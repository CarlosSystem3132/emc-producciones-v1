"""Tests de flujos completos de la API (cada módulo del sistema).

Corre con:  PYTHONPATH=... pytest backend/tests -q
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4 as _uuid4

from app.db.session import SessionLocal
from app.models.reserva import Reserva

API = "/api/v1"


# ---------------------------------------------------------------------------
# Salud y autenticación
# ---------------------------------------------------------------------------

def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_login_admin(client, admin_headers):
    r = client.get(f"{API}/auth/me", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["rol"] == "admin"


def test_login_invalido(client):
    r = client.post(f"{API}/auth/login", json={"email": "admin@test.com", "password": "mala"})
    assert r.status_code in (400, 401)


def test_sin_token_rechaza(client):
    assert client.get(f"{API}/users").status_code == 401


# ---------------------------------------------------------------------------
# Usuarios / ejecutivos
# ---------------------------------------------------------------------------

def test_ejecutivo_solo_ve_su_perfil(client, admin_headers, ejecutivo_headers):
    # El ejecutivo no puede listar usuarios (solo admin, docs/07)
    assert client.get(f"{API}/users", headers=ejecutivo_headers).status_code == 403
    # Pero sí verse a sí mismo
    r = client.get(f"{API}/users/{ejecutivo_headers['_id']}", headers=ejecutivo_headers)
    assert r.status_code == 200
    # No puede cambiar su propio rol/estado
    r = client.patch(
        f"{API}/users/{ejecutivo_headers['_id']}",
        headers=ejecutivo_headers,
        json={"rol": "admin", "cargo": "Nuevo cargo"},
    )
    assert r.status_code == 200
    assert r.json()["rol"] == "ejecutivo"  # rol ignorado
    assert r.json()["cargo"] == "Nuevo cargo"


def test_change_password(client):
    r = client.post(f"{API}/auth/login", json={"email": "ejecutivo@test.com", "password": "Ejecutivo123*"})
    token = {"Authorization": f"Bearer {r.json()['access_token']}"}
    # Contraseña actual incorrecta → 400
    r = client.post(f"{API}/users/me/change-password", headers=token,
                    json={"current_password": "equivocada", "new_password": "Nueva123*"})
    assert r.status_code == 400
    # Cambio correcto → 204 y login con la nueva
    r = client.post(f"{API}/users/me/change-password", headers=token,
                    json={"current_password": "Ejecutivo123*", "new_password": "Nueva123*"})
    assert r.status_code == 204
    r = client.post(f"{API}/auth/login", json={"email": "ejecutivo@test.com", "password": "Nueva123*"})
    assert r.status_code == 200
    # restaurar
    token = {"Authorization": f"Bearer {r.json()['access_token']}"}
    client.post(f"{API}/users/me/change-password", headers=token,
                json={"current_password": "Nueva123*", "new_password": "Ejecutivo123*"})


# ---------------------------------------------------------------------------
# Empresas y contactos
# ---------------------------------------------------------------------------

def test_empresas_crud_y_duplicados(client, ejecutivo_headers):
    payload = {"razon_social": "Empresa Prueba SRL", "rubro": "construcción", "ciudad": "La Paz"}
    r = client.post(f"{API}/empresas", headers=ejecutivo_headers, json=payload)
    assert r.status_code == 201, r.text
    empresa_id = r.json()["id"]
    # duplicado por razón social → 409
    r = client.post(f"{API}/empresas", headers=ejecutivo_headers, json=payload)
    assert r.status_code == 409
    # contacto
    r = client.post(f"{API}/empresas/{empresa_id}/contactos", headers=ejecutivo_headers,
                    json={"nombre": "Contacto Uno", "email": "c1@empresa.bo", "whatsapp": "+591 70000002"})
    assert r.status_code == 201, r.text
    # resumen IA (modo local)
    r = client.post(f"{API}/empresas/{empresa_id}/resumen", headers=ejecutivo_headers)
    assert r.status_code == 200
    assert r.json()["origen"] in ("ia", "local")
    # export CSV
    r = client.get(f"{API}/empresas/export", headers=ejecutivo_headers)
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Leads + IA comercial (Agente 2)
# ---------------------------------------------------------------------------

def test_leads_clasificar_sugerir_asignar(client, admin_headers, ejecutivo_headers):
    # empresa propia del test (aislamiento)
    empresa_id = client.post(
        f"{API}/empresas", headers=ejecutivo_headers,
        json={"razon_social": f"Empresa Leads {_uuid4().hex[:6]}", "rubro": "estructuras"},
    ).json()["id"]
    r = client.post(f"{API}/leads", headers=ejecutivo_headers,
                    json={"empresa_id": empresa_id, "interes": "stand premium", "prioridad": "media"})
    assert r.status_code in (200, 201), r.text
    lead_id = r.json()["id"]

    assert client.get(f"{API}/leads/embudo", headers=ejecutivo_headers).status_code == 200

    # clasificar en modo asistido (por defecto): no aplica sin confirmación
    r = client.post(f"{API}/leads/{lead_id}/clasificar", headers=ejecutivo_headers)
    assert r.status_code == 200
    assert r.json()["aplicado"] is False
    # aplicar con confirmación humana
    r = client.post(f"{API}/leads/{lead_id}/clasificar?aplicar=true", headers=ejecutivo_headers)
    assert r.json()["aplicado"] is True

    # sugerencias de siguiente acción
    r = client.get(f"{API}/leads/{lead_id}/sugerencias", headers=ejecutivo_headers)
    assert r.status_code == 200 and len(r.json()) >= 1

    # asignación sugerida (admin aplica)
    r = client.get(f"{API}/leads/{lead_id}/asignacion-sugerida", headers=admin_headers)
    assert r.status_code == 200 and r.json()["nombre"]
    r = client.post(f"{API}/leads/{lead_id}/asignar-sugerido", headers=admin_headers)
    assert r.status_code == 200 and r.json()["ok"] is True
    # el ejecutivo no puede reasignar
    assert client.post(f"{API}/leads/{lead_id}/asignar-sugerido", headers=ejecutivo_headers).status_code == 403


def test_config_agentes_modos(client, admin_headers, ejecutivo_headers):
    r = client.get(f"{API}/config/agentes", headers=admin_headers)
    assert r.status_code == 200
    claves = {a["clave"] for a in r.json()}
    assert {"estrategia", "prospeccion", "contenido", "difusion", "atencion"} <= claves
    # el ejecutivo no configura agentes
    assert client.get(f"{API}/config/agentes", headers=ejecutivo_headers).status_code == 403

    # modo manual: clasificar no aplica nunca
    client.patch(f"{API}/config/agentes/prospeccion", headers=admin_headers,
                 json={"modo_autonomia": "manual"})
    empresa_id = client.post(
        f"{API}/empresas", headers=ejecutivo_headers,
        json={"razon_social": f"Empresa Modos {_uuid4().hex[:6]}"},
    ).json()["id"]
    lead = client.post(f"{API}/leads", headers=ejecutivo_headers,
                       json={"empresa_id": empresa_id, "interes": "cancha"}).json()
    r = client.post(f"{API}/leads/{lead['id']}/clasificar?aplicar=true", headers=ejecutivo_headers)
    assert r.json()["aplicado"] is False and "manual" in r.json().get("nota", "").lower()
    assert client.post(f"{API}/leads/{lead['id']}/asignar-sugerido", headers=admin_headers).status_code == 409

    # modo automático: aplica sin confirmación
    client.patch(f"{API}/config/agentes/prospeccion", headers=admin_headers,
                 json={"modo_autonomia": "automatico", "prompt_sistema": "Prompt de prueba para el agente de prospección."})
    r = client.post(f"{API}/leads/{lead['id']}/clasificar", headers=ejecutivo_headers)
    assert r.json()["aplicado"] is True
    # modo inválido → 400
    assert client.patch(f"{API}/config/agentes/prospeccion", headers=admin_headers,
                        json={"modo_autonomia": "loco"}).status_code == 400
    # restaurar
    client.patch(f"{API}/config/agentes/prospeccion", headers=admin_headers, json={"modo_autonomia": "asistido"})


# ---------------------------------------------------------------------------
# Público: plano, registro, chat (Agente 5)
# ---------------------------------------------------------------------------

def test_plano_publico(client, zona_stands):
    _, _, _, codigos = zona_stands
    r = client.get(f"{API}/public/plano")
    assert r.status_code == 200
    codigos_plano = {s["codigo"] for s in r.json()["stands"]}
    assert set(codigos) <= codigos_plano


def test_registro_publico(client):
    r = client.post(f"{API}/public/registro", json={
        "razon_social": "Empresa Web SRL", "nombre_contacto": "Visitante Web",
        "email": "web@empresa.bo", "tipo_solicitud": "brochure",
        "fuente": "meta/cpc/stands2027",
    })
    assert r.status_code == 201, r.text


def test_chat_faq_sin_ia(client):
    r = client.post(f"{API}/public/chat", json={"mensaje": "¿Cuándo es la expo?"})
    assert r.status_code == 200
    assert r.json()["origen"] in ("faq", "ia")
    assert r.json()["respuesta"]
    # rate limit: 10/min por IP
    for _ in range(12):
        r = client.post(f"{API}/public/chat", json={"mensaje": "hola"})
    assert r.status_code == 429


# ---------------------------------------------------------------------------
# Reservas: bloqueo → extensión → venta → liberación (docs/06)
# ---------------------------------------------------------------------------

def test_flujo_reserva_completo(client, admin_headers, ejecutivo_headers, zona_stands):
    _, stand1, stand2, (cod1, cod2) = zona_stands

    # 1) Solicitud pública → bloqueo temporal 30 min
    r = client.post(f"{API}/reservas/solicitar", json={
        "stand_id": stand1,
        "empresa": {"razon_social": "Cliente Reserva SRL", "rubro": "maquinaria"},
        "contacto": {"nombre": "Cliente Uno", "whatsapp": "+591 70000003", "email": "cliente@reserva.bo"},
        "interes": "stand premium",
    })
    assert r.status_code == 201, r.text
    reserva = r.json()
    assert reserva["estado"] == "bloqueado" and reserva["fecha_expiracion"]
    assert reserva["ejecutivo_id"]  # asignación automática

    # el stand quedó bloqueado
    plano = client.get(f"{API}/public/plano").json()["stands"]
    assert next(s for s in plano if s["codigo"] == cod1)["estado"] == "bloqueado_temporal"

    # 2) Extensión (una vez)
    r = client.post(f"{API}/reservas/{reserva['id']}/extender",
                    headers=ejecutivo_headers,
                    json={"minutos": 30, "motivo": "negociación activa"})
    assert r.status_code == 200
    assert client.post(f"{API}/reservas/{reserva['id']}/extender",
                       headers=ejecutivo_headers,
                       json={"minutos": 30, "motivo": "otra vez"}).status_code == 409

    # 3) Confirmar → reservado
    r = client.post(f"{API}/reservas/{reserva['id']}/confirmar", headers=ejecutivo_headers)
    assert r.json()["estado"] == "reservado"

    # 4) Vender → vendido + stand vendido
    r = client.post(f"{API}/reservas/{reserva['id']}/vender",
                    headers=ejecutivo_headers,
                    json={"monto": 2500})
    assert r.json()["estado"] == "vendido"
    plano = client.get(f"{API}/public/plano").json()["stands"]
    assert next(s for s in plano if s["codigo"] == cod1)["estado"] == "vendido"

    # 5) Notificación al ejecutivo registrada
    r = client.get(f"{API}/notificaciones", headers=ejecutivo_headers)
    assert r.status_code == 200 and r.json()["total"] >= 1


def test_reserva_cancelar_y_liberar_expiradas(client, ejecutivo_headers, zona_stands):
    _, _, stand2, (cod1, cod2) = zona_stands
    r = client.post(f"{API}/reservas/solicitar", json={
        "stand_id": stand2,
        "empresa": {"razon_social": "Cliente Dos SRL"},
        "contacto": {"nombre": "Cliente Dos"},
    })
    reserva = r.json()

    # forzar expiración directamente en BD
    db = SessionLocal()
    fila = db.get(Reserva, __import__("uuid").UUID(reserva["id"]))
    fila.fecha_expiracion = datetime.now(timezone.utc) - timedelta(minutes=5)
    db.commit()
    db.close()

    # ejecutivo sin secreto → 403 (la automatización usa X-Webhook-Secret)
    r = client.post(f"{API}/reservas/liberar-expiradas", headers=ejecutivo_headers)
    assert r.status_code == 403
    # automatización (n8n) con secreto → libera
    r = client.post(f"{API}/reservas/liberar-expiradas",
                    headers={"X-Webhook-Secret": "webhook-de-pruebas-123"})
    assert r.status_code == 200
    plano = client.get(f"{API}/public/plano").json()["stands"]
    assert next(s for s in plano if s["codigo"] == cod2)["estado"] == "disponible"

    # por-expirar accesible para la automatización con secreto
    r = client.get(f"{API}/reservas/por-expirar",
                   headers={"X-Webhook-Secret": "webhook-de-pruebas-123"})
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Pagos, firma digital y facturación (Fase 4)
# ---------------------------------------------------------------------------

def test_pagos_firma_factura(client, admin_headers, ejecutivo_headers, zona_stands):
    _, stand1, _, (cod1, cod2) = zona_stands
    r = client.post(f"{API}/reservas/solicitar", json={
        "stand_id": stand1,
        "empresa": {"razon_social": "Cliente Pagos SRL"},
        "contacto": {"nombre": "Pagador", "email": "pagos@cliente.bo"},
    })
    reserva = r.json()
    client.post(f"{API}/reservas/{reserva['id']}/confirmar", headers=ejecutivo_headers)

    # pago pendiente → confirmado; anulado solo admin
    r = client.post(f"{API}/reservas/{reserva['id']}/pagos", headers=ejecutivo_headers,
                    json={"monto": 500, "metodo": "transferencia", "referencia": "TRF-1"})
    assert r.status_code == 201, r.text
    pago_id = r.json()["id"]
    assert client.post(f"{API}/pagos/{pago_id}/confirmar", headers=ejecutivo_headers).json()["estado"] == "confirmado"
    assert client.post(f"{API}/pagos/{pago_id}/anular", headers=ejecutivo_headers).status_code == 403
    assert client.post(f"{API}/pagos/{pago_id}/anular", headers=admin_headers).json()["estado"] == "anulado"

    # firma digital: solicitud → firma pública con token
    r = client.post(f"{API}/reservas/{reserva['id']}/firmas", headers=ejecutivo_headers,
                    json={"firmante_nombre": "Firmante Prueba", "firmante_email": "firma@cliente.bo"})
    assert r.status_code == 201, r.text
    token = r.json()["token"]
    r = client.get(f"{API}/public/firmas/{token}")
    assert r.status_code == 200 and r.json()["estado"] == "pendiente"
    r = client.post(f"{API}/public/firmas/{token}", json={"firmante_nombre": "Firmante Prueba", "acepta": True})
    assert r.json()["estado"] == "firmada"
    # doble firma → 409
    r = client.post(f"{API}/public/firmas/{token}", json={"firmante_nombre": "Otra Persona", "acepta": True})
    assert r.status_code == 409
    # nombre demasiado corto → 422 (validación)
    r2 = client.post(f"{API}/public/firmas/{_uuid4().hex}", json={"firmante_nombre": "X", "acepta": True})
    assert r2.status_code in (404, 422)

    # facturación (la reserva no tiene monto de venta → se indica explícito)
    r = client.post(f"{API}/facturas", headers=admin_headers,
                    json={"reserva_id": reserva["id"], "nit": "1234567001",
                          "razon_social": "Cliente Pagos SRL", "monto": 3800})
    assert r.status_code == 201, r.text
    factura_id = r.json()["id"]
    assert client.post(f"{API}/facturas/{factura_id}/emitir", headers=admin_headers).json()["estado"] == "emitida"
    assert client.post(f"{API}/facturas/{factura_id}/anular", headers=admin_headers).json()["estado"] == "anulada"
    assert client.get(f"{API}/facturas", headers=admin_headers).status_code == 200


# ---------------------------------------------------------------------------
# Plantillas y contenido (Agente 3)
# ---------------------------------------------------------------------------

def test_plantillas_render_enviar_pdf(client, admin_headers, ejecutivo_headers):
    r = client.post(f"{API}/plantillas", headers=admin_headers,
                    json={"nombre": "Invitación Test", "tipo": "invitacion", "canal": "email",
                          "contenido": "Hola {{contacto}} de {{empresa}}, los esperamos."})
    assert r.status_code == 201, r.text
    plantilla_id = r.json()["id"]

    # render con variables
    r = client.post(f"{API}/plantillas/{plantilla_id}/render", headers=ejecutivo_headers,
                    json={"variables": {"contacto": "Juan", "empresa": "ACME"}})
    assert r.status_code == 200
    assert "Juan" in r.json()["contenido"] and r.json()["variables_faltantes"] == []

    # enviar (sin n8n configurado → queda registrada)
    empresa_id = client.post(
        f"{API}/empresas", headers=ejecutivo_headers,
        json={"razon_social": f"Empresa Plant {_uuid4().hex[:6]}"},
    ).json()["id"]
    r = client.post(f"{API}/plantillas/{plantilla_id}/enviar", headers=ejecutivo_headers,
                    json={"empresa_id": empresa_id})
    assert r.status_code == 200, r.text

    # extraer texto de PDF (reportlab genera un PDF mínimo)
    from io import BytesIO
    from reportlab.pdfgen import canvas
    buf = BytesIO()
    c = canvas.Canvas(buf)
    c.drawString(100, 750, "Texto de prueba del PDF")
    c.save()
    r = client.post(f"{API}/plantillas/extraer-pdf", headers=admin_headers,
                    files={"archivo": ("plantilla.pdf", buf.getvalue(), "application/pdf")})
    assert r.status_code == 200, r.text
    assert "Texto de prueba" in r.json()["texto"]


# ---------------------------------------------------------------------------
# Campañas y secuencias (Agente 4)
# ---------------------------------------------------------------------------

def test_campanas_generar_despachar(client, admin_headers):
    plantillas = client.get(f"{API}/plantillas", headers=admin_headers).json()
    r = client.post(f"{API}/campanas", headers=admin_headers,
                    json={"nombre": "Campaña Test", "plantilla_id": plantillas[0]["id"],
                          "canal": "email", "limite_diario": 10})
    assert r.status_code == 201, r.text
    campana_id = r.json()["id"]
    r = client.post(f"{API}/campanas/{campana_id}/generar", headers=admin_headers)
    assert r.status_code == 200, r.text
    r = client.post(f"{API}/campanas/{campana_id}/despachar", headers=admin_headers)
    assert r.status_code == 200, r.text
    # sin n8n configurado las comunicaciones quedan registradas (pendientes/enviadas)
    assert client.get(f"{API}/comunicaciones", headers=admin_headers).status_code == 200


def test_secuencias_flujo(client, admin_headers, ejecutivo_headers):
    plantillas = client.get(f"{API}/plantillas", headers=admin_headers).json()
    r = client.post(f"{API}/secuencias", headers=admin_headers,
                    json={"nombre": "Secuencia Test", "canal": "email",
                          "pasos": [{"orden": 1, "dias_espera": 0, "plantilla_id": plantillas[0]["id"]},
                                    {"orden": 2, "dias_espera": 7, "mensaje": "Seguimiento"}]})
    assert r.status_code == 201, r.text
    secuencia_id = r.json()["id"]

    empresa_id = client.post(
        f"{API}/empresas", headers=ejecutivo_headers,
        json={"razon_social": f"Empresa Sec {_uuid4().hex[:6]}"},
    ).json()["id"]
    r = client.post(f"{API}/secuencias/{secuencia_id}/inscribir", headers=ejecutivo_headers,
                    json={"empresa_id": empresa_id})
    assert r.status_code == 201, r.text

    r = client.post(f"{API}/secuencias/ejecutar-pendientes", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["enviados"] + r.json()["omitidos"] >= 1

    r = client.get(f"{API}/secuencias/inscripciones/listado", headers=admin_headers)
    assert r.status_code == 200 and len(r.json()) >= 1


# ---------------------------------------------------------------------------
# Reportes, patrocinadores, notificaciones, webhooks e IA
# ---------------------------------------------------------------------------

def test_reportes_y_export(client, admin_headers):
    for ruta in ("/reportes/ventas-por-ejecutivo", "/reportes/ocupacion-por-zona",
                 "/reportes/embudo", "/reportes/comunicaciones", "/reportes/pronostico"):
        assert client.get(f"{API}{ruta}", headers=admin_headers).status_code == 200, ruta
    r = client.get(f"{API}/reportes/export?tipo=ventas", headers=admin_headers)
    assert r.status_code == 200 and "text/csv" in r.headers["content-type"]
    assert client.get(f"{API}/reportes/export?tipo=invalido", headers=admin_headers).status_code == 422


def test_patrocinadores(client, admin_headers, ejecutivo_headers):
    r = client.post(f"{API}/patrocinadores", headers=admin_headers,
                    json={"nombre": "Patrocinador Test", "categoria": "oro", "sitio_web": "https://patro.bo"})
    assert r.status_code == 201, r.text
    pid = r.json()["id"]
    assert client.patch(f"{API}/patrocinadores/{pid}", headers=admin_headers,
                        json={"estado": "inactivo"}).status_code == 200
    r = client.get(f"{API}/public/patrocinadores")
    assert all(p["nombre"] != "Patrocinador Test" for p in r.json())  # inactivo no sale
    assert client.delete(f"{API}/patrocinadores/{pid}", headers=admin_headers).status_code == 204


def test_webhook_estado_comunicacion(client, admin_headers):
    # secreto incorrecto → 401
    r = client.post(f"{API}/webhooks/estado-comunicacion",
                    headers={"X-Webhook-Secret": "malo"},
                    json={"comunicacion_id": "00000000-0000-0000-0000-000000000000", "estado": "enviado"})
    assert r.status_code == 401
    # secreto correcto + id inexistente → 404
    r = client.post(f"{API}/webhooks/estado-comunicacion",
                    headers={"X-Webhook-Secret": "webhook-de-pruebas-123"},
                    json={"comunicacion_id": "00000000-0000-0000-0000-000000000000", "estado": "enviado"})
    assert r.status_code == 404


def test_ia_estado_y_estrategia(client, admin_headers, ejecutivo_headers):
    r = client.get(f"{API}/ia/estado", headers=admin_headers)
    assert r.status_code == 200  # sin keys: cadena vacía, pero responde
    r = client.get(f"{API}/ia/estrategia", headers=ejecutivo_headers)
    assert r.status_code == 200
    assert "plan_semanal_sugerido" in r.json()
    r = client.get(f"{API}/prospeccion", headers=ejecutivo_headers)
    assert r.status_code == 200
    assert client.get(f"{API}/alertas", headers=ejecutivo_headers).status_code == 200
