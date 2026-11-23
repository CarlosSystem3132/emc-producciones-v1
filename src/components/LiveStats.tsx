import { useEffect, useState } from 'react';
import { fetchPlano, EVENTO_DATOS } from '../lib/api';
import type { PlanoResponse } from '../lib/api';

/**
 * Contador de ocupación en vivo (quick win 1 — INFORME.md §11).
 * Prueba social con datos reales del inventario: stands vendidos/reservados,
 * disponibles y canchas de maquinaria. Actualiza al montar el componente.
 */
export default function LiveStats() {
  const [stats, setStats] = useState<{
    total: number;
    ocupados: number;
    disponibles: number;
    canchasDisponibles: number;
  } | null>(null);
  const [errorApi, setErrorApi] = useState(false);

  // Refresco en vivo: al montar, cuando cambian datos (EVENTO_DATOS), al
  // recuperar el foco y cada 60 s — las ventas se reflejan sin recargar.
  useEffect(() => {
    let cancelled = false;
    const cargar = () => {
      fetchPlano()
        .then((plano: PlanoResponse) => {
          if (cancelled) return;
          const stands = plano.stands;
          const ocupados = stands.filter((s) => s.estado === 'vendido' || s.estado === 'reservado').length;
          const canchas = stands.filter((s) => s.tipo === 'cancha');
          setStats({
            total: stands.length,
            ocupados,
            disponibles: stands.filter((s) => s.estado === 'disponible').length,
            canchasDisponibles: canchas.filter((s) => s.estado === 'disponible').length,
          });
          setErrorApi(false);
        })
        .catch(() => {
          if (!cancelled) setErrorApi(true);
        });
    };

    cargar();
    window.addEventListener(EVENTO_DATOS, cargar);
    window.addEventListener('focus', cargar);
    const intervalo = window.setInterval(cargar, 60000);
    return () => {
      cancelled = true;
      window.removeEventListener(EVENTO_DATOS, cargar);
      window.removeEventListener('focus', cargar);
      window.clearInterval(intervalo);
    };
  }, []);

  if (errorApi && !stats) {
    return (
      <section className="live-stats" aria-label="Estado de conexión">
        <div className="wrap live-stats-row">
          <div className="live-stats-badge">
            <span className="live-stats-pulse" aria-hidden="true" /> Sin conexión con el servidor
          </div>
          <div className="live-stats-numbers">
            <span>⚠️ No se pudo cargar la disponibilidad en este momento.</span>
          </div>
        </div>
      </section>
    );
  }

  if (!stats) return null;

  const porcentaje = Math.round((100 * stats.ocupados) / Math.max(stats.total, 1));

  return (
    <section className="live-stats" aria-label="Disponibilidad de stands en tiempo real">
      <div className="wrap live-stats-row">
        <div className="live-stats-badge">
          <span className="live-stats-pulse" aria-hidden="true" />
          Disponibilidad en tiempo real
        </div>
        <div className="live-stats-numbers">
          <span>
            🔥 <strong>{stats.ocupados}</strong> de <strong>{stats.total}</strong> stands
            ocupados ({porcentaje}%)
          </span>
          <span>
            ✅ <strong>{stats.disponibles}</strong> stands disponibles
          </span>
          <span>
            🏗️ <strong>{stats.canchasDisponibles}</strong> canchas de maquinaria libres
          </span>
        </div>
        <a href="#plano" className="btn btn-primary live-stats-cta">
          Ver plano y reservar
        </a>
      </div>
    </section>
  );
}
