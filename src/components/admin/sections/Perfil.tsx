import { useEffect, useState } from 'react';
import { api, changeMyPassword, ApiError } from '../../../lib/adminApi';
import type { Usuario } from '../../../lib/adminApi';

/**
 * Perfil del usuario autenticado (docs/08 — Panel del ejecutivo de ventas).
 * Cada ejecutivo edita únicamente su propio perfil: datos de contacto,
 * WhatsApp/correo de notificaciones, cargo, experiencia y especialidad.
 * El rol y el estado solo los gestiona el administrador (docs/07).
 */
export default function Perfil() {
  const [user, setUser] = useState<Usuario | null>(null);
  const [form, setForm] = useState({
    nombre_completo: '',
    telefono: '',
    whatsapp: '',
    correo_contacto: '',
    cargo: '',
    experiencia: '',
    especialidad: '',
    foto_url: '',
  });
  const [clave, setClave] = useState({ actual: '', nueva: '', repetir: '' });
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api
      .get<Usuario>('/auth/me')
      .then((u) => {
        setUser(u);
        setForm({
          nombre_completo: u.nombre_completo ?? '',
          telefono: u.telefono ?? '',
          whatsapp: u.whatsapp ?? '',
          correo_contacto: u.correo_contacto ?? '',
          cargo: u.cargo ?? '',
          experiencia: u.experiencia ?? '',
          especialidad: u.especialidad ?? '',
          foto_url: u.foto_url ?? '',
        });
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Error al cargar el perfil'));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    setSaving(true);
    try {
      const updated = await api.patch<Usuario>(`/users/${user.id}`, {
        nombre_completo: form.nombre_completo,
        telefono: form.telefono || null,
        whatsapp: form.whatsapp || null,
        correo_contacto: form.correo_contacto || null,
        cargo: form.cargo || null,
        experiencia: form.experiencia || null,
        especialidad: form.especialidad || null,
        foto_url: form.foto_url || null,
      });
      setUser(updated);
      setInfo('Perfil actualizado.');
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo guardar el perfil');
      setInfo(null);
    } finally {
      setSaving(false);
    }
  };

  const handlePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (clave.nueva !== clave.repetir) {
      setError('Las contraseñas nuevas no coinciden');
      setInfo(null);
      return;
    }
    try {
      await changeMyPassword(clave.actual, clave.nueva);
      setClave({ actual: '', nueva: '', repetir: '' });
      setInfo('Contraseña actualizada.');
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo cambiar la contraseña');
      setInfo(null);
    }
  };

  if (error && !user) return <p className="reserva-error">⚠️ {error}</p>;
  if (!user) return <p className="admin-loading">Cargando perfil…</p>;

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Mi perfil</h2>
        <p>
          Tus datos de contacto y notificaciones.{' '}
          <span className="admin-pill">{user.rol}</span>{' '}
          <span className="admin-muted">
            (rol y estado los gestiona el administrador)
          </span>
        </p>
      </header>

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {info && <p className="admin-ok">✅ {info}</p>}

      <form className="admin-panel" onSubmit={handleSave}>
        <h3>Datos personales y de contacto</h3>
        <div className="admin-form-grid">
          <input
            className="admin-input"
            required
            placeholder="Nombre completo *"
            value={form.nombre_completo}
            onChange={(e) => setForm({ ...form, nombre_completo: e.target.value })}
          />
          <input
            className="admin-input"
            placeholder="Teléfono"
            value={form.telefono}
            onChange={(e) => setForm({ ...form, telefono: e.target.value })}
          />
          <input
            className="admin-input"
            placeholder="WhatsApp (notificaciones)"
            value={form.whatsapp}
            onChange={(e) => setForm({ ...form, whatsapp: e.target.value })}
          />
          <input
            className="admin-input"
            type="email"
            placeholder="Correo de contacto (notificaciones)"
            value={form.correo_contacto}
            onChange={(e) => setForm({ ...form, correo_contacto: e.target.value })}
          />
          <input
            className="admin-input"
            placeholder="Cargo"
            value={form.cargo}
            onChange={(e) => setForm({ ...form, cargo: e.target.value })}
          />
          <input
            className="admin-input"
            placeholder="Especialidad comercial / rubro"
            value={form.especialidad}
            onChange={(e) => setForm({ ...form, especialidad: e.target.value })}
          />
          <input
            className="admin-input"
            placeholder="URL de foto de perfil"
            value={form.foto_url}
            onChange={(e) => setForm({ ...form, foto_url: e.target.value })}
          />
        </div>
        <textarea
          className="admin-input"
          style={{ width: '100%', minHeight: '80px', marginTop: '0.75rem' }}
          placeholder="Experiencia profesional"
          value={form.experiencia}
          onChange={(e) => setForm({ ...form, experiencia: e.target.value })}
        />
        <div className="admin-toolbar">
          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? 'Guardando…' : 'Guardar perfil'}
          </button>
        </div>
      </form>

      <form className="admin-panel" onSubmit={handlePassword} style={{ marginTop: '1.25rem' }}>
        <h3>Cambiar contraseña</h3>
        <div className="admin-form-grid">
          <input
            className="admin-input"
            required
            type="password"
            autoComplete="current-password"
            placeholder="Contraseña actual *"
            value={clave.actual}
            onChange={(e) => setClave({ ...clave, actual: e.target.value })}
          />
          <input
            className="admin-input"
            required
            type="password"
            minLength={8}
            autoComplete="new-password"
            placeholder="Nueva contraseña * (mín. 8)"
            value={clave.nueva}
            onChange={(e) => setClave({ ...clave, nueva: e.target.value })}
          />
          <input
            className="admin-input"
            required
            type="password"
            minLength={8}
            autoComplete="new-password"
            placeholder="Repetir nueva contraseña *"
            value={clave.repetir}
            onChange={(e) => setClave({ ...clave, repetir: e.target.value })}
          />
          <button type="submit" className="btn btn-primary">Cambiar contraseña</button>
        </div>
      </form>
    </div>
  );
}
