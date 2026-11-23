/**
 * Cliente de la API para el panel de administración (con JWT).
 */

const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/api/v1';

const TOKEN_KEY = 'emc_admin_token';

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (typeof window === 'undefined') return;
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (res.status === 401) {
    setToken(null);
    throw new ApiError(401, 'Sesión expirada, vuelve a iniciar sesión');
  }
  if (!res.ok) {
    let detail = `Error ${res.status}`;
    try {
      const body = await res.json();
      if (typeof body.detail === 'string') detail = body.detail;
    } catch {
      // cuerpo no JSON
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  put: <T>(path: string) => request<T>(path, { method: 'PUT' }),
  delete: (path: string) => request<void>(path, { method: 'DELETE' }),
};

// ---------- Auth ----------

export async function login(email: string, password: string): Promise<void> {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    let detail = 'Correo o contraseña incorrectos';
    try {
      const body = await res.json();
      if (typeof body.detail === 'string') detail = body.detail;
    } catch {
      // cuerpo no JSON
    }
    throw new ApiError(res.status, detail);
  }
  const data = await res.json();
  setToken(data.access_token);
}

// ---------- Tipos ----------

export interface Usuario {
  id: string;
  nombre_completo: string;
  email: string;
  telefono: string | null;
  whatsapp: string | null;
  correo_contacto: string | null;
  cargo: string | null;
  experiencia: string | null;
  especialidad: string | null;
  foto_url: string | null;
  rol: 'admin' | 'ejecutivo' | 'presidencia';
  estado: 'activo' | 'bloqueado' | 'inactivo';
  created_at: string;
}

/** Cambio de contraseña del propio usuario (docs/08). */
export async function changeMyPassword(currentPassword: string, newPassword: string): Promise<void> {
  await request<void>('/users/me/change-password', {
    method: 'POST',
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  });
}

export interface Empresa {
  id: string;
  razon_social: string;
  nombre_comercial: string | null;
  rubro: string | null;
  ciudad: string | null;
  estado: string;
  origen: string | null;
  ejecutivo_id: string | null;
  created_at: string;
}

export interface Lead {
  id: string;
  empresa_id: string;
  estado: string;
  prioridad: string;
  rubro: string | null;
  interes: string | null;
  proxima_accion: string | null;
  ejecutivo_id: string | null;
  created_at: string;
}

export interface Stand {
  id: string;
  codigo: string;
  zona_id: string;
  tipo: string;
  dimensiones: string | null;
  precio_base: number | null;
  estado: 'disponible' | 'bloqueado_temporal' | 'reservado' | 'vendido' | 'no_disponible';
  reserva_activa_id: string | null;
}

export interface Zona {
  id: string;
  nombre: string;
  tipo: string;
  capacidad: number | null;
}

export interface Reserva {
  id: string;
  empresa_id: string;
  lead_id: string | null;
  stand_id: string;
  ejecutivo_id: string | null;
  estado: 'bloqueado' | 'reservado' | 'vendido' | 'expirado' | 'cancelado';
  fecha_inicio: string | null;
  fecha_expiracion: string | null;
  fecha_extension: string | null;
  motivo_extension: string | null;
  monto: number | null;
  contrato_url: string | null;
  created_at: string;
}

export interface DashboardData {
  stands: {
    total: number;
    disponibles: number;
    bloqueados: number;
    reservados: number;
    vendidos: number;
    no_disponibles: number;
    porcentaje_ocupacion: number;
  };
  canchas: { disponibles: number; vendidas: number };
  ventas: { totales: number; proyectadas: number };
  empresas_por_estado: Record<string, number>;
  embudo: Record<string, number>;
  desempeno_ejecutivos: { ejecutivo_id: string; nombre: string; leads_abiertos: number; ventas: number }[];
  avance_semanal: { empresas: number; leads: number; reservas: number };
  alertas: { tipo: string; mensaje: string }[];
}

export interface ListResponse<T> {
  total: number;
  items: T[];
}

export interface Plantilla {
  id: string;
  nombre: string;
  tipo: string;
  canal: 'email' | 'whatsapp' | 'chat' | 'pdf';
  contenido: string;
  estado: 'activo' | 'inactivo';
  created_at: string;
}

export interface Comunicacion {
  id: string;
  empresa_id: string | null;
  contacto_id: string | null;
  canal: string;
  plantilla_id: string | null;
  contenido: string | null;
  estado: 'pendiente' | 'enviado' | 'entregado' | 'leido' | 'respondido' | 'error';
  agente: string | null;
  created_at: string;
}

export interface Campana {
  id: string;
  nombre: string;
  segmento: string | null;
  plantilla_id: string | null;
  canal: string;
  estado: 'borrador' | 'aprobada' | 'enviando' | 'finalizada';
  limite_diario: number | null;
  created_at?: string;
}

export const money = (n: number | null | undefined): string =>
  n == null ? '—' : `$us ${Number(n).toLocaleString('es-BO')}`;

// ---------- Tipos Fase 3/4 ----------

export interface Notificacion {
  id: string;
  tipo: string;
  titulo: string;
  mensaje: string | null;
  canal: string;
  estado: 'pendiente' | 'enviado' | 'leido';
  created_at: string;
}

export interface Secuencia {
  id: string;
  nombre: string;
  descripcion: string | null;
  canal: string;
  estado: string;
  pasos: number;
  inscripciones_activas: number;
  created_at: string;
}

export interface Inscripcion {
  id: string;
  secuencia_id: string;
  empresa: string;
  paso_actual: number;
  proxima_ejecucion: string;
  estado: string;
}

export interface Pago {
  id: string;
  reserva_id: string;
  monto: number;
  metodo: string;
  referencia: string | null;
  estado: string;
  created_at: string;
}

export interface Patrocinador {
  id: string;
  nombre: string;
  categoria: string | null;
  logo_url: string | null;
  sitio_web: string | null;
  estado: string;
  orden: number;
}

export interface Pronostico {
  total_stands: number;
  ocupados: number;
  porcentaje_actual: number;
  reservas_ultimos_30_dias: number;
  velocidad_semanal: number;
  semanas_para_100: number | null;
  fecha_estimada_100: string | null;
  porcentaje_proyectado_abril_2027: number;
}

export const fecha = (iso: string | null | undefined): string =>
  iso ? new Date(iso).toLocaleString('es-BO', { dateStyle: 'short', timeStyle: 'short' }) : '—';

