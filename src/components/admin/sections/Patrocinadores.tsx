import { useCallback, useEffect, useState } from 'react';
import { api, ApiError } from '../../../lib/adminApi';
import type { Patrocinador } from '../../../lib/adminApi';

const CATEGORIAS = ['oro', 'plata', 'bronce', 'aliado'];

/**
 * Panel de patrocinadores (Fase 4 — docs/10).
 * Gestión de patrocinadores: alta, edición, orden y baja lógica.
 * Los activos se muestran en la web pública.
 */
export default function Patrocinadores() {
  const [items, setItems] = useState<Patrocinador[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ nombre: '', categoria: 'aliado', logo_url: '', sitio_web: '', orden: 0 });

  const load = useCallback(async () => {
    try {
      setItems(await api.get<Patrocinador[]>('/patrocinadores'));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const run = async (fn: () => Promise<unknown>, msg: string) => {
    try {
      await fn();
      setInfo(msg);
      setError(null);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Error en la operación');
      setInfo(null);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/patrocinadores', {
        nombre: form.nombre,
        categoria: form.categoria,
        logo_url: form.logo_url || null,
        sitio_web: form.sitio_web || null,
        orden: Number(form.orden) || 0,
      });
      setCreating(false);
      setInfo('✅ Patrocinador agregado.');
      setForm({ nombre: '', categoria: 'aliado', logo_url: '', sitio_web: '', orden: 0 });
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo crear');
      setInfo(null);
    }
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Patrocinadores</h2>
        <p>Aliados y patrocinadores de la expo. Los activos se publican en la web.</p>
      </header>

      <div className="admin-toolbar">
        <button type="button" className="btn btn-primary" onClick={() => setCreating((v) => !v)}>
          {creating ? 'Cancelar' : '+ Nuevo patrocinador'}
        </button>
      </div>

      {creating && (
        <form className="admin-form-grid" onSubmit={handleCreate}>
          <input className="admin-input" required placeholder="Nombre *" value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          <select className="admin-input" value={form.categoria}
            onChange={(e) => setForm({ ...form, categoria: e.target.value })}>
            {CATEGORIAS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <input className="admin-input" placeholder="URL del logo" value={form.logo_url}
            onChange={(e) => setForm({ ...form, logo_url: e.target.value })} />
          <input className="admin-input" placeholder="Sitio web" value={form.sitio_web}
            onChange={(e) => setForm({ ...form, sitio_web: e.target.value })} />
          <input className="admin-input" type="number" min={0} max={999} placeholder="Orden"
            value={form.orden} onChange={(e) => setForm({ ...form, orden: Number(e.target.value) })} />
          <button type="submit" className="btn btn-primary">Agregar</button>
        </form>
      )}

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {info && <p className="admin-ok">✅ {info}</p>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr><th>Orden</th><th>Nombre</th><th>Categoría</th><th>Web</th><th>Estado</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.id}>
                <td>{p.orden}</td>
                <td><strong>{p.nombre}</strong></td>
                <td><span className="admin-pill">{p.categoria ?? '—'}</span></td>
                <td>{p.sitio_web ? <a href={p.sitio_web} target="_blank" rel="noopener noreferrer">{p.sitio_web}</a> : '—'}</td>
                <td><span className="admin-pill">{p.estado}</span></td>
                <td className="admin-actions">
                  <button
                    type="button"
                    className={`admin-btn-mini ${p.estado === 'activo' ? 'danger' : 'success'}`}
                    onClick={() =>
                      run(
                        () => api.patch(`/patrocinadores/${p.id}`, { estado: p.estado === 'activo' ? 'inactivo' : 'activo' }),
                        'Estado actualizado.',
                      )
                    }
                  >
                    {p.estado === 'activo' ? 'Desactivar' : 'Activar'}
                  </button>
                  <button
                    type="button"
                    className="admin-btn-mini danger"
                    onClick={() => {
                      if (!confirm(`¿Eliminar a ${p.nombre}?`)) return;
                      run(() => api.delete(`/patrocinadores/${p.id}`), 'Patrocinador eliminado.');
                    }}
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={6} className="admin-muted">Sin patrocinadores registrados.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
