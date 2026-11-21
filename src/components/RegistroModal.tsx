import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';

const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/api/v1';

const initialForm = {
  razon_social: '',
  nombre_comercial: '',
  rubro: '',
  ciudad: '',
  nombre_contacto: '',
  cargo_contacto: '',
  email: '',
  whatsapp: '',
  telefono: '',
  tipo_solicitud: 'registro',
  mensaje: '',
};

/**
 * Formulario público de registro de empresas (docs/02 — módulo público).
 * Se abre desde cualquier botón con el atributo data-open-registro.
 */
export default function RegistroModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [form, setForm] = useState(initialForm);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const triggers = Array.from(document.querySelectorAll('[data-open-registro]'));
    const handleOpen = () => {
      setForm(initialForm);
      setError(null);
      setSuccess(false);
      setIsOpen(true);
    };
    triggers.forEach((el) => el.addEventListener('click', handleOpen));
    return () => triggers.forEach((el) => el.removeEventListener('click', handleOpen));
  }, []);

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
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const set = (key: keyof typeof initialForm) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSending(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/public/registro`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        let detail = 'No se pudo enviar el registro';
        try {
          const body = await res.json();
          if (typeof body.detail === 'string') detail = body.detail;
        } catch {
          // cuerpo no JSON
        }
        throw new Error(detail);
      }
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error inesperado');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="brochure-modal open" role="dialog" aria-modal="true" aria-labelledby="registro-modal-title">
      <div className="brochure-modal-overlay" onClick={() => setIsOpen(false)} />
      <div className="brochure-modal-container">
        <button ref={closeBtnRef} className="brochure-modal-close" type="button" onClick={() => setIsOpen(false)} aria-label="Cerrar">
          <X size={20} />
        </button>

        <div className="brochure-modal-header">
          <span className="section-tag">Participa en EXPOINCO 2027</span>
          <h2 id="registro-modal-title">Registra tu empresa</h2>
          {success ? (
            <p>Recibimos tu información.</p>
          ) : (
            <p>Completa el formulario y un ejecutivo de ventas se pondrá en contacto contigo.</p>
          )}
        </div>

        {success ? (
          <div className="reserva-success">
            <p>
              ✅ <strong>¡Registro recibido!</strong> Nuestro equipo comercial te contactará pronto para contarte
              sobre stands, paquetes y oportunidades de negocio.
            </p>
            <button type="button" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={() => setIsOpen(false)}>
              Cerrar
            </button>
          </div>
        ) : (
          <form className="reserva-form" onSubmit={handleSubmit}>
            <fieldset disabled={sending}>
              <legend>Datos de la empresa</legend>
              <div className="reserva-grid">
                <label className="reserva-field span-2">
                  Razón social *
                  <input type="text" required value={form.razon_social} onChange={set('razon_social')} />
                </label>
                <label className="reserva-field">
                  Nombre comercial
                  <input type="text" value={form.nombre_comercial} onChange={set('nombre_comercial')} />
                </label>
                <label className="reserva-field">
                  Rubro
                  <input type="text" value={form.rubro} onChange={set('rubro')} />
                </label>
                <label className="reserva-field">
                  Ciudad
                  <input type="text" value={form.ciudad} onChange={set('ciudad')} />
                </label>
              </div>

              <legend>Persona de contacto</legend>
              <div className="reserva-grid">
                <label className="reserva-field span-2">
                  Nombre completo *
                  <input type="text" required value={form.nombre_contacto} onChange={set('nombre_contacto')} />
                </label>
                <label className="reserva-field">
                  Cargo
                  <input type="text" value={form.cargo_contacto} onChange={set('cargo_contacto')} />
                </label>
                <label className="reserva-field">
                  Correo electrónico
                  <input type="email" value={form.email} onChange={set('email')} />
                </label>
                <label className="reserva-field">
                  WhatsApp
                  <input type="tel" value={form.whatsapp} onChange={set('whatsapp')} />
                </label>
                <label className="reserva-field">
                  Teléfono
                  <input type="tel" value={form.telefono} onChange={set('telefono')} />
                </label>
              </div>

              <legend>Solicitud</legend>
              <div className="reserva-grid">
                <label className="reserva-field">
                  Tipo de solicitud
                  <select className="admin-select-mini" value={form.tipo_solicitud} onChange={set('tipo_solicitud')}>
                    <option value="registro">Registro general</option>
                    <option value="propuesta">Solicitar propuesta</option>
                  </select>
                </label>
                <label className="reserva-field span-2">
                  Mensaje (opcional)
                  <input type="text" maxLength={1000} value={form.mensaje} onChange={set('mensaje')} />
                </label>
              </div>
            </fieldset>

            {error && <p className="reserva-error">⚠️ {error}</p>}

            <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }} disabled={sending}>
              {sending ? 'Enviando…' : 'Enviar registro'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
