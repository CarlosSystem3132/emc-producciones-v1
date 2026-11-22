import { useEffect, useState } from 'react';
import { api, getToken, login, setToken, ApiError } from '../../lib/adminApi';
import type { Usuario } from '../../lib/adminApi';
import Dashboard from './sections/Dashboard';
import Empresas from './sections/Empresas';
import Leads from './sections/Leads';
import Stands from './sections/Stands';
import Reservas from './sections/Reservas';
import Usuarios from './sections/Usuarios';
import Plantillas from './sections/Plantillas';
import Comunicaciones from './sections/Comunicaciones';
import Perfil from './sections/Perfil';
import Secuencias from './sections/Secuencias';
import Prospeccion from './sections/Prospeccion';
import Reportes from './sections/Reportes';
import AgentesIA from './sections/AgentesIA';
import Patrocinadores from './sections/Patrocinadores';
import Notificaciones from './sections/Notificaciones';

type Section =
  | 'dashboard'
  | 'empresas'
  | 'leads'
  | 'stands'
  | 'reservas'
  | 'usuarios'
  | 'plantillas'
  | 'comunicaciones'
  | 'secuencias'
  | 'prospeccion'
  | 'reportes'
  | 'agentes'
  | 'patrocinadores'
  | 'notificaciones'
  | 'perfil';

type Grupo = 'General' | 'Comercial' | 'Comunicación' | 'Inteligencia' | 'Administración' | 'Cuenta';

const NAV: { id: Section; label: string; icon: string; grupo: Grupo; soloAdmin?: boolean }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊', grupo: 'General' },
  { id: 'notificaciones', label: 'Notificaciones', icon: '🔔', grupo: 'General' },
  { id: 'empresas', label: 'Empresas', icon: '🏢', grupo: 'Comercial' },
  { id: 'leads', label: 'Leads', icon: '📈', grupo: 'Comercial' },
  { id: 'stands', label: 'Stands', icon: '🗺️', grupo: 'Comercial' },
  { id: 'reservas', label: 'Reservas', icon: '🎟️', grupo: 'Comercial' },
  { id: 'comunicaciones', label: 'Comunicaciones', icon: '📣', grupo: 'Comunicación' },
  { id: 'plantillas', label: 'Plantillas', icon: '📝', grupo: 'Comunicación' },
  { id: 'secuencias', label: 'Secuencias', icon: '⏱️', grupo: 'Comunicación' },
  { id: 'prospeccion', label: 'Prospección IA', icon: '🤖', grupo: 'Inteligencia' },
  { id: 'reportes', label: 'Reportes', icon: '📉', grupo: 'Inteligencia' },
  { id: 'agentes', label: 'Agentes IA', icon: '🧠', grupo: 'Inteligencia', soloAdmin: true },
  { id: 'patrocinadores', label: 'Patrocinadores', icon: '🏆', grupo: 'Administración', soloAdmin: true },
  // docs/07: solo el administrador gestiona ejecutivos
  { id: 'usuarios', label: 'Ejecutivos', icon: '👥', grupo: 'Administración', soloAdmin: true },
  { id: 'perfil', label: 'Mi perfil', icon: '👤', grupo: 'Cuenta' },
];

const ORDEN_GRUPOS: Grupo[] = ['General', 'Comercial', 'Comunicación', 'Inteligencia', 'Administración', 'Cuenta'];

function LoginScreen({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    setError(null);
    try {
      await login(email, password);
      onLogin();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'No se pudo iniciar sesión');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="admin-login-wrap">
      <form className="admin-login-card" onSubmit={handleSubmit}>
        <span className="section-tag">Panel privado</span>
        <h1>EMC Producciones</h1>
        <p>Acceso para administradores y ejecutivos de ventas.</p>
        <label className="reserva-field">
          Correo electrónico
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="username" />
        </label>
        <label className="reserva-field">
          Contraseña
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </label>
        {error && <p className="reserva-error">⚠️ {error}</p>}
        <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={sending}>
          {sending ? 'Ingresando…' : 'Ingresar'}
        </button>
      </form>
    </div>
  );
}

