import { useEffect, useRef, useState } from 'react';
import { X } from 'lucide-react';

export default function BrochureModal() {
  const [isOpen, setIsOpen] = useState(false);
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
          <p>Tapas del brochure oficial de difusión del evento.</p>
        </div>

        <div className="brochure-modal-grid">
          <div className="brochure-view-card">
            <img
              src="/assets/Portada-of.jpg"
              alt="Portada del Brochure Oficial EXPOINCO 2027"
              decoding="async"
            />
            <div className="brochure-view-caption">Portada Oficial - EXPOINCO 2027</div>
          </div>

          <div className="brochure-view-card">
            <img
              src="/assets/Contra-p.jpg"
              alt="Contraportada del Brochure Oficial EXPOINCO 2027"
              decoding="async"
            />
            <div className="brochure-view-caption">Contraportada · Sede &amp; Contacto</div>
          </div>
        </div>
      </div>
    </div>
  );
}
