/**
 * Cliente de la API FastAPI (backend/app).
 * La URL se configura con VITE_API_URL (ver .env.example).
 */

const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/api/v1';

// ---------- Tipos (espejo de los schemas del backend) ----------

export interface StandPlano {
  id: string;
  codigo: string;
  tipo: string;
  estado: 'disponible' | 'bloqueado_temporal' | 'reservado' | 'vendido' | 'no_disponible';
  dimensiones: string | null;
  precio_base: number | null;
  zona_id: string;
  zona_nombre: string;
}

export interface PlanoResponse {
  zonas: { id: string; nombre: string; tipo: string; descripcion: string | null; capacidad: number | null }[];
  stands: StandPlano[];
}

export interface SolicitudReservaPayload {
  stand_id: string;
  empresa: {
    razon_social: string;
    nombre_comercial?: string | null;
    rubro?: string | null;
    ciudad?: string | null;
    pais?: string | null;
    origen?: string | null;
  };
  contacto: {
    nombre: string;
    cargo?: string | null;
    email?: string | null;
    whatsapp?: string | null;
    telefono?: string | null;
  };
  interes?: string | null;
}

export interface ReservaCreada {
  id: string;
  estado: string;
  fecha_expiracion: string | null;
}

// ---------- Funciones ----------

export async function fetchPlano(): Promise<PlanoResponse> {
  const res = await fetch(`${API_URL}/public/plano`);
  if (!res.ok) throw new Error(`Error al consultar el plano (${res.status})`);
  return res.json();
}

export async function solicitarReserva(
  payload: SolicitudReservaPayload,
): Promise<ReservaCreada> {
  const res = await fetch(`${API_URL}/reservas/solicitar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      const body = await res.json();
      if (typeof body.detail === 'string') detail = body.detail;
    } catch {
      // cuerpo no JSON
    }
    throw new Error(detail);
  }
  return res.json();
}

export default API_URL;
