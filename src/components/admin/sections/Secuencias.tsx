import { useCallback, useEffect, useState } from 'react';
import { useAutoRefresh } from '../../../lib/useAutoRefresh';
import { api, fecha, ApiError } from '../../../lib/adminApi';
import type { Inscripcion, Secuencia } from '../../../lib/adminApi';

/**
 * Secuencias de seguimiento comercial (Fase 2 — docs/10).
 * Pasos escalonados (plantilla + días de espera) que se envían a las
 * empresas inscritas. La ejecución la corre FastAPI y n8n solo despacha.
 */
export default function Secuencias() {
  const [items, setItems] = useState<Secuencia[]>([]);
  const [inscripciones, setInscripciones] = useState<Inscripcion[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    nombre: '',
    descripcion: '',
    canal: 'email',
    pasosTexto: '0|Invitación inicial\nd7|Seguimiento 1\nd14|Seguimiento 2',
  });

  const load = useCallback(async () => {
    try {
      const [seqs, insc] = await Promise.all([
        api.get<Secuencia[]>('/secuencias'),
        api.get<Inscripcion[]>('/secuencias/inscripciones/listado'),
      ]);
      setItems(seqs);
      setInscripciones(insc);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);
  useAutoRefresh(load); // refresco automático al cambiar datos

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

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Formato de pasos: una línea por paso «días|mensaje» (orden automático)
      const pasos = form.pasosTexto
        .split('\n')
        .map((linea, idx) => {
          const [dias, ...resto] = linea.split('|');
          const diasEspera = Number(dias.replace(/^d/, '').trim());
          return {
            orden: idx + 1,
            dias_espera: isNaN(diasEspera) ? 0 : diasEspera,
            mensaje: resto.join('|').trim() || null,
            plantilla_id: null,
          };
        })
        .filter((p) => p.mensaje);

      await api.post('/secuencias', {
        nombre: form.nombre,
        descripcion: form.descripcion || null,
        canal: form.canal,
        pasos,
      });
      setCreating(false);
      setInfo('✅ Secuencia creada.');
      setForm({ ...form, nombre: '', descripcion: '' });
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo crear');
    }
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Secuencias de seguimiento</h2>
        <p>Mensajes escalonados para nutrir contactos. Los pasos se envían con control de frecuencia vía n8n.</p>
      </header>

      <div className="admin-toolbar">
        <button type="button" className="btn btn-primary" onClick={() => setCreating((v) => !v)}>
          {creating ? 'Cancelar' : '+ Nueva secuencia'}
        </button>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => run(() => api.post('/secuencias/ejecutar-pendientes'), 'Pasos ejecutados:')}
        >
          ▶ Ejecutar pasos vencidos
        </button>
      </div>

      {creating && (
        <form className="admin-form-grid" onSubmit={handleCreate}>
          <input className="admin-input" required placeholder="Nombre *" value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          <input className="admin-input" placeholder="Descripción" value={form.descripcion}
            onChange={(e) => setForm({ ...form, descripcion: e.target.value })} />
          <select className="admin-input" value={form.canal}
            onChange={(e) => setForm({ ...form, canal: e.target.value })}>
            <option value="email">email</option>
            <option value="whatsapp">whatsapp</option>
          </select>
          <textarea
            className="admin-input"
            style={{ width: '100%', minHeight: '90px' }}
            placeholder={'Pasos, uno por línea (días desde el paso anterior|mensaje):\nd0|Invitación inicial\nd7|Seguimiento'}
            value={form.pasosTexto}
            onChange={(e) => setForm({ ...form, pasosTexto: e.target.value })}
          />
          <button type="submit" className="btn btn-primary">Crear secuencia</button>
        </form>
      )}

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {info && <p className="admin-ok">{info}</p>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr><th>Secuencia</th><th>Canal</th><th>Estado</th><th>Pasos</th><th>Inscripciones activas</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {items.map((s) => (
              <tr key={s.id}>
                <td><strong>{s.nombre}</strong></td>
                <td>{s.canal}</td>
                <td><span className="admin-pill">{s.estado}</span></td>
                <td>{s.pasos}</td>
                <td>{s.inscripciones_activas}</td>
                <td className="admin-actions">
                  <button
                    type="button"
                    className="admin-btn-mini"
                    onClick={() => {
                      const empresaId = prompt('ID de la empresa a inscribir (sección Empresas):');
                      if (!empresaId) return;
                      run(() => api.post(`/secuencias/${s.id}/inscribir`, { empresa_id: empresaId }), 'Empresa inscrita.');
                    }}
                  >
                    Inscribir empresa
                  </button>
                  <button
                    type="button"
                    className={`admin-btn-mini ${s.estado === 'activo' ? 'danger' : 'success'}`}
                    onClick={() =>
                      run(
                        () => api.patch(`/secuencias/${s.id}`, { estado: s.estado === 'activo' ? 'inactivo' : 'activo' }),
                        'Estado actualizado.',
                      )
                    }
                  >
                    {s.estado === 'activo' ? 'Desactivar' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={6} className="admin-muted">Sin secuencias. Crea la primera.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="admin-panel" style={{ marginTop: '1.25rem' }}>
        <h3>Inscripciones</h3>
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr><th>Empresa</th><th>Paso actual</th><th>Próxima ejecución</th><th>Estado</th></tr>
            </thead>
            <tbody>
              {inscripciones.map((i) => (
                <tr key={i.id}>
                  <td><strong>{i.empresa}</strong></td>
                  <td>{i.paso_actual}</td>
                  <td>{fecha(i.proxima_ejecucion)}</td>
                  <td><span className="admin-pill">{i.estado}</span></td>
                </tr>
              ))}
              {inscripciones.length === 0 && (
                <tr><td colSpan={4} className="admin-muted">Sin inscripciones.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
