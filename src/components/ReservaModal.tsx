import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';
import { solicitarReserva, notificarDatosActualizados } from '../lib/api';
import { getFuente, track } from '../utils/utm';
import type { ReservaCreada } from '../lib/api';

interface ReservaModalProps {
  open: boolean;
  onClose: () => void;
  /** Etiqueta visible del stand, p. ej. "01" */
  standLabel: string;
  /** UUID del stand en la API (si está disponible) */
  standUuid?: string;
}

const initialForm = {
  razon_social: '',
  nombre_comercial: '',
  rubro: '',
  ciudad: '',
  nombre: '',
  cargo: '',
  email: '',
  whatsapp: '',
  telefono: '',
};

export default function ReservaModal({ open, onClose, standLabel, standUuid }: ReservaModalProps) {
  const [form, setForm] = useState(initialForm);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<ReservaCreada | null>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeBtnRef.current?.focus();
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = previousOverflow;
    };
  }, [open, onClose]);

  if (!open) return null;

  const set = (key: keyof typeof initialForm) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [key]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!standUuid) return;
    setSending(true);
    setError(null);
    try {
      const reserva = await solicitarReserva({
        stand_id: standUuid,
        empresa: {
          razon_social: form.razon_social,
          nombre_comercial: form.nombre_comercial || null,
          rubro: form.rubro || null,
          ciudad: form.ciudad || null,
          origen: getFuente() ?? 'web',
        },
        contacto: {
          nombre: form.nombre,
          cargo: form.cargo || null,
          email: form.email || null,
          whatsapp: form.whatsapp || null,
          telefono: form.telefono || null,
        },
        interes: `Stand ${standLabel}`,
      });
      setSuccess(reserva);
      notificarDatosActualizados(); // refresca plano y contador sin recargar
      track('ReservaSolicitada', { content_name: standLabel });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo procesar la solicitud');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="brochure-modal open" role="dialog" aria-modal="true" aria-labelledby="reserva-modal-title">
      <div className="brochure-modal-overlay" onClick={onClose} />
      <div className="brochure-modal-container">
        <button ref={closeBtnRef} className="brochure-modal-close" type="button" onClick={onClose} aria-label="Cerrar">
          <X size={20} />
        </button>

        <div className="brochure-modal-header">
          <span className="section-tag">Reserva de stand</span>
          <h2 id="reserva-modal-title">STAND {standLabel} · EXPOINCO 2027</h2>
          {success ? (
            <p>Tu solicitud fue registrada correctamente.</p>
          ) : (
            <p>
              Completa tus datos empresariales. El stand quedará <strong>bloqueado por 30 minutos</strong> mientras
              un ejecutivo se pone en contacto contigo.
            </p>
          )}
        </div>

        {success ? (
          <div className="reserva-success">
            <p>
              ✅ <strong>¡Solicitud registrada!</strong> El stand {standLabel} está bloqueado temporalmente para tu
              empresa.
            </p>
            <p>
              Un ejecutivo de ventas te contactará antes de que expire el bloqueo (30 minutos). Si prefieres agilizar
              el proceso, escríbenos por WhatsApp:
            </p>
            <a
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
              href={`https://wa.me/59178873090?text=${encodeURIComponent(
                `Hola, acabo de solicitar el STAND ${standLabel} en EXPOINCO 2027 (empresa: ${form.razon_social}).`,
              )}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              Continuar por WhatsApp
            </a>
            <button type="button" className="btn" style={{ width: '100%', justifyContent: 'center' }} onClick={onClose}>
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

              <legend>Datos de contacto</legend>
              <div className="reserva-grid">
                <label className="reserva-field span-2">
                  Nombre completo *
                  <input type="text" required value={form.nombre} onChange={set('nombre')} />
                </label>
                <label className="reserva-field">
                  Cargo
                  <input type="text" value={form.cargo} onChange={set('cargo')} />
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
            </fieldset>

            {error && <p className="reserva-error">⚠️ {error}</p>}

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: '100%', justifyContent: 'center' }}
              disabled={sending || !standUuid}
            >
              {sending ? 'Enviando…' : `Reservar el Stand ${standLabel}`}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
