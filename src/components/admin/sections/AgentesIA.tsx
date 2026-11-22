import { useCallback, useEffect, useState } from 'react';
import { api, ApiError } from '../../../lib/adminApi';

interface AgenteIA {
  clave: string;
  nombre: string;
  descripcion: string | null;
  prompt_sistema: string;
  modo_autonomia: 'automatico' | 'asistido' | 'manual';
  activo: boolean;
}

const MODOS: { valor: AgenteIA['modo_autonomia']; etiqueta: string; detalle: string }[] = [
  { valor: 'automatico', etiqueta: 'Automático', detalle: 'Ejecuta sus acciones sin pedir confirmación.' },
  { valor: 'asistido', etiqueta: 'Asistido', detalle: 'Propone y espera tu confirmación (recomendado).' },
  { valor: 'manual', etiqueta: 'Manual', detalle: 'Solo actúa cuando un humano lo solicita.' },
];

/**
 * Configuración de los agentes de IA (docs/09 y docs/14).
 * El administrador edita el prompt del sistema y el modo de autonomía de
 * cada agente. Los cambios se aplican de inmediato en todo el sistema.
 */
export default function AgentesIA() {
  const [items, setItems] = useState<AgenteIA[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [editando, setEditando] = useState<Record<string, AgenteIA>>({});

  const load = useCallback(async () => {
    try {
      const lista = await api.get<AgenteIA[]>('/config/agentes');
      setItems(lista);
      setEditando(Object.fromEntries(lista.map((a) => [a.clave, { ...a }])));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const guardar = async (clave: string) => {
    const cambios = editando[clave];
    if (!cambios) return;
    try {
      await api.patch(`/config/agentes/${clave}`, {
        prompt_sistema: cambios.prompt_sistema,
        modo_autonomia: cambios.modo_autonomia,
        activo: cambios.activo,
      });
      setInfo(`✅ Configuración del «${cambios.nombre}» guardada. Se aplica de inmediato.`);
      setError(null);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo guardar');
      setInfo(null);
    }
  };

  const set = (clave: string, campo: keyof AgenteIA, valor: string | boolean) => {
    setEditando((prev) => ({
      ...prev,
      [clave]: { ...prev[clave], [campo]: valor } as AgenteIA,
    }));
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Agentes de IA</h2>
        <p>
          Configura cómo trabaja cada agente: edita su prompt del sistema y decide si actúa
          automáticamente, asistido por humanos o solo bajo petición manual.
        </p>
      </header>

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {info && <p className="admin-ok">{info}</p>}

      {items.map((agente) => {
        const borrador = editando[agente.clave] ?? agente;
        return (
          <div className="admin-panel" key={agente.clave}>
            <h3>{agente.nombre}</h3>
            {agente.descripcion && <p className="admin-muted">{agente.descripcion}</p>}

            <label className="reserva-field" style={{ marginBottom: '0.75rem' }}>
              Modo de autonomía
              <select
                className="admin-input"
                value={borrador.modo_autonomia}
                onChange={(e) => set(agente.clave, 'modo_autonomia', e.target.value)}
              >
                {MODOS.map((m) => (
                  <option key={m.valor} value={m.valor}>
                    {m.etiqueta} — {m.detalle}
                  </option>
                ))}
              </select>
            </label>

            <label className="reserva-field" style={{ marginBottom: '0.75rem' }}>
              Prompt del sistema (instrucciones que sigue el agente)
              <textarea
                className="admin-input"
                style={{ width: '100%', minHeight: '140px', lineHeight: 1.5 }}
                value={borrador.prompt_sistema}
                onChange={(e) => set(agente.clave, 'prompt_sistema', e.target.value)}
                placeholder="Describe las reglas y el rol del agente…"
              />
            </label>

            <div className="admin-toolbar">
              <label className="reserva-field" style={{ flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}>
                <input
                  type="checkbox"
                  checked={borrador.activo}
                  onChange={(e) => set(agente.clave, 'activo', e.target.checked)}
                  style={{ width: '18px', height: '18px' }}
                />
                Agente activo
              </label>
              <button type="button" className="btn btn-primary" onClick={() => guardar(agente.clave)}>
                💾 Guardar cambios
              </button>
            </div>
          </div>
        );
      })}

      {items.length === 0 && !error && (
        <p className="admin-loading">Cargando agentes…</p>
      )}
    </div>
  );
}
