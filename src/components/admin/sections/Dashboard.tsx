import { useCallback, useEffect, useState } from 'react';
import { api, money } from '../../../lib/adminApi';
import { useAutoRefresh } from '../../../lib/useAutoRefresh';
import type { DashboardData, Pronostico } from '../../../lib/adminApi';

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [alertasIA, setAlertasIA] = useState<{ tipo: string; mensaje: string }[]>([]);
  const [pronostico, setPronostico] = useState<Pronostico | null>(null);

  const cargar = useCallback(() => {
    api
      .get<DashboardData>('/dashboard')
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : 'Error'));
    // Alertas inteligentes y pronóstico de ocupación (Fase 3/4)
    api.get<{ tipo: string; mensaje: string }[]>('/alertas').then(setAlertasIA).catch(() => {});
    api.get<Pronostico>('/reportes/pronostico').then(setPronostico).catch(() => {});
  }, []);

  useEffect(() => {
    cargar();
  }, [cargar]);
  useAutoRefresh(cargar); // refresco automático al cambiar datos

  if (error) return <p className="reserva-error">⚠️ {error}</p>;
  if (!data) return <p className="admin-loading">Cargando métricas…</p>;

  const { stands, canchas, ventas, empresas_por_estado, embudo, desempeno_ejecutivos, avance_semanal, alertas } = data;

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Dashboard</h2>
        <p>Resumen general de la operación comercial.</p>
      </header>

      {[...alertas, ...alertasIA].length > 0 && (
        <div className="admin-alerts">
          {[...alertas, ...alertasIA].map((a, i) => (
            <div key={i} className={`admin-alert alert-${a.tipo}`}>
              🔔 {a.mensaje}
            </div>
          ))}
        </div>
      )}

      <div className="admin-cards">
        <div className="admin-card accent">
          <span className="lbl">Ocupación global</span>
          <span className="big">{stands.porcentaje_ocupacion}%</span>
          <span className="sub">{stands.reservados + stands.vendidos} de {stands.total} stands</span>
        </div>
        <div className="admin-card">
          <span className="lbl">Ventas totales</span>
          <span className="big">{money(ventas.totales)}</span>
          <span className="sub">Proyectadas: {money(ventas.proyectadas)}</span>
        </div>
        <div className="admin-card">
          <span className="lbl">Avance semanal</span>
          <span className="big">{avance_semanal.leads} leads</span>
          <span className="sub">{avance_semanal.empresas} empresas · {avance_semanal.reservas} reservas</span>
        </div>
        <div className="admin-card">
          <span className="lbl">Canchas de maquinaria</span>
          <span className="big">{canchas.vendidas} vendidas</span>
          <span className="sub">{canchas.disponibles} disponibles</span>
        </div>
        {pronostico && (
          <div className="admin-card accent">
            <span className="lbl">Pronóstico de ocupación</span>
            <span className="big">{pronostico.porcentaje_proyectado_abril_2027}%</span>
            <span className="sub">
              Proyección a abril 2027 · velocidad {pronostico.velocidad_semanal}/sem
            </span>
          </div>
        )}
      </div>

      <div className="admin-grid-2">
        <div className="admin-panel">
          <h3>Estado de stands</h3>
          <div className="admin-table-wrap"><table className="admin-table">
            <tbody>
              <tr><td>Disponibles</td><td>{stands.disponibles}</td></tr>
              <tr><td>Bloqueados temporalmente</td><td>{stands.bloqueados}</td></tr>
              <tr><td>Reservados</td><td>{stands.reservados}</td></tr>
              <tr><td>Vendidos</td><td>{stands.vendidos}</td></tr>
              <tr><td>No disponibles</td><td>{stands.no_disponibles}</td></tr>
            </tbody>
          </table></div>
        </div>

        <div className="admin-panel">
          <h3>Embudo comercial (leads)</h3>
          <div className="admin-table-wrap"><table className="admin-table">
            <tbody>
              {Object.entries(embudo).map(([estado, cantidad]) => (
                <tr key={estado}>
                  <td>{estado.replace(/_/g, ' ')}</td>
                  <td>{cantidad}</td>
                </tr>
              ))}
            </tbody>
          </table></div>
        </div>

        <div className="admin-panel">
          <h3>Empresas por estado</h3>
          <div className="admin-table-wrap"><table className="admin-table">
            <tbody>
              {Object.entries(empresas_por_estado).map(([estado, cantidad]) => (
                <tr key={estado}>
                  <td>{estado.replace(/_/g, ' ')}</td>
                  <td>{cantidad}</td>
                </tr>
              ))}
            </tbody>
          </table></div>
        </div>

        <div className="admin-panel">
          <h3>Desempeño por ejecutivo</h3>
          {desempeno_ejecutivos.length === 0 ? (
            <p className="admin-muted">Sin ejecutivos registrados.</p>
          ) : (
            <div className="admin-table-wrap"><table className="admin-table">
              <thead>
                <tr><th>Ejecutivo</th><th>Leads abiertos</th><th>Ventas</th></tr>
              </thead>
              <tbody>
                {desempeno_ejecutivos.map((ej) => (
                  <tr key={ej.ejecutivo_id}>
                    <td>{ej.nombre}</td>
                    <td>{ej.leads_abiertos}</td>
                    <td>{money(ej.ventas)}</td>
                  </tr>
                ))}
              </tbody>
            </table></div>
          )}
        </div>
      </div>
    </div>
  );
}
