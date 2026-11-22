import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';
import API_URL from '../lib/api';
import { getFuente, track } from '../utils/utm';

/**
 * Brochure oficial con captura de leads (quick win 1 — INFORME.md §11).
 * La descarga del material se intercambia por los datos de contacto, que
 * entran al CRM como lead público con atribución de marketing (UTM).
 */
export default function BrochureModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [capturado, setCapturado] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    nombre_contacto: '',
    razon_social: '',
    email: '',
    whatsapp: '',
  });
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const triggerRef = useRef<HTMLElement | null>(null);

  // Botón del Hero (vive en un componente .astro, fuera de React)
  useEffect(() => {
    const btn = document.getElementById('openBrochureBtn');
    const handleOpen = () => {
      triggerRef.current = btn;
      setIsOpen(true);
    };
    btn?.addEventListener('click', handleOpen);
    return () => btn?.removeEventListener('click', handleOpen);
  }, []);

  // Escape + bloqueo de scroll + manejo de foco solo mientras el modal está abierto
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    window.addEventListener('keydown', handleKeyDown);

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeBtnRef.current?.focus();

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = previousOverflow;
      triggerRef.current?.focus();
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const close = () => setIsOpen(false);

  const set = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/public/registro`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          razon_social: form.razon_social,
          nombre_contacto: form.nombre_contacto,
          email: form.email || null,
          whatsapp: form.whatsapp || null,
          tipo_solicitud: 'brochure',
          mensaje: 'Descarga del brochure oficial EXPOINCO 2027',
          fuente: getFuente(),
        }),
      });
      if (!res.ok) {
        let detail = 'No se pudo procesar la solicitud';
        try {
          const body = await res.json();
          if (typeof body.detail === 'string') detail = body.detail;
        } catch {
          // cuerpo no JSON
        }
        throw new Error(detail);
      }
      setCapturado(true);
      track('Lead', { content_name: 'brochure_oficial' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setSending(false);
    }
  };

  return (
    <div
      className="brochure-modal open"
      role="dialog"
      aria-modal="true"
      aria-labelledby="brochure-modal-title"
    >
      <div className="brochure-modal-overlay" onClick={close} />
      <div className="brochure-modal-container">
        <button
          ref={closeBtnRef}
          className="brochure-modal-close"
          type="button"
          onClick={close}
          aria-label="Cerrar brochure"
        >
          <X size={20} />
        </button>

        <div className="brochure-modal-header">
          <span className="section-tag">Material Oficial</span>
          <h2 id="brochure-modal-title">Brochure Oficial EXPOINCO 2027</h2>
          {capturado ? (
            <p>¡Listo! Descarga el material oficial del evento.</p>
          ) : (
            <p>Completa tus datos y descarga el brochure oficial de difusión.</p>
          )}
        </div>

        {/* Captura de lead: se muestra hasta que el visitante deja sus datos */}
        {!capturado ? (
          <form className="brochure-lead-form" onSubmit={handleSubmit} style={{ padding: '1rem' }}>
            <label className="reserva-field">
              Nombre completo *
              <input required value={form.nombre_contacto} onChange={set('nombre_contacto')} />
            </label>
            <label className="reserva-field">
              Empresa *
              <input required value={form.razon_social} onChange={set('razon_social')} />
            </label>
            <label className="reserva-field">
              Correo electrónico
              <input type="email" value={form.email} onChange={set('email')} />
            </label>
            <label className="reserva-field">
              WhatsApp
              <input value={form.whatsapp} onChange={set('whatsapp')} />
            </label>
            {error && <p className="reserva-error">⚠️ {error}</p>}
            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
              disabled={sending}
            >
              {sending ? 'Enviando…' : '📥 Descargar brochure'}
            </button>
            <p className="admin-muted" style={{ fontSize: '0.75rem', marginTop: '0.5rem' }}>
              Usaremos tus datos solo para contactarte sobre la expo.
            </p>
          </form>
        ) : (
          <div className="brochure-modal-grid">
            <div className="brochure-view-card">
              <img
                src="/assets/Portada-of.jpg"
                alt="Portada del Brochure Oficial EXPOINCO 2027"
                decoding="async"
              />
              <div className="brochure-view-caption">
                Portada Oficial{' '}
                <a href="/assets/Portada-of.jpg" download onClick={() => track('Descarga', { material: 'portada' })}>
                  ⬇ Descargar
                </a>
              </div>
            </div>

            <div className="brochure-view-card">
              <img
                src="/assets/Contra-p.jpg"
                alt="Contraportada del Brochure Oficial EXPOINCO 2027"
                decoding="async"
              />
              <div className="brochure-view-caption">
                Contraportada · Sede &amp; Contacto{' '}
                <a href="/assets/Contra-p.jpg" download onClick={() => track('Descarga', { material: 'contraportada' })}>
                  ⬇ Descargar
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
