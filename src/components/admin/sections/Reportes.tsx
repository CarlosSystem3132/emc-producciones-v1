import { useCallback, useEffect, useState } from 'react';
import { useAutoRefresh } from '../../../lib/useAutoRefresh';
import { api, money, getToken, ApiError } from '../../../lib/adminApi';
import type { Pronostico } from '../../../lib/adminApi';

const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/api/v1';

/**
 * Reportes comerciales avanzados y pronóstico de ocupación (Fase 4 — docs/10).
 * Exportación CSV de ventas, ocupación y embudo.
 */
export default function Reportes() {
  const [ventas, setVentas] = useState<{ nombre: string; ventas: number; monto_total: number }[]>([]);
  const [zonas, setZonas] = useState<Record<string, unknown>[]>([]);
  const [embudo, setEmbudo] = useState<Record<string, unknown>[]>([]);
  const [coms, setComs] = useState<{ total: number; por_canal: Record<string, Record<string, number>> } | null>(null);
  const [pronostico, setPronostico] = useState<Pronostico | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [v, z, e, c, p] = await Promise.all([
        api.get<{ nombre: string; ventas: number; monto_total: number }[]>('/reportes/ventas-por-ejecutivo'),
        api.get<Record<string, unknown>[]>('/reportes/ocupacion-por-zona'),
        api.get<Record<string, unknown>[]>('/reportes/embudo'),
        api.get<{ total: number; por_canal: Record<string, Record<string, number>> }>('/reportes/comunicaciones'),
        api.get<Pronostico>('/reportes/pronostico'),
      ]);
      setVentas(v);
      setZonas(z);
      setEmbudo(e);
      setComs(c);
      setPronostico(p);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar reportes');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);
  useAutoRefresh(load); // refresco automático al cambiar datos

  const exportar = async (tipo: 'ventas' | 'ocupacion' | 'embudo') => {
    try {
      const res = await fetch(`${API_URL}/reportes/export?tipo=${tipo}`, {
        headers: { Authorization: `Bearer ${getToken() ?? ''}` },
      });
      if (!res.ok) throw new ApiError(res.status, 'No se pudo exportar');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `reporte-${tipo}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al exportar');
    }
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Reportes</h2>
        <p>Ventas, ocupación, embudo, comunicaciones y pronóstico de ocupación.</p>
      </header>

      {error && <p className="reserva-error">⚠️ {error}</p>}

      {/* Pronóstico */}
      {pronostico && (
        <div className="admin-cards">
          <div className="admin-card accent">
            <span className="lbl">Ocupación actual</span>
            <span className="big">{pronostico.porcentaje_actual}%</span>
            <span className="sub">{pronostico.ocupados} de {pronostico.total_stands} stands</span>
          </div>
          <div className="admin-card">
            <span className="lbl">Velocidad de cierre</span>
            <span className="big">{pronostico.velocidad_semanal}/sem</span>
            <span className="sub">{pronostico.reservas_ultimos_30_dias} reservas en 30 días</span>
          </div>
          <div className="admin-card">
            <span className="lbl">Proyección abril 2027</span>
            <span className="big">{pronostico.porcentaje_proyectado_abril_2027}%</span>
            <span className="sub">
              {pronostico.fecha_estimada_100
                ? `100% estimado: ${pronostico.fecha_estimada_100}`
                : 'Sin velocidad suficiente para proyectar'}
            </span>
          </div>
        </div>
      )}

      {/* Ventas por ejecutivo */}
      <div className="admin-panel">
        <h3>Ventas por ejecutivo</h3>
        <div className="admin-toolbar">
          <button type="button" className="admin-btn-mini" onClick={() => exportar('ventas')}>⬇ Exportar CSV</button>
        </div>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr><th>Ejecutivo</th><th>Ventas</th><th>Monto total</th></tr>
            </thead>
            <tbody>
              {ventas.map((v, i) => (
                <tr key={i}>
                  <td><strong>{v.nombre}</strong></td>
                  <td>{v.ventas}</td>
                  <td>{money(v.monto_total)}</td>
                </tr>
              ))}
              {ventas.length === 0 && (
                <tr><td colSpan={3} className="admin-muted">Sin ventas registradas.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Ocupación por zona */}
      <div className="admin-panel" style={{ marginTop: '1.25rem' }}>
        <h3>Ocupación por zona</h3>
        <div className="admin-toolbar">
          <button type="button" className="admin-btn-mini" onClick={() => exportar('ocupacion')}>⬇ Exportar CSV</button>
        </div>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr><th>Zona</th><th>Tipo</th><th>Total</th><th>Disponibles</th><th>Reservados</th><th>Vendidos</th><th>Ocupación</th></tr>
            </thead>
            <tbody>
              {zonas.map((z, i) => (
                <tr key={i}>
                  <td><strong>{String(z.zona)}</strong></td>
                  <td>{String(z.tipo)}</td>
                  <td>{String(z.total)}</td>
                  <td>{String(z.disponibles)}</td>
                  <td>{String(z.reservados)}</td>
                  <td>{String(z.vendidos)}</td>
                  <td>{String(z.porcentaje_ocupacion)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Embudo */}
      <div className="admin-panel" style={{ marginTop: '1.25rem' }}>
        <h3>Embudo comercial</h3>
        <div className="admin-toolbar">
          <button type="button" className="admin-btn-mini" onClick={() => exportar('embudo')}>⬇ Exportar CSV</button>
        </div>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr><th>Estado</th><th>Leads</th><th>Conversión al siguiente</th></tr>
            </thead>
            <tbody>
              {embudo.map((e, i) => (
                <tr key={i}>
                  <td><strong>{String(e.estado)}</strong></td>
                  <td>{String(e.cantidad)}</td>
                  <td>{String(e.conversion_siguiente)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Comunicaciones */}
      {coms && (
        <div className="admin-panel" style={{ marginTop: '1.25rem' }}>
          <h3>Comunicaciones por canal ({coms.total} en total)</h3>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr><th>Canal</th><th>Estados</th></tr>
              </thead>
              <tbody>
                {Object.entries(coms.por_canal).map(([canal, estados]) => (
                  <tr key={canal}>
                    <td><strong>{canal}</strong></td>
                    <td>{Object.entries(estados).map(([estado, n]) => `${estado}: ${n}`).join(' · ')}</td>
                  </tr>
                ))}
                {Object.keys(coms.por_canal).length === 0 && (
                  <tr><td colSpan={2} className="admin-muted">Sin comunicaciones registradas.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
