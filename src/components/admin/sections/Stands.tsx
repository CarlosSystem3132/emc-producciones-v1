import { useCallback, useEffect, useState } from 'react';
import { api, money, ApiError } from '../../../lib/adminApi';
import type { ListResponse, Stand, Zona } from '../../../lib/adminApi';

const ESTADOS: Stand['estado'][] = ['disponible', 'bloqueado_temporal', 'reservado', 'vendido', 'no_disponible'];

export default function Stands() {
  const [items, setItems] = useState<Stand[]>([]);
  const [zonas, setZonas] = useState<Zona[]>([]);
  const [zonaId, setZonaId] = useState('');
  const [estado, setEstado] = useState('');
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (zonaId) params.set('zona_id', zonaId);
      if (estado) params.set('estado', estado);
      const res = await api.get<ListResponse<Stand>>(`/inventario/stands?${params}`);
      setItems(res.items);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, [zonaId, estado]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    api
      .get<Zona[]>('/inventario/zonas')
      .then(setZonas)
      .catch(() => {});
  }, []);

  const cambiarEstado = async (stand: Stand, nuevo: Stand['estado']) => {
    try {
      await api.patch(`/inventario/stands/${stand.id}`, { estado: nuevo });
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Error');
    }
  };

  const nombreZona = (id: string) => zonas.find((z) => z.id === id)?.nombre ?? '—';

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Stands</h2>
        <p>Inventario del pabellón, precios y disponibilidad.</p>
      </header>

      <div className="admin-toolbar">
        <select className="admin-input" value={zonaId} onChange={(e) => setZonaId(e.target.value)}>
          <option value="">Todas las zonas</option>
          {zonas.map((z) => (
            <option key={z.id} value={z.id}>{z.nombre}</option>
          ))}
        </select>
        <select className="admin-input" value={estado} onChange={(e) => setEstado(e.target.value)}>
          <option value="">Todos los estados</option>
          {ESTADOS.map((s) => (
            <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
          ))}
        </select>
      </div>

      {error && <p className="reserva-error">⚠️ {error}</p>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Código</th>
              <th>Zona</th>
              <th>Tipo</th>
              <th>Dimensiones</th>
              <th>Precio base</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {items.map((stand) => (
              <tr key={stand.id}>
                <td><strong>{stand.codigo}</strong></td>
                <td>{nombreZona(stand.zona_id)}</td>
                <td>{stand.tipo.replace(/_/g, ' ')}</td>
                <td>{stand.dimensiones ?? '—'}</td>
                <td>{money(stand.precio_base)}</td>
                <td>
                  <select
                    className={`admin-select-mini estado-${stand.estado}`}
                    value={stand.estado}
                    onChange={(e) => cambiarEstado(stand, e.target.value as Stand['estado'])}
                  >
                    {ESTADOS.map((s) => (
                      <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={6} className="admin-muted">Sin stands con estos filtros.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
