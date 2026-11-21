import { useCallback, useEffect, useState } from 'react';
import { api, ApiError } from '../../../lib/adminApi';
import type { Plantilla } from '../../../lib/adminApi';

const CANALES = ['email', 'whatsapp', 'chat', 'pdf'] as const;

export default function Plantillas() {
  const [items, setItems] = useState<Plantilla[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({ nombre: '', tipo: 'invitacion', canal: 'email' as string, contenido: '' });
  const [preview, setPreview] = useState<{ id: string; contenido: string; faltantes: string[] } | null>(null);
  const [varsInput, setVarsInput] = useState('');

  const load = useCallback(async () => {
    try {
      setItems(await api.get<Plantilla[]>('/plantillas'));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/plantillas', form);
      setCreating(false);
      setForm({ nombre: '', tipo: 'invitacion', canal: 'email', contenido: '' });
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo crear');
    }
  };

  const handlePreview = async (p: Plantilla) => {
    try {
      // Interpreta líneas "clave=valor" como variables
      const variables: Record<string, string> = {};
      for (const linea of varsInput.split('\n')) {
        const idx = linea.indexOf('=');
        if (idx > 0) variables[linea.slice(0, idx).trim()] = linea.slice(idx + 1).trim();
      }
      const res = await api.post<{ contenido: string; variables_faltantes: string[] }>(
        `/plantillas/${p.id}/render`,
        { variables },
      );
      setPreview({ id: p.id, contenido: res.contenido, faltantes: res.variables_faltantes });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al renderizar');
    }
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Plantillas</h2>
        <p>Mensajes con variables {'{{empresa}}'}, {'{{contacto}}'}, {'{{cargo}}'}… para invitaciones, propuestas y nutrición.</p>
      </header>

      <div className="admin-toolbar">
        <button type="button" className="btn btn-primary" onClick={() => setCreating((v) => !v)}>
          {creating ? 'Cancelar' : '+ Nueva plantilla'}
        </button>
      </div>

      {creating && (
        <form className="admin-form-inline" onSubmit={handleCreate}>
          <input className="admin-input" required placeholder="Nombre *" value={form.nombre}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })} />
          <select className="admin-input" value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>
            <option value="invitacion">Invitación</option>
            <option value="propuesta">Propuesta</option>
            <option value="contrato">Contrato</option>
            <option value="nutricion">Nutrición</option>
          </select>
          <select className="admin-input" value={form.canal} onChange={(e) => setForm({ ...form, canal: e.target.value })}>
            {CANALES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <textarea
            className="admin-input"
            required
            style={{ width: '100%', minHeight: '100px' }}
            placeholder="Contenido con variables {{empresa}}, {{contacto}}…"
            value={form.contenido}
            onChange={(e) => setForm({ ...form, contenido: e.target.value })}
          />
          <button type="submit" className="btn btn-primary">Crear plantilla</button>
        </form>
      )}

      <div className="admin-toolbar">
        <textarea
          className="admin-input"
          style={{ width: '100%', minHeight: '70px' }}
          placeholder={'Variables para previsualizar (una por línea):\nempresa=Mi Empresa SA\ncontacto=Juan Pérez\ncargo=Gerente'}
          value={varsInput}
          onChange={(e) => setVarsInput(e.target.value)}
        />
      </div>

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {preview && (
        <div className="admin-panel">
          <h3>Vista previa {preview.faltantes.length > 0 && <small className="admin-muted">(faltan: {preview.faltantes.join(', ')})</small>}</h3>
          <pre style={{ whiteSpace: 'pre-wrap', margin: 0, fontSize: '0.9rem' }}>{preview.contenido}</pre>
        </div>
      )}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Tipo</th>
              <th>Canal</th>
              <th>Estado</th>
              <th>Contenido</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.id}>
                <td><strong>{p.nombre}</strong></td>
                <td>{p.tipo}</td>
                <td>{p.canal}</td>
                <td><span className="admin-pill">{p.estado}</span></td>
                <td style={{ maxWidth: '320px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={p.contenido}>
                  {p.contenido}
                </td>
                <td>
                  <button type="button" className="admin-btn-mini" onClick={() => handlePreview(p)}>
                    Previsualizar
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={6} className="admin-muted">Sin plantillas. Crea la primera.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
