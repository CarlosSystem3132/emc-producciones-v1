/**
 * Atribución de marketing (quick win 2 — INFORME.md §11).
 *
 * - Captura parámetros UTM y click ids (gclid, fbclid) de la URL en el primer
 *   toque y los conserva en localStorage (atribución de primer contacto).
 * - `getFuente()` devuelve una cadena compacta (≤50 chars) que el backend
 *   guarda como `origen` del lead/empresa.
 * - `track()` dispara eventos a Meta Pixel / Google (gtag) si están instalados.
 */

const STORAGE_KEY = 'emc_fuente';

function leerUTM(): string | null {
  if (typeof window === 'undefined') return null;
  const params = new URLSearchParams(window.location.search);

  const source = params.get('utm_source');
  const medium = params.get('utm_medium');
  const campaign = params.get('utm_campaign');
  const gclid = params.get('gclid');
  const fbclid = params.get('fbclid');

  let fuente: string | null = null;
  if (source) {
    fuente = [source, medium, campaign].filter(Boolean).join('/');
  } else if (gclid) {
    fuente = 'google/cpc';
  } else if (fbclid) {
    fuente = 'meta/cpc';
  }
  return fuente ? fuente.slice(0, 50) : null;
}

/** Captura la fuente de la URL (primer toque) y la conserva. */
export function capturarUTM(): void {
  if (typeof window === 'undefined') return;
  try {
    const existente = window.localStorage.getItem(STORAGE_KEY);
    const nueva = leerUTM();
    if (nueva && !existente) {
      window.localStorage.setItem(STORAGE_KEY, nueva);
    }
  } catch {
    // almacenamiento no disponible: la atribución simplemente se omite
  }
}

/** Fuente compacta para los formularios (p. ej. "meta/cpc/verano27"). */
export function getFuente(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    return window.localStorage.getItem(STORAGE_KEY) ?? leerUTM();
  } catch {
    return leerUTM();
  }
}

type VentanaAnalitica = Window & {
  gtag?: (...args: unknown[]) => void;
  fbq?: (...args: unknown[]) => void;
};

/** Registra un evento de marketing si Meta Pixel / Google (gtag) están cargados. */
export function track(evento: string, datos: Record<string, unknown> = {}): void {
  if (typeof window === 'undefined') return;
  const w = window as VentanaAnalitica;
  try {
    if (typeof w.gtag === 'function') {
      w.gtag('event', evento, { ...datos, source: getFuente() ?? 'directo' });
    }
    if (typeof w.fbq === 'function') {
      w.fbq('track', evento, { ...datos, source: getFuente() ?? 'directo' });
    }
  } catch {
    // la analítica nunca debe romper la experiencia
  }
}
