import { useCallback, useEffect, useState } from 'react';
import { useAutoRefresh } from '../../../lib/useAutoRefresh';
import { api, fecha, getToken, ApiError } from '../../../lib/adminApi';
import type { Campana, Comunicacion, Empresa, ListResponse, Plantilla } from '../../../lib/adminApi';

const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/api/v1';

export default function Comunicaciones({ isAdmin = false }: { isAdmin?: boolean }) {
  // Historial
  const [items, setItems] = useState<Comunicacion[]>([]);
  const [total, setTotal] = useState(0);
  const [canal, setCanal] = useState('');
  const [estado, setEstado] = useState('');
  // Campañas
  const [campanas, setCampanas] = useState<Campana[]>([]);
  const [plantillas, setPlantillas] = useState<Plantilla[]>([]);
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [form, setForm] = useState({ nombre: '', segmento: '', plantilla_id: '', canal: 'email', limite_diario: 50 });
  const [propuesta, setPropuesta] = useState({ empresa_id: '', plantilla_id: '' });
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (canal) params.set('canal', canal);
      if (estado) params.set('estado', estado);
      const res = await api.get<ListResponse<Comunicacion>>(`/comunicaciones?${params}`);
      setItems(res.items);
      setTotal(res.total);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, [canal, estado]);

  useEffect(() => {
    load();
  }, [load]);
  useAutoRefresh(load); // refresco automático al cambiar datos

  useEffect(() => {
    api.get<Plantilla[]>('/plantillas').then(setPlantillas).catch(() => {});
    api.get<ListResponse<Empresa>>('/empresas?limit=200').then((r) => setEmpresas(r.items)).catch(() => {});
    api.get<{ items: Campana[] }>('/campanas').then((r) => setCampanas(r.items)).catch(() => {});
  }, []);

  const run = async (fn: () => Promise<unknown>, msg: string) => {
    try {
      const res = await fn();
      setInfo(typeof res === 'object' && res !== null ? `${msg} ${JSON.stringify(res)}` : msg);
      setError(null);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Error en la operación');
      setInfo(null);
    }
  };

  const handleCampana = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/campanas', {
        nombre: form.nombre,
        segmento: form.segmento || null,
        plantilla_id: form.plantilla_id,
        canal: form.canal,
        limite_diario: Number(form.limite_diario),
      });
      setInfo('✅ Campaña creada en estado borrador.');
      setForm({ nombre: '', segmento: '', plantilla_id: '', canal: 'email', limite_diario: 50 });
      api.get<{ items: Campana[] }>('/campanas').then((r) => setCampanas(r.items)).catch(() => {});
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo crear');
    }
  };

  const descargarPropuesta = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_URL}/propuestas/pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken() ?? ''}` },
        body: JSON.stringify({ empresa_id: propuesta.empresa_id, plantilla_id: propuesta.plantilla_id }),
      });
      if (!res.ok) throw new ApiError(res.status, 'No se pudo generar la propuesta');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'propuesta.pdf';
      a.click();
      URL.revokeObjectURL(url);
      setInfo('✅ Propuesta PDF descargada.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al generar PDF');
    }
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Comunicaciones</h2>
        <p>Historial, campañas y propuestas. Los envíos se despachan vía n8n (Gmail / WhatsApp).</p>
      </header>

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {info && <p className="admin-ok">{info}</p>}

      {/* ---- Campañas ---- */}
      <div className="admin-panel">
        <h3>Campañas</h3>
        {isAdmin && (
        <form className="admin-form-inline" onSubmit={handleCampana}>
          <input className="admin-input" required placeholder="Nombre de campaña *" value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          <input className="admin-input" placeholder="Segmento (estado o rubro:valor)" value={form.segmento}
            onChange={(e) => setForm({ ...form, segmento: e.target.value })} />
          <select className="admin-input" required value={form.plantilla_id}
            onChange={(e) => setForm({ ...form, plantilla_id: e.target.value })}>
            <option value="">Plantilla *</option>
            {plantillas.map((p) => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
          <select className="admin-input" value={form.canal} onChange={(e) => setForm({ ...form, canal: e.target.value })}>
            <option value="email">email</option>
            <option value="whatsapp">whatsapp</option>
          </select>
          <input className="admin-input" type="number" min={1} max={1000} style={{ minWidth: '110px' }}
            value={form.limite_diario} onChange={(e) => setForm({ ...form, limite_diario: Number(e.target.value) })} />
          <button type="submit" className="btn btn-primary">Crear campaña</button>
        </form>
        )}

        <div className="admin-table-wrap" style={{ marginTop: '1rem' }}><table className="admin-table">
          <thead>
            <tr><th>Campaña</th><th>Segmento</th><th>Canal</th><th>Estado</th><th>Límite/día</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {campanas.map((c) => (
              <tr key={c.id}>
                <td><strong>{c.nombre}</strong></td>
                <td>{c.segmento ?? 'todas'}</td>
                <td>{c.canal}</td>
                <td><span className="admin-pill">{c.estado}</span></td>
                <td>{c.limite_diario ?? '—'}</td>
                <td className="admin-actions">
                  {isAdmin && c.estado === 'borrador' && (
                    <button type="button" className="admin-btn-mini"
                      onClick={() => run(() => api.post(`/campanas/${c.id}/generar`), 'Generadas:')}>
                      Generar
                    </button>
                  )}
                  {isAdmin && (c.estado === 'aprobada' || c.estado === 'enviando') && (
                    <button type="button" className="admin-btn-mini success"
                      onClick={() => run(() => api.post(`/campanas/${c.id}/despachar`), 'Despachadas:')}>
                      Despachar
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {campanas.length === 0 && (
              <tr><td colSpan={6} className="admin-muted">Sin campañas.</td></tr>
            )}
          </tbody>
        </table></div>
      </div>

      {/* ---- Propuesta PDF ---- */}
      <div className="admin-panel">
        <h3>Generar propuesta PDF</h3>
        <form className="admin-form-inline" onSubmit={descargarPropuesta}>
          <select className="admin-input" required value={propuesta.empresa_id}
            onChange={(e) => setPropuesta({ ...propuesta, empresa_id: e.target.value })}>
            <option value="">Empresa *</option>
            {empresas.map((emp) => (
              <option key={emp.id} value={emp.id}>{emp.razon_social}</option>
            ))}
          </select>
          <select className="admin-input" required value={propuesta.plantilla_id}
            onChange={(e) => setPropuesta({ ...propuesta, plantilla_id: e.target.value })}>
            <option value="">Plantilla *</option>
            {plantillas.map((p) => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
          <button type="submit" className="btn btn-primary">Descargar PDF</button>
        </form>
      </div>

      {/* ---- Historial ---- */}
      <div className="admin-toolbar">
        <select className="admin-input" value={canal} onChange={(e) => setCanal(e.target.value)}>
          <option value="">Todos los canales</option>
          <option value="email">email</option>
          <option value="whatsapp">whatsapp</option>
          <option value="chat">chat</option>
        </select>
        <select className="admin-input" value={estado} onChange={(e) => setEstado(e.target.value)}>
          <option value="">Todos los estados</option>
          <option value="pendiente">pendiente</option>
          <option value="enviado">enviado</option>
          <option value="entregado">entregado</option>
          <option value="leido">leido</option>
          <option value="respondido">respondido</option>
          <option value="error">error</option>
        </select>
        <strong>{total} comunicación(es)</strong>
      </div>

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr><th>Fecha</th><th>Canal</th><th>Estado</th><th>Agente</th><th>Contenido</th></tr>
          </thead>
          <tbody>
            {items.map((c) => (
              <tr key={c.id}>
                <td>{fecha(c.created_at)}</td>
                <td>{c.canal}</td>
                <td><span className={`admin-pill estado-${c.estado}`}>{c.estado}</span></td>
                <td>{c.agente ?? '—'}</td>
                <td style={{ maxWidth: '380px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={c.contenido ?? ''}>
                  {c.contenido ?? '—'}
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={5} className="admin-muted">Sin comunicaciones.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
