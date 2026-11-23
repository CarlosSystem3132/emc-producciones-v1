import { useCallback, useEffect, useState } from 'react';
import { useAutoRefresh } from '../../../lib/useAutoRefresh';
import { api, fecha, ApiError } from '../../../lib/adminApi';
import type { Notificacion } from '../../../lib/adminApi';

/**
 * Notificaciones del panel (Fase 1 — notificaciones básicas + docs/08).
 * Avisos de reservas, leads, seguimientos y alertas; el usuario las marca
 * como leídas. Los canales externos (correo/WhatsApp) los despacha n8n.
 */
export default function Notificaciones() {
  const [items, setItems] = useState<Notificacion[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const res = await api.get<{ total: number; items: Notificacion[] }>('/notificaciones?limit=100');
      setItems(res.items);
      setTotal(res.total);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);
  useAutoRefresh(load); // refresco automático al cambiar datos

  const marcarLeida = async (n: Notificacion) => {
    try {
      await api.post(`/notificaciones/${n.id}/leer`);
      setInfo('Notificación marcada como leída.');
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Error al actualizar');
    }
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Notificaciones</h2>
        <p>{total} notificación(es). Reservas, leads, seguimientos y alertas del panel.</p>
      </header>

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {info && <p className="admin-ok">✅ {info}</p>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr><th>Fecha</th><th>Tipo</th><th>Título</th><th>Mensaje</th><th>Estado</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {items.map((n) => (
              <tr key={n.id}>
                <td>{fecha(n.created_at)}</td>
                <td><span className="admin-pill">{n.tipo}</span></td>
                <td><strong>{n.titulo}</strong></td>
                <td style={{ maxWidth: '340px' }}>{n.mensaje ?? '—'}</td>
                <td><span className={`admin-pill estado-${n.estado}`}>{n.estado}</span></td>
                <td>
                  {n.estado !== 'leido' && (
                    <button type="button" className="admin-btn-mini" onClick={() => marcarLeida(n)}>
                      Marcar leída
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={6} className="admin-muted">Sin notificaciones.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
