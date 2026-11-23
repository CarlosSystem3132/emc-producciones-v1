import { useState, useRef, useEffect } from 'react';
import type { KeyboardEvent, MouseEvent } from 'react';
import { motion } from 'framer-motion';
import { fetchPlano, EVENTO_DATOS } from '../lib/api';
import type { StandPlano } from '../lib/api';
import ReservaModal from './ReservaModal';

interface StandItem {
  id: number;
  sector: string;
  size: number;
  dim: string;
  reserved: boolean;
}

const STANDS: StandItem[] = [
  { id: 1, sector: 'Lateral Este · Sector Norte (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 2, sector: 'Lateral Este · Sector Norte (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 3, sector: 'Lateral Este · Sector Norte (Fila 3)', size: 9, dim: '3 × 3 m', reserved: true },
  { id: 4, sector: 'Acceso Norte · Zona Preferencial', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 5, sector: 'Acceso Norte · Zona Preferencial', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 6, sector: 'Lateral Oeste · Sector Norte (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 7, sector: 'Lateral Oeste · Sector Norte (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 8, sector: 'Lateral Oeste · Sector Norte (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 9, sector: 'Lateral Oeste · Sector Sur (Fila 1)', size: 9, dim: '3 × 3 m', reserved: true },
  { id: 10, sector: 'Lateral Oeste · Sector Sur (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 11, sector: 'Lateral Oeste · Sector Sur (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 12, sector: 'Acceso Sur Principal · Ala Oeste', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 13, sector: 'Acceso Sur Principal · Ala Este', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 14, sector: 'Lateral Este · Sector Sur (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 15, sector: 'Lateral Este · Sector Sur (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 16, sector: 'Lateral Este · Sector Sur (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 17, sector: 'Pabellón Central Sur · Col. Este (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 18, sector: 'Pabellón Central Sur · Col. Este (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 19, sector: 'Pabellón Central Sur · Col. Este (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 20, sector: 'Pabellón Central Sur · Col. Este (Fila 4)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 21, sector: 'Pabellón Central Sur · Col. Este (Fila 5)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 22, sector: 'Pabellón Central Norte · Col. Este (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 23, sector: 'Pabellón Central Norte · Col. Este (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 24, sector: 'Pabellón Central Norte · Col. Este (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 25, sector: 'Pabellón Central Norte · Col. Este (Fila 4)', size: 9, dim: '3 × 3 m', reserved: true },
  { id: 26, sector: 'Pabellón Central Sur · Columna 2 (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 27, sector: 'Pabellón Central Sur · Columna 2 (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 28, sector: 'Pabellón Central Sur · Columna 2 (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 29, sector: 'Pabellón Central Sur · Columna 2 (Fila 4)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 30, sector: 'Pabellón Central Sur · Columna 2 (Fila 5)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 31, sector: 'Pabellón Central Norte · Columna 2 (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 32, sector: 'Pabellón Central Norte · Columna 2 (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 33, sector: 'Pabellón Central Norte · Columna 2 (Fila 3)', size: 9, dim: '3 × 3 m', reserved: true },
  { id: 34, sector: 'Pabellón Central Norte · Columna 2 (Fila 4)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 35, sector: 'Pabellón Central Sur · Columna 3 (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 36, sector: 'Pabellón Central Sur · Columna 3 (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 37, sector: 'Pabellón Central Sur · Columna 3 (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 38, sector: 'Pabellón Central Sur · Columna 3 (Fila 4)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 39, sector: 'Pabellón Central Sur · Columna 3 (Fila 5)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 40, sector: 'Pabellón Central Norte · Columna 3 (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 41, sector: 'Pabellón Central Norte · Columna 3 (Fila 2)', size: 9, dim: '3 × 3 m', reserved: true },
  { id: 42, sector: 'Pabellón Central Norte · Columna 3 (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 43, sector: 'Pabellón Central Norte · Columna 3 (Fila 4)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 44, sector: 'Pabellón Central Sur · Col. Oeste (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 45, sector: 'Pabellón Central Sur · Col. Oeste (Fila 2)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 46, sector: 'Pabellón Central Sur · Col. Oeste (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 47, sector: 'Pabellón Central Sur · Col. Oeste (Fila 4)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 48, sector: 'Pabellón Central Sur · Col. Oeste (Fila 5)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 49, sector: 'Pabellón Central Norte · Col. Oeste (Fila 1)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 50, sector: 'Pabellón Central Norte · Col. Oeste (Fila 2)', size: 9, dim: '3 × 3 m', reserved: true },
  { id: 51, sector: 'Pabellón Central Norte · Col. Oeste (Fila 3)', size: 9, dim: '3 × 3 m', reserved: false },
  { id: 52, sector: 'Pabellón Central Norte · Col. Oeste (Fila 4)', size: 9, dim: '3 × 3 m', reserved: false },
];

const STAND_COORDS: Record<number, { x: number; y: number; tx: number; ty: number }> = {
  1: { x: 434, y: 292, tx: 451, ty: 304 },
  2: { x: 434, y: 264, tx: 451, ty: 276 },
  3: { x: 434, y: 236, tx: 451, ty: 248 },
  4: { x: 343, y: 168, tx: 360, ty: 180 },
  5: { x: 304, y: 168, tx: 321, ty: 180 },
  6: { x: 212, y: 236, tx: 229, ty: 248 },
  7: { x: 212, y: 264, tx: 229, ty: 276 },
  8: { x: 212, y: 292, tx: 229, ty: 304 },
  9: { x: 212, y: 372, tx: 229, ty: 384 },
  10: { x: 212, y: 400, tx: 229, ty: 412 },
  11: { x: 212, y: 428, tx: 229, ty: 440 },
  12: { x: 304, y: 496, tx: 321, ty: 508 },
  13: { x: 343, y: 496, tx: 360, ty: 508 },
  14: { x: 434, y: 428, tx: 451, ty: 440 },
  15: { x: 434, y: 400, tx: 451, ty: 412 },
  16: { x: 434, y: 372, tx: 451, ty: 384 },
  17: { x: 382, y: 456, tx: 399, ty: 468 },
  18: { x: 382, y: 428, tx: 399, ty: 440 },
  19: { x: 382, y: 400, tx: 399, ty: 412 },
  20: { x: 382, y: 372, tx: 399, ty: 384 },
  21: { x: 382, y: 344, tx: 399, ty: 356 },
  22: { x: 382, y: 292, tx: 399, ty: 304 },
  23: { x: 382, y: 264, tx: 399, ty: 276 },
  24: { x: 382, y: 236, tx: 399, ty: 248 },
  25: { x: 382, y: 208, tx: 399, ty: 220 },
  26: { x: 343, y: 456, tx: 360, ty: 468 },
  27: { x: 343, y: 428, tx: 360, ty: 440 },
  28: { x: 343, y: 400, tx: 360, ty: 412 },
  29: { x: 343, y: 372, tx: 360, ty: 384 },
  30: { x: 343, y: 344, tx: 360, ty: 356 },
  31: { x: 343, y: 292, tx: 360, ty: 304 },
  32: { x: 343, y: 264, tx: 360, ty: 276 },
  33: { x: 343, y: 236, tx: 360, ty: 248 },
  34: { x: 343, y: 208, tx: 360, ty: 220 },
  35: { x: 304, y: 456, tx: 321, ty: 468 },
  36: { x: 304, y: 428, tx: 321, ty: 440 },
  37: { x: 304, y: 400, tx: 321, ty: 412 },
  38: { x: 304, y: 372, tx: 321, ty: 384 },
  39: { x: 304, y: 344, tx: 321, ty: 356 },
  40: { x: 304, y: 292, tx: 321, ty: 304 },
  41: { x: 304, y: 264, tx: 321, ty: 276 },
  42: { x: 304, y: 236, tx: 321, ty: 248 },
  43: { x: 304, y: 208, tx: 321, ty: 220 },
  44: { x: 265, y: 456, tx: 282, ty: 468 },
  45: { x: 265, y: 428, tx: 282, ty: 440 },
  46: { x: 265, y: 400, tx: 282, ty: 412 },
  47: { x: 265, y: 372, tx: 282, ty: 384 },
  48: { x: 265, y: 344, tx: 282, ty: 356 },
  49: { x: 265, y: 292, tx: 282, ty: 304 },
  50: { x: 265, y: 264, tx: 282, ty: 276 },
  51: { x: 265, y: 236, tx: 282, ty: 248 },
  52: { x: 265, y: 208, tx: 282, ty: 220 },
};

const PRICE_PER_M2 = 98; // $us por m² (misma tarifa que Hero y Packages)

// Número al que llegan las solicitudes de reserva de stands.
// OJO: el resto del sitio usa 59168166068; confirma que este sea el número correcto.
const RESERVATIONS_WA = '59178873090';

// El estado real (disponible/reservado) viene de la API (/public/plano).
// STANDS es la plantilla visual del plano (posiciones y medidas) y el
// fallback cuando el backend no está disponible.

export default function InteractivePlano() {
  const [selectedId, setSelectedId] = useState<number>(1);
  const [filter, setFilter] = useState<'all' | 'disponibles' | 'reservados'>('all');
  const [tooltip, setTooltip] = useState({ show: false, x: 0, y: 0, text: '' });
  const [stands, setStands] = useState<StandItem[]>(STANDS);
  const [apiStands, setApiStands] = useState<Record<string, StandPlano>>({});
  const [modalOpen, setModalOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Disponibilidad en tiempo real desde el backend FastAPI.
  // Se refresca al montar, cuando un dato cambia (EVENTO_DATOS), al recuperar
  // el foco de la pestaña y cada 60 s: los cambios de reservas se ven sin F5.
  useEffect(() => {
    let cancelled = false;
    const cargarPlano = () => {
      fetchPlano()
        .then((plano) => {
          if (cancelled) return;
          const byCodigo: Record<string, StandPlano> = {};
          for (const s of plano.stands) byCodigo[s.codigo] = s;
          setApiStands(byCodigo);
          setStands(
            STANDS.map((stand) => {
              const match = byCodigo[String(stand.id)] ?? byCodigo[String(stand.id).padStart(2, '0')];
              return match ? { ...stand, reserved: match.estado !== 'disponible' } : stand;
            }),
          );
        })
        .catch(() => {
          // Backend fuera de línea: se mantiene la disponibilidad estática
        });
    };

    cargarPlano();
    window.addEventListener(EVENTO_DATOS, cargarPlano);
    window.addEventListener('focus', cargarPlano);
    document.addEventListener('visibilitychange', cargarPlano);
    const intervalo = window.setInterval(cargarPlano, 60000);

    return () => {
      cancelled = true;
      window.removeEventListener(EVENTO_DATOS, cargarPlano);
      window.removeEventListener('focus', cargarPlano);
      document.removeEventListener('visibilitychange', cargarPlano);
      window.clearInterval(intervalo);
    };
  }, []);

  const currentStand = stands.find((s) => s.id === selectedId) || stands[0];
  const estimatedPrice = currentStand.size * PRICE_PER_M2;
  const currentApiStand =
    apiStands[String(currentStand.id)] ?? apiStands[String(currentStand.id).padStart(2, '0')];
  const reservedCount = stands.filter((s) => s.reserved).length;
  const availableCount = stands.length - reservedCount;

  const handleMapClick = (e: MouseEvent<HTMLDivElement>) => {
    const target = (e.target as HTMLElement).closest('.stand-node');
    if (target) {
      const id = parseInt(target.getAttribute('data-id') || '', 10);
      if (id) setSelectedId(id);
    }
  };

  const handleStandKeyDown = (e: KeyboardEvent<SVGGElement>, id: number) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setSelectedId(id);
    }
  };

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    const target = (e.target as HTMLElement).closest('.stand-node');
    if (!target || !containerRef.current) {
      setTooltip((prev) => ({ ...prev, show: false }));
      return;
    }
    const id = parseInt(target.getAttribute('data-id') || '', 10);
    const stand = stands.find((s) => s.id === id);
    if (!stand) return;

    const rect = containerRef.current.getBoundingClientRect();
    const statusText = stand.reserved ? 'Reservado' : 'Disponible';
    const priceText = (stand.size * PRICE_PER_M2).toLocaleString('es-BO');

    setTooltip({
      show: true,
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      text: `STAND ${String(stand.id).padStart(2, '0')} · ${statusText} · $us ${priceText}`,
    });
  };

  return (
    <section className="plan" id="plano">
      <div className="wrap">
        <motion.div
          className="section-head"
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <span className="section-tag">Plano del pabellón</span>
          <h2>Elige tu ubicación</h2>
          <p>
            Plano oficial del Polideportivo Héroes de Octubre. Haz clic sobre
            cualquier stand para consultar medidas, disponibilidad y cotización inmediata.
          </p>
        </motion.div>

        <div className="plan-layout">
          <div className="arena-frame">
            <div className="venue-tag">
              <div className="venue-info-left">
                <strong>Polideportivo Héroes de Octubre</strong>
                <span>El Alto · Capacidad {STANDS.length} Stands</span>
              </div>
              <div className="stands-filter-btns">
                <button
                  type="button"
                  className={`btn-filter-stand ${filter === 'all' ? 'active' : ''}`}
                  aria-pressed={filter === 'all'}
                  onClick={() => setFilter('all')}
                >
                  Todos ({STANDS.length})
                </button>
                <button
                  type="button"
                  className={`btn-filter-stand ${filter === 'disponibles' ? 'active' : ''}`}
                  aria-pressed={filter === 'disponibles'}
                  onClick={() => setFilter('disponibles')}
                >
                  Disponibles ({availableCount})
                </button>
                <button
                  type="button"
                  className={`btn-filter-stand ${filter === 'reservados' ? 'active' : ''}`}
                  aria-pressed={filter === 'reservados'}
                  onClick={() => setFilter('reservados')}
                >
                  Reservados ({reservedCount})
                </button>
              </div>
            </div>

            <div
              className="arena-svg-container"
              ref={containerRef}
              onClick={handleMapClick}
              onMouseMove={handleMouseMove}
              onMouseLeave={() => setTooltip((prev) => ({ ...prev, show: false }))}
            >
              {tooltip.show && (
                <div
                  className="stand-hover-tooltip"
                  style={{ display: 'block', left: `${tooltip.x}px`, top: `${tooltip.y}px` }}
                >
                  {tooltip.text}
                </div>
              )}

              <svg
                className="arena-map-svg"
                viewBox="90 60 500 520"
                xmlns="http://www.w3.org/2000/svg"
                role="group"
                aria-label="Plano de stands del Polideportivo Héroes de Octubre"
              >
                <rect x="90" y="60" width="500" height="520" fill="#14120f" />
                <ellipse cx="340" cy="330" rx="245" ry="230" fill="#1e1b16" stroke="#484133" strokeWidth="2" />
                <ellipse cx="340" cy="330" rx="230" ry="215" fill="#28241c" stroke="#544c3c" strokeWidth="1.5" />
                <text x="340" y="114" fill="#c9c4b6" fontSize="9" fontFamily="'JetBrains Mono',monospace" fontWeight="700" letterSpacing="1.5" textAnchor="middle">
                  ESCENARIO / ZONA PREFERENCIAL
                </text>
                <ellipse cx="340" cy="330" rx="210" ry="195" fill="#181511" stroke="#fbf8f2" strokeWidth="2.5" />
                <ellipse cx="340" cy="330" rx="202" ry="187" fill="none" stroke="rgba(255,255,255,0.25)" strokeWidth="1" strokeDasharray="4,4" />
                <rect x="256" y="200" width="168" height="288" rx="5" fill="rgba(0,0,0,0.12)" stroke="#fbf8f2" strokeWidth="1.5" strokeDasharray="4,3" />
                <rect x="258" y="320" width="164" height="20" fill="rgba(0,0,0,0.22)" rx="2" />
                <text x="340" y="333" fill="rgba(255,255,255,0.85)" fontSize="8" fontFamily="'JetBrains Mono',monospace" fontWeight="700" letterSpacing="2" textAnchor="middle">
                  PASILLO
                </text>
                <text x="340" y="156" fill="#ffffff" fontSize="8.5" fontFamily="'JetBrains Mono',monospace" fontWeight="700" letterSpacing="1.5" textAnchor="middle">
                  ▲ ACCESO NORTE ▲
                </text>
                <text x="340" y="555" fill="#e8e4d8" fontSize="8.5" fontFamily="'JetBrains Mono',monospace" fontWeight="700" letterSpacing="1.5" textAnchor="middle">
                  ▼ ACCESO PRINCIPAL SUR ▼
                </text>

                {stands.map((stand) => {
                  const coords = STAND_COORDS[stand.id];
                  if (!coords) return null;
                  const isSelected = stand.id === selectedId;
                  const isDimmed =
                    (filter === 'disponibles' && stand.reserved) ||
                    (filter === 'reservados' && !stand.reserved);

                  return (
                    <g
                      key={stand.id}
                      className={`stand-node ${stand.reserved ? 'reserved' : ''} ${isSelected ? 'active' : ''} ${isDimmed ? 'dimmed' : ''}`}
                      data-id={stand.id}
                      role="button"
                      tabIndex={isDimmed ? -1 : 0}
                      aria-pressed={isSelected}
                      aria-label={`Stand ${stand.id}, ${stand.reserved ? 'reservado' : 'disponible'}, ${stand.size} metros cuadrados`}
                      onKeyDown={(e) => handleStandKeyDown(e, stand.id)}
                    >
                      <rect className="stand-box" x={coords.x} y={coords.y} width="34" height="24" rx="3" />
                      <text className="stand-num" x={coords.tx} y={coords.ty}>
                        {stand.id}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>

            <div className="legend">
              <div className="legend-item">
                <span className="legend-swatch" style={{ background: 'var(--brick)' }} /> Disponible
              </div>
              <div className="legend-item">
                <span className="legend-swatch" style={{ background: 'var(--safety)' }} /> Seleccionado / Activo
              </div>
              <div className="legend-item">
                <span className="legend-swatch" style={{ background: '#333028', border: '1px dashed #544f43' }} /> Reservado
              </div>
            </div>
          </div>

          <div className="stand-info" id="standInfo" aria-live="polite">
            <span className="stand-id">STAND {String(currentStand.id).padStart(2, '0')}</span>
            <h3>{currentStand.sector}</h3>

            <div className="stand-info-row">
              <span className="k">Estado</span>
              <span className="v">
                <span className={`status-pill ${currentStand.reserved ? 'taken' : 'free'}`}>
                  {currentStand.reserved ? 'Reservado' : 'Disponible'}
                </span>
              </span>
            </div>

            <div className="stand-info-row">
              <span className="k">Superficie</span>
              <span className="v">{currentStand.size} m² ({currentStand.dim})</span>
            </div>

            <div className="stand-info-row">
              <span className="k">Tarifa oficial</span>
              <span className="v">$us {PRICE_PER_M2} / m²</span>
            </div>

            <div className="stand-price">
              <span className="lbl">Inversión estimada:</span>
              <span className="amt">$us {estimatedPrice.toLocaleString('es-BO')}</span>
              <span className="cur">Dólares Americanos · Facturado</span>
            </div>

            <div className="stand-includes">
              <h4>Incluye:</h4>
              <ul>
                <li>Estructura modular de aluminio perfil estándar</li>
                <li>Panel de fondo y laterales blancos</li>
                <li>Cenefa con nombre de la empresa</li>
                <li>Iluminación spot LED orientable</li>
                <li>1 punto de toma eléctrica monofásica</li>
                <li>Acreditaciones para personal expositor</li>
                <li>Inclusión en catálogo y directorio web</li>
              </ul>
            </div>

            {currentStand.reserved ? (
              <a
                href={`https://wa.me/${RESERVATIONS_WA}?text=Hola,%20solicito%20entrar%20a%20la%20lista%20de%20espera%20del%20STAND%20${encodeURIComponent(String(currentStand.id).padStart(2, '0'))}%20en%20EXPOINCO%202027`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
              >
                Consultar lista de espera
              </a>
            ) : (
              <button
                type="button"
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                onClick={() => setModalOpen(true)}
              >
                Reservar este Stand
              </button>
            )}
          </div>
        </div>
      </div>

      <ReservaModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        standLabel={String(currentStand.id).padStart(2, '0')}
        standUuid={currentApiStand?.id}
      />
    </section>
  );
}