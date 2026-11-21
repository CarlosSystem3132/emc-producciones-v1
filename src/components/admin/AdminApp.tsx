import { useEffect, useState } from 'react';
import { getToken, login, setToken, ApiError } from '../../lib/adminApi';
import Dashboard from './sections/Dashboard';
import Empresas from './sections/Empresas';
import Leads from './sections/Leads';
import Stands from './sections/Stands';
import Reservas from './sections/Reservas';
import Usuarios from './sections/Usuarios';
import Plantillas from './sections/Plantillas';
import Comunicaciones from './sections/Comunicaciones';

type Section = 'dashboard' | 'empresas' | 'leads' | 'stands' | 'reservas' | 'usuarios' | 'plantillas' | 'comunicaciones';

const NAV: { id: Section; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: '📊' },
  { id: 'empresas', label: 'Empresas', icon: '🏢' },
  { id: 'leads', label: 'Leads', icon: '📈' },
  { id: 'stands', label: 'Stands', icon: '🗺️' },
  { id: 'reservas', label: 'Reservas', icon: '🎟️' },
  { id: 'comunicaciones', label: 'Comunicaciones', icon: '📣' },
  { id: 'plantillas', label: 'Plantillas', icon: '📝' },
  { id: 'usuarios', label: 'Ejecutivos', icon: '👥' },
];

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
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    if (!authed) return;
    // Muestra el correo del usuario (opcional, tolera fallos)
    import('../../lib/adminApi').then(({ api }) =>
      api
        .get<{ email: string }>('/auth/me')
        .then((u) => setUserEmail(u.email))
        .catch(() => {}),
    );
  }, [authed]);

  if (!authed) {
    return <LoginScreen onLogin={() => setAuthed(true)} />;
  }

  const handleLogout = () => {
    setToken(null);
    setAuthed(false);
  };

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="admin-brand">
          <span className="section-tag">Panel admin</span>
          <strong>EXPOINCO 2027</strong>
        </div>
        <nav className="admin-nav">
          {NAV.map((item) => (
            <button
              key={item.id}
              type="button"
              className={`admin-nav-btn ${section === item.id ? 'active' : ''}`}
              onClick={() => setSection(item.id)}
            >
              <span aria-hidden="true">{item.icon}</span> {item.label}
            </button>
          ))}
        </nav>
        <div className="admin-sidebar-footer">
          {userEmail && <small title={userEmail}>{userEmail}</small>}
          <button type="button" className="admin-nav-btn" onClick={handleLogout}>
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
        {section === 'comunicaciones' && <Comunicaciones />}
        {section === 'plantillas' && <Plantillas />}
        {section === 'usuarios' && <Usuarios />}
      </main>
    </div>
  );
}
