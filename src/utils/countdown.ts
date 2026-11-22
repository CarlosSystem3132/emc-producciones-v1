/**
 * Inicio oficial de la expo: 21 de abril de 2027, 09:00 hora de Bolivia (UTC-4).
 * Se usa formato ISO con offset para que el resultado sea idéntico en cualquier
 * zona horaria y navegador (el formato "April 21, 2027" depende del navegador).
 */
export const EXPO_START = new Date('2027-04-21T09:00:00-04:00').getTime();

interface CountdownIds {
  days: string;
  hours: string;
  mins: string;
  secs: string;
}

const pad = (n: number) => String(n).padStart(2, '0');

function setText(id: string, value: string) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

/** Inicia una cuenta regresiva y la detiene sola al llegar a cero. */
export function startCountdown(ids: CountdownIds, onEnd?: () => void) {
  let timer: number | undefined;

  const tick = () => {
    const diff = Math.max(0, EXPO_START - Date.now());

    setText(ids.days, pad(Math.floor(diff / 86_400_000)));
    setText(ids.hours, pad(Math.floor((diff % 86_400_000) / 3_600_000)));
    setText(ids.mins, pad(Math.floor((diff % 3_600_000) / 60_000)));
    setText(ids.secs, pad(Math.floor((diff % 60_000) / 1000)));

    if (diff === 0) {
      if (timer !== undefined) window.clearInterval(timer);
      onEnd?.();
    }
  };

  tick();
  timer = window.setInterval(tick, 1000);
}