export default function AdminApp() {
  const [authed, setAuthed] = useState<boolean>(() => getToken() !== null);
  const [section, setSection] = useState<Section>('dashboard');
  const [user, setUser] = useState<Usuario | null>(null);
  const [menuAbierto, setMenuAbierto] = useState(false);

  useEffect(() => {
    if (!authed) return;
    // Datos del usuario autenticado (rol para el menú y el perfil)
    api
      .get<Usuario>('/auth/me')
      .then(setUser)
      .catch(() => {});
  }, [authed]);

  if (!authed) {
    return <LoginScreen onLogin={() => setAuthed(true)} />;
  }

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    setAuthed(false);
  };

  const isAdmin = user?.rol === 'admin';
  const nav = NAV.filter((item) => !item.soloAdmin || isAdmin);
  const grupos = ORDEN_GRUPOS.map((g) => ({
    grupo: g,
    items: nav.filter((item) => item.grupo === g),
  })).filter((g) => g.items.length > 0);

  const irA = (id: Section) => {
    setSection(id);
    setMenuAbierto(false); // cierra el drawer en móvil
  };

  return (
    <div className="admin-shell">
      {/* Barra superior visible solo en pantallas pequeñas */}
      <header className="admin-topbar">
        <button
          type="button"
          className="admin-menu-btn"
          aria-label={menuAbierto ? 'Cerrar menú' : 'Abrir menú'}
          aria-expanded={menuAbierto}
          onClick={() => setMenuAbierto((v) => !v)}
        >
          ☰
        </button>
        <strong>EXPOINCO 2027</strong>
        <span className="admin-pill">{isAdmin ? 'admin' : 'ejecutivo'}</span>
      </header>

      {menuAbierto && (
        <div className="admin-sidebar-backdrop" onClick={() => setMenuAbierto(false)} aria-hidden="true" />
      )}

      <aside className={`admin-sidebar ${menuAbierto ? 'open' : ''}`}>
        <div className="admin-brand">
          <span className="section-tag">Panel {isAdmin ? 'admin' : 'ejecutivo'}</span>
          <strong>EXPOINCO 2027</strong>
        </div>
        <nav className="admin-nav" aria-label="Secciones del panel">
          {grupos.map(({ grupo, items }) => (
            <div key={grupo}>
              <div className="admin-nav-group">{grupo}</div>
              {items.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={`admin-nav-btn ${section === item.id ? 'active' : ''}`}
                  aria-current={section === item.id ? 'page' : undefined}
                  onClick={() => irA(item.id)}
                >
                  <span aria-hidden="true">{item.icon}</span> {item.label}
                </button>
              ))}
            </div>
          ))}
        </nav>
        <div className="admin-sidebar-footer">
          {user && (
            <small title={user.email}>
              <strong>{user.nombre_completo}</strong>
              <span className="admin-pill">{user.rol}</span>
            </small>
          )}
          <button type="button" className="admin-logout-btn" onClick={handleLogout}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="admin-main">
        {section === 'dashboard' && <Dashboard />}
        {section === 'empresas' && <Empresas />}
        {section === 'leads' && <Leads />}
        {section === 'stands' && <Stands />}
        {section === 'reservas' && <Reservas />}
        {section === 'comunicaciones' && <Comunicaciones isAdmin={isAdmin} />}
        {section === 'plantillas' && <Plantillas isAdmin={isAdmin} />}
        {section === 'secuencias' && <Secuencias />}
        {section === 'prospeccion' && <Prospeccion />}
        {section === 'reportes' && <Reportes />}
        {section === 'agentes' && isAdmin && <AgentesIA />}
        {section === 'patrocinadores' && isAdmin && <Patrocinadores />}
        {section === 'notificaciones' && <Notificaciones />}
        {section === 'usuarios' && isAdmin && <Usuarios />}
        {section === 'perfil' && <Perfil />}
      </main>
    </div>
  );
}
