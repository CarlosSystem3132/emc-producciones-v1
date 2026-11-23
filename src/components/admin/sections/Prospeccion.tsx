import { useCallback, useEffect, useState } from 'react';
import { api } from '../../../lib/adminApi';
import { useAutoRefresh } from '../../../lib/useAutoRefresh';

interface DatosProspeccion {
  rubros_con_menor_cobertura: { rubro: string; empresas: number }[];
  zonas_con_mayor_disponibilidad: { zona_id: string; stands_disponibles: number }[];
  empresas_reactivar: { id: string; razon_social: string; rubro: string | null }[];
  borrador_mensaje: string;
  origen_borrador: string;
}

interface DatosEstrategia {
  inventario: { total_stands: number; ocupados: number; porcentaje_ocupacion: number; zonas_casi_agotadas: { zona: string }[] };
  avance_semanal: { leads: number; empresas: number; reservas: number };
  desempeno_ejecutivos: { ejecutivo: string; leads_abiertos: number; ventas: number; estado: string }[];
  plan_semanal_sugerido: string[];
  segmentos_prioritarios: { segmento: string; empresas: number; prioridad: string }[];
  campanas_sugeridas: { nombre: string; segmento: string; plantilla_sugerida: string }[];
  autonomia: string;
}

/**
 * Prospección asistida + Agente de Estrategia (Fase 3 — docs/09).
 * Analiza la cartera: rubros con menor cobertura, zonas con disponibilidad,
 * empresas dormidas para reactivar y borrador de mensaje de prospección.
 * Todo es una sugerencia supervisada: el ejecutivo decide.
 */
export default function Prospeccion() {
  const [datos, setDatos] = useState<DatosProspeccion | null>(null);
  const [estrategia, setEstrategia] = useState<DatosEstrategia | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copiado, setCopiado] = useState(false);

  const load = useCallback(async () => {
    try {
      const [p, e] = await Promise.all([
        api.get<DatosProspeccion>('/prospeccion'),
        api.get<DatosEstrategia>('/ia/estrategia'),
      ]);
      setDatos(p);
      setEstrategia(e);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);
  useAutoRefresh(load); // refresco automático al cambiar datos

  const copiar = async () => {
    if (!datos) return;
    try {
      await navigator.clipboard.writeText(datos.borrador_mensaje);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2000);
    } catch {
      setCopiado(false);
    }
  };

  if (error) return <p className="reserva-error">⚠️ {error}</p>;
  if (!datos) return <p className="admin-loading">Analizando cartera…</p>;

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Prospección asistida</h2>
        <p>Dónde enfocar el esfuerzo comercial según el análisis de la cartera. Sugerencias supervisadas.</p>
      </header>

      {/* Agente de Estrategia (docs/09) */}
      {estrategia && (
        <div className="admin-panel">
          <h3>🧠 Agente de Estrategia — plan semanal sugerido</h3>
          <p className="admin-muted">{estrategia.autonomia}</p>
          <ul style={{ margin: '0.5rem 0', paddingLeft: '1.2rem' }}>
            {estrategia.plan_semanal_sugerido.map((p, i) => (
              <li key={i} style={{ marginBottom: '0.35rem' }}>{p}</li>
            ))}
            {estrategia.plan_semanal_sugerido.length === 0 && (
              <li>Sin acciones urgentes sugeridas para esta semana.</li>
            )}
          </ul>
          <p className="admin-muted">
            Avance semanal: {estrategia.avance_semanal.leads} leads · {estrategia.avance_semanal.empresas} empresas ·{' '}
            {estrategia.avance_semanal.reservas} reservas · ocupación {estrategia.inventario.porcentaje_ocupacion}%
          </p>
          {estrategia.campanas_sugeridas.length > 0 && (
            <p className="admin-muted">
              Campañas sugeridas: {estrategia.campanas_sugeridas.map((c) => c.nombre).join(' · ')}
            </p>
          )}
        </div>
      )}

      <div className="admin-cards">
        <div className="admin-card accent">
          <span className="lbl">Rubros con menor cobertura</span>
          <span className="big">{datos.rubros_con_menor_cobertura.length}</span>
          <span className="sub">oportunidades de segmento</span>
        </div>
        <div className="admin-card">
          <span className="lbl">Empresas para reactivar</span>
          <span className="big">{datos.empresas_reactivar.length}</span>
          <span className="sub">sin actividad reciente</span>
        </div>
        <div className="admin-card">
          <span className="lbl">Zonas con disponibilidad</span>
          <span className="big">{datos.zonas_con_mayor_disponibilidad.length}</span>
          <span className="sub">para ofrecer primero</span>
        </div>
      </div>

      <div className="admin-panel">
        <h3>Rubros con menor cobertura</h3>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead><tr><th>Rubro</th><th>Empresas registradas</th></tr></thead>
            <tbody>
              {datos.rubros_con_menor_cobertura.map((r, i) => (
                <tr key={i}>
                  <td><strong>{r.rubro}</strong></td>
                  <td>{r.empresas}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="admin-panel" style={{ marginTop: '1.25rem' }}>
        <h3>Empresas para reactivar (sin actividad reciente)</h3>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead><tr><th>Empresa</th><th>Rubro</th></tr></thead>
            <tbody>
              {datos.empresas_reactivar.map((e) => (
                <tr key={e.id}>
                  <td><strong>{e.razon_social}</strong></td>
                  <td>{e.rubro ?? '—'}</td>
                </tr>
              ))}
              {datos.empresas_reactivar.length === 0 && (
                <tr><td colSpan={2} className="admin-muted">Sin empresas dormidas. ¡Buen trabajo!</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="admin-panel" style={{ marginTop: '1.25rem' }}>
        <h3>Borrador de mensaje de prospección</h3>
        <p className="admin-muted">Revísalo y edítalo antes de usarlo. La IA no envía nada sin tu autorización.</p>
        <pre style={{ whiteSpace: 'pre-wrap', background: '#1c1f26', padding: '1rem', borderRadius: '10px', fontSize: '0.86rem' }}>
          {datos.borrador_mensaje}
        </pre>
        <button type="button" className="btn btn-primary" onClick={copiar}>
          {copiado ? '✅ Copiado' : 'Copiar mensaje'}
        </button>
      </div>
    </div>
  );
}
