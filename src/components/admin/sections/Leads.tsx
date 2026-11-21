import { useCallback, useEffect, useState } from 'react';
import { api, fecha, ApiError } from '../../../lib/adminApi';
import type { Empresa, Lead, ListResponse } from '../../../lib/adminApi';

const ESTADOS = [
  'prospecto', 'contactado', 'interesado', 'propuesta_enviada',
  'en_negociacion', 'reserva_temporal', 'reservado', 'vendido', 'descartado',
];
const PRIORIDADES = ['alta', 'media', 'baja'];

export default function Leads() {
  const [items, setItems] = useState<Lead[]>([]);
  const [embudo, setEmbudo] = useState<Record<string, number>>({});
  const [estado, setEstado] = useState('');
  const [prioridad, setPrioridad] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [form, setForm] = useState({ empresa_id: '', prioridad: 'media', interes: '' });

  const load = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (estado) params.set('estado', estado);
      if (prioridad) params.set('prioridad', prioridad);
      const [res, emb] = await Promise.all([
        api.get<ListResponse<Lead>>(`/leads?${params}`),
        api.get<Record<string, number>>('/leads/embudo'),
      ]);
      setItems(res.items);
      setEmbudo(emb);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, [estado, prioridad]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    api
      .get<ListResponse<Empresa>>('/empresas?limit=200')
      .then((r) => setEmpresas(r.items))
      .catch(() => {});
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/leads', {
        empresa_id: form.empresa_id,
        prioridad: form.prioridad,
        interes: form.interes || null,
        origen: 'panel',
      });
      setCreating(false);
      setForm({ empresa_id: '', prioridad: 'media', interes: '' });
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo crear');
    }
  };

  const cambiarEstado = async (lead: Lead, nuevo: string) => {
    try {
      await api.patch(`/leads/${lead.id}`, { estado: nuevo });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    }
  };

  const nombreEmpresa = (id: string) => empresas.find((e) => e.id === id)?.razon_social ?? id.slice(0, 8);

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Leads</h2>
        <p>Embudo comercial y seguimiento de oportunidades.</p>
      </header>

      <div className="admin-funnel">
        {ESTADOS.map((s) => (
          <button
            key={s}
            type="button"
            className={`admin-funnel-step ${estado === s ? 'active' : ''}`}
            onClick={() => setEstado(estado === s ? '' : s)}
          >
            <span className="n">{embudo[s] ?? 0}</span>
            <span className="l">{s.replace(/_/g, ' ')}</span>
          </button>
        ))}
      </div>

      <div className="admin-toolbar">
        <select className="admin-input" value={prioridad} onChange={(e) => setPrioridad(e.target.value)}>
          <option value="">Toda prioridad</option>
          {PRIORIDADES.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
        <button type="button" className="btn btn-primary" onClick={() => setCreating((v) => !v)}>
          {creating ? 'Cancelar' : '+ Nuevo lead'}
        </button>
      </div>

      {creating && (
        <form className="admin-form-inline" onSubmit={handleCreate}>
          <select
            className="admin-input"
            required
            value={form.empresa_id}
            onChange={(e) => setForm({ ...form, empresa_id: e.target.value })}
          >
            <option value="">Selecciona empresa *</option>
            {empresas.map((emp) => (
              <option key={emp.id} value={emp.id}>{emp.razon_social}</option>
            ))}
          </select>
          <select
            className="admin-input"
            value={form.prioridad}
            onChange={(e) => setForm({ ...form, prioridad: e.target.value })}
          >
            {PRIORIDADES.map((p) => (
              <option key={p} value={p}>Prioridad {p}</option>
            ))}
          </select>
          <input
            className="admin-input"
            placeholder="Interés (stand, paquete…)"
            value={form.interes}
            onChange={(e) => setForm({ ...form, interes: e.target.value })}
          />
          <button type="submit" className="btn btn-primary">Crear</button>
        </form>
      )}

      {error && <p className="reserva-error">⚠️ {error}</p>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Empresa</th>
              <th>Interés</th>
              <th>Prioridad</th>
              <th>Estado</th>
              <th>Próxima acción</th>
              <th>Registro</th>
            </tr>
          </thead>
          <tbody>
            {items.map((lead) => (
              <tr key={lead.id}>
                <td><strong>{nombreEmpresa(lead.empresa_id)}</strong></td>
                <td>{lead.interes ?? '—'}</td>
                <td>
                  <span className={`admin-pill prio-${lead.prioridad}`}>{lead.prioridad}</span>
                </td>
                <td>
                  <select
                    className="admin-select-mini"
                    value={lead.estado}
                    onChange={(e) => cambiarEstado(lead, e.target.value)}
                  >
                    {ESTADOS.map((s) => (
                      <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
                    ))}
                  </select>
                </td>
                <td>{lead.proxima_accion ?? '—'}</td>
                <td>{fecha(lead.created_at)}</td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={6} className="admin-muted">Sin leads con estos filtros.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
