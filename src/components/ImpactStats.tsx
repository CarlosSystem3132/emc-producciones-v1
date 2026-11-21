import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

const STATS = [
  { target: 150, suffix: '+', label: 'Empresas Expositoras' },
  { target: 25, suffix: '.000+', label: 'Visitantes Estimados' },
  { target: 52, suffix: '', label: 'Stands Comerciales' },
  { target: 4, suffix: '', label: 'Sedes Internacionales' },
];

const DURATION_MS = 1600;

function AnimatedCounter({ target, suffix }: { target: number; suffix: string }) {
  const [count, setCount] = useState(0);
  const startedRef = useRef(false);
  const frameRef = useRef<number | null>(null);

  // Cancela la animación si el componente se desmonta a mitad de camino
  useEffect(() => {
    return () => {
      if (frameRef.current !== null) cancelAnimationFrame(frameRef.current);
    };
  }, []);

  const start = () => {
    if (startedRef.current) return;
    startedRef.current = true;

    // Respeta "reducir movimiento": muestra el número final sin animar
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setCount(target);
      return;
    }

    const startTime = performance.now();

    const update = (now: number) => {
      const progress = Math.min((now - startTime) / DURATION_MS, 1);
      const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      setCount(Math.floor(eased * target));
      frameRef.current = progress < 1 ? requestAnimationFrame(update) : null;
    };

    frameRef.current = requestAnimationFrame(update);
  };

  return (
    <motion.span
      className="stat-num-row"
      viewport={{ once: true, amount: 0.3 }}
      onViewportEnter={start}
    >
      <span className="stat-counter">
        {count.toLocaleString('es-BO')}
      </span>
      {suffix && (
        <span className="stat-plus">{suffix}</span>
      )}
    </motion.span>
  );
}

export default function ImpactStats() {
  return (
    <div className="impact-stats-strip">
      {STATS.map((stat) => (
        <div className="stat-box" key={stat.label}>
          <AnimatedCounter target={stat.target} suffix={stat.suffix} />
          <div className="stat-label">{stat.label}</div>
        </div>
      ))}
    </div>
  );
}
