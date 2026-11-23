import { useEffect } from 'react';
import { EVENTO_DATOS } from './api';

/**
 * Refresco automático de datos en los paneles (admin/ejecutivo).
 *
 * Vuelve a cargar cuando:
 * - cambia un dato en el sistema (evento EVENTO_DATOS: reservas, ventas…),
 * - la pestaña recupera el foco,
 * - transcurre el intervalo (por defecto 30 s).
 */
export function useAutoRefresh(cargar: () => void, intervaloMs = 30000): void {
  useEffect(() => {
    const alCambiar = () => cargar();
    window.addEventListener(EVENTO_DATOS, alCambiar);
    window.addEventListener('focus', alCambiar);
    document.addEventListener('visibilitychange', alCambiar);
    const intervalo = window.setInterval(alCambiar, intervaloMs);
    return () => {
      window.removeEventListener(EVENTO_DATOS, alCambiar);
      window.removeEventListener('focus', alCambiar);
      document.removeEventListener('visibilitychange', alCambiar);
      window.clearInterval(intervalo);
    };
  }, [cargar, intervaloMs]);
}
