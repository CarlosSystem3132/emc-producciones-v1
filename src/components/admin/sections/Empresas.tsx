import { useCallback, useEffect, useRef, useState } from 'react';
import { api, fecha, ApiError, getToken } from '../../../lib/adminApi';
import type { Empresa, ListResponse, Usuario } from '../../../lib/adminApi';

const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/api/v1';

const ESTADOS = [
  'prospecto', 'contactado', 'interesado', 'propuesta_enviada',
  'en_negociacion', 'reserva_temporal', 'reservado', 'vendido', 'descartado',
];

export default function Empresas() {
  const [items, setItems] = useState<Empresa[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [estado, setEstado] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ razon_social: '', rubro: '', ciudad: '' });
  const [ejecutivos, setEjecutivos] = useState<Usuario[]>([]);
  const [importInfo, setImportInfo] = useState<string | null>(null);
  const [resumen, setResumen] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const load = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (search) params.set('search', search);
      if (estado) params.set('estado', estado);
      const res = await api.get<ListResponse<Empresa>>(`/empresas?${params}`);
      setItems(res.items);
      setTotal(res.total);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, [search, estado]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    api
      .get<ListResponse<Usuario>>('/users?rol=ejecutivo')
      .then((r) => setEjecutivos(r.items))
      .catch(() => {});
  }, []);

  const nombreEjecutivo = (id: string | null) =>
    id ? ejecutivos.find((e) => e.id === id)?.nombre_completo ?? '—' : 'Sin asignar';

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/empresas', { ...form, origen: 'panel' });
      setCreating(false);
      setForm({ razon_social: '', rubro: '', ciudad: '' });
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo crear');
    }
  };

  const cambiarEstado = async (empresa: Empresa, nuevo: string) => {
    try {
      await api.patch(`/empresas/${empresa.id}`, { estado: nuevo });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    }
  };

  const reasignar = async (empresa: Empresa, ejecutivo_id: string) => {
    try {
      await api.patch(`/empresas/${empresa.id}`, { ejecutivo_id: ejecutivo_id || null });
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImportInfo(null);
    setError(null);
    try {
      const body = new FormData();
      body.append('archivo', file);
      const res = await fetch(`${API_URL}/empresas/import`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken() ?? ''}` },
        body,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new ApiError(res.status, typeof err.detail === 'string' ? err.detail : 'Error al importar');
      }
      const data = await res.json();
      const errores = data.errores?.length ? ` · Errores: ${data.errores.join('; ')}` : '';
      setImportInfo(`✅ Importadas: ${data.creadas} · Duplicadas omitidas: ${data.duplicadas}${errores}`);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al importar');
    } finally {
      if (fileRef.current) fileRef.current.value = '';
    }
  };

  const handleExport = async () => {
    try {
      const res = await fetch(`${API_URL}/empresas/export`, {
        headers: { Authorization: `Bearer ${getToken() ?? ''}` },
      });
      if (!res.ok) throw new ApiError(res.status, 'No se pudo exportar');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'empresas.csv';
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al exportar');
    }
  };

  const eliminar = async (empresa: Empresa) => {
    if (!confirm(`¿Eliminar (soft delete) "${empresa.razon_social}"?`)) return;
    try {
      await api.delete(`/empresas/${empresa.id}`);
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    }
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Empresas</h2>
        <p>{total} empresa(s) registradas.</p>
      </header>

      <div className="admin-toolbar">
        <input
          className="admin-input"
          placeholder="Buscar por razón social, nombre o rubro…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select className="admin-input" value={estado} onChange={(e) => setEstado(e.target.value)}>
          <option value="">Todos los estados</option>
          {ESTADOS.map((s) => (
            <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
          ))}
        </select>
        <button type="button" className="btn btn-primary" onClick={() => setCreating((v) => !v)}>
          {creating ? 'Cancelar' : '+ Nueva empresa'}
        </button>
        <button type="button" className="btn" onClick={() => fileRef.current?.click()}>
          Importar CSV/Excel
        </button>
        <button type="button" className="btn" onClick={handleExport}>
          Exportar CSV
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".csv,.xlsx"
          style={{ display: 'none' }}
          onChange={handleImport}
        />
      </div>

      {importInfo && <p className="admin-ok">{importInfo}</p>}

      {creating && (
        <form className="admin-form-inline" onSubmit={handleCreate}>
          <input
            className="admin-input"
            required
            placeholder="Razón social *"
            value={form.razon_social}
            onChange={(e) => setForm({ ...form, razon_social: e.target.value })}
          />
          <input
            className="admin-input"
            placeholder="Rubro"
            value={form.rubro}
            onChange={(e) => setForm({ ...form, rubro: e.target.value })}
          />
          <input
            className="admin-input"
            placeholder="Ciudad"
            value={form.ciudad}
            onChange={(e) => setForm({ ...form, ciudad: e.target.value })}
          />
          <button type="submit" className="btn btn-primary">Crear</button>
        </form>
      )}

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {resumen && (
        <div className="admin-panel" style={{ whiteSpace: 'pre-wrap', fontSize: '0.88rem' }}>
          🤖 {resumen}
        </div>
      )}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Razón social</th>
              <th>Rubro</th>
              <th>Ciudad</th>
              <th>Estado</th>
              <th>Ejecutivo</th>
              <th>Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((emp) => (
              <tr key={emp.id}>
                <td><strong>{emp.razon_social}</strong></td>
                <td>{emp.rubro ?? '—'}</td>
                <td>{emp.ciudad ?? '—'}</td>
                <td>
                  <select
                    className="admin-select-mini"
                    value={emp.estado}
                    onChange={(e) => cambiarEstado(emp, e.target.value)}
                  >
                    {ESTADOS.map((s) => (
                      <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
                    ))}
                  </select>
                </td>
                <td>
                  <select
                    className="admin-select-mini"
                    value={emp.ejecutivo_id ?? ''}
                    onChange={(e) => reasignar(emp, e.target.value)}
                  >
                    <option value="">Sin asignar</option>
                    {ejecutivos.map((ej) => (
                      <option key={ej.id} value={ej.id}>{ej.nombre_completo}</option>
                    ))}
                  </select>
                </td>
                <td>{fecha(emp.created_at)}</td>
                <td>
                  <button
                    type="button"
                    className="admin-btn-mini"
                    onClick={() => {
                      api
                        .post<{ resumen: string; comunicaciones: number; actividades: number }>(
                          `/empresas/${emp.id}/resumen`,
                        )
                        .then((r) => setResumen(`${emp.razon_social}: ${r.resumen}`))
                        .catch((err) => setError(err instanceof ApiError ? err.message : 'Error al resumir'));
                    }}
                  >
                    Resumen IA
                  </button>{' '}
                  <button type="button" className="admin-btn-mini danger" onClick={() => eliminar(emp)}>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={7} className="admin-muted">Sin resultados.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
