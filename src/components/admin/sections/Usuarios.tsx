import { useCallback, useEffect, useState } from 'react';
import { api, fecha, ApiError } from '../../../lib/adminApi';
import type { ListResponse, Usuario } from '../../../lib/adminApi';

const ESTADOS: Usuario['estado'][] = ['activo', 'bloqueado', 'inactivo'];

export default function Usuarios() {
  const [items, setItems] = useState<Usuario[]>([]);
  const [total, setTotal] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    nombre_completo: '',
    email: '',
    password: '',
    telefono: '',
    whatsapp: '',
    cargo: '',
    especialidad: '',
  });

  const load = useCallback(async () => {
    try {
      const res = await api.get<ListResponse<Usuario>>('/users');
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
      await api.post('/users', {
        ...form,
        telefono: form.telefono || null,
        whatsapp: form.whatsapp || null,
        cargo: form.cargo || null,
        especialidad: form.especialidad || null,
        rol: 'ejecutivo',
      });
      setCreating(false);
      setInfo('Ejecutivo creado.');
      setForm({ nombre_completo: '', email: '', password: '', telefono: '', whatsapp: '', cargo: '', especialidad: '' });
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo crear');
      setInfo(null);
    }
  };

  const cambiarEstado = (u: Usuario, estado: Usuario['estado']) => {
    const action = estado === 'activo' ? 'activate' : estado === 'bloqueado' ? 'block' : 'deactivate';
    run(() => api.post(`/users/${u.id}/${action}`), `Usuario ${estado}.`);
  };

  const resetPassword = (u: Usuario) => {
    const nueva = prompt(`Nueva contraseña para ${u.nombre_completo} (mín. 8 caracteres):`);
    if (!nueva) return;
    run(() => api.post(`/users/${u.id}/reset-password`, { new_password: nueva }), 'Contraseña restablecida.');
  };

  const eliminar = (u: Usuario) => {
    if (!confirm(`¿Eliminar a ${u.nombre_completo}? (soft delete; si tiene empresas asignadas será rechazado)`)) return;
    run(() => api.delete(`/users/${u.id}`), 'Usuario eliminado.');
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Ejecutivos de ventas</h2>
        <p>{total} usuario(s). Solo el administrador gestiona estas cuentas.</p>
      </header>

      <div className="admin-toolbar">
        <button type="button" className="btn btn-primary" onClick={() => setCreating((v) => !v)}>
          {creating ? 'Cancelar' : '+ Nuevo ejecutivo'}
        </button>
      </div>

      {creating && (
        <form className="admin-form-grid" onSubmit={handleCreate}>
          <input className="admin-input" required placeholder="Nombre completo *" value={form.nombre_completo}
            onChange={(e) => setForm({ ...form, nombre_completo: e.target.value })} />
          <input className="admin-input" required type="email" placeholder="Correo de acceso *" value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="admin-input" required type="password" placeholder="Contraseña inicial * (mín. 8)" value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <input className="admin-input" placeholder="Cargo" value={form.cargo}
            onChange={(e) => setForm({ ...form, cargo: e.target.value })} />
          <input className="admin-input" placeholder="Teléfono" value={form.telefono}
            onChange={(e) => setForm({ ...form, telefono: e.target.value })} />
          <input className="admin-input" placeholder="WhatsApp" value={form.whatsapp}
            onChange={(e) => setForm({ ...form, whatsapp: e.target.value })} />
          <input className="admin-input" placeholder="Especialidad / rubro" value={form.especialidad}
            onChange={(e) => setForm({ ...form, especialidad: e.target.value })} />
          <button type="submit" className="btn btn-primary">Crear ejecutivo</button>
        </form>
      )}

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {info && <p className="admin-ok">✅ {info}</p>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Cargo</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Registro</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((u) => (
              <tr key={u.id}>
                <td><strong>{u.nombre_completo}</strong></td>
                <td>{u.email}</td>
                <td>{u.cargo ?? '—'}</td>
                <td><span className="admin-pill">{u.rol}</span></td>
                <td>
                  <select
                    className={`admin-select-mini estado-${u.estado}`}
                    value={u.estado}
                    onChange={(e) => cambiarEstado(u, e.target.value as Usuario['estado'])}
                  >
                    {ESTADOS.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </td>
                <td>{fecha(u.created_at)}</td>
                <td className="admin-actions">
                  <button type="button" className="admin-btn-mini" onClick={() => resetPassword(u)}>
                    Reset clave
                  </button>
                  <button type="button" className="admin-btn-mini danger" onClick={() => eliminar(u)}>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={7} className="admin-muted">Sin usuarios.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
