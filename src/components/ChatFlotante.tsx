import { useEffect, useRef, useState } from 'react';

/**
 * Chat flotante con IA supervisada (Fase 3 — docs/09).
 * Botón flotante + ventana de chat que consulta a la API pública.
 * El asistente informa sobre la expo pero nunca confirma ventas ni precios;
 * siempre deriva la conversación con un ejecutivo de ventas.
 */

const API_URL: string =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/api/v1';

interface Msg {
  rol: 'visitante' | 'asistente';
  contenido: string;
  origen?: 'ia' | 'faq';
}

const SUGERENCIAS = [
  '¿Cuándo es la expo?',
  'Quiero reservar un stand',
  'Espacios para maquinaria pesada',
  '¿Cómo participo como expositor?',
];

const SALUDO: Msg = {
  rol: 'asistente',
  contenido:
    '¡Hola! 👋 Soy el asistente virtual de EXPOINCO 2027. Puedo informarte sobre stands, paquetes, maquinaria pesada y el proceso de reserva. ¿En qué te ayudo?',
};

export default function ChatFlotante() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([SALUDO]);
  const [input, setInput] = useState('');
  const [typing, setTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [msgs, typing, open]);

  const enviar = async (texto: string) => {
    const mensaje = texto.trim();
    if (!mensaje || typing) return;

    const historial = msgs.slice(-8).map((m) => ({ rol: m.rol, contenido: m.contenido }));
    setMsgs((prev) => [...prev, { rol: 'visitante', contenido: mensaje }]);
    setInput('');
    setTyping(true);

    try {
      const res = await fetch(`${API_URL}/public/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje, historial }),
      });
      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = (await res.json()) as { respuesta: string; origen: 'ia' | 'faq' };
      setMsgs((prev) => [...prev, { rol: 'asistente', contenido: data.respuesta, origen: data.origen }]);
    } catch {
      setMsgs((prev) => [
        ...prev,
        {
          rol: 'asistente',
          contenido:
            'No pude conectar con el servicio en este momento. Puedes escribirnos por WhatsApp y un ejecutivo te atenderá. 💬',
        },
      ]);
    } finally {
      setTyping(false);
    }
  };

  return (
    <div style={{ position: 'fixed', left: '20px', bottom: '20px', zIndex: 900 }}>
      {/* Ventana del chat */}
      {open && (
        <div
          style={{
            width: 'min(360px, calc(100vw - 40px))',
            height: 'min(520px, calc(100vh - 120px))',
            marginBottom: '12px',
            background: '#14161c',
            border: '1px solid rgba(255,255,255,0.12)',
            borderRadius: '16px',
            boxShadow: '0 18px 50px rgba(0,0,0,0.45)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* Encabezado */}
          <div
            style={{
              padding: '14px 16px',
              background: 'linear-gradient(135deg, #1c3f2E, #2e7d32)',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <strong style={{ fontSize: '0.95rem' }}>Asistente EXPOINCO</strong>
              <div style={{ fontSize: '0.72rem', opacity: 0.85 }}>
                Consultas sobre stands y la expo
              </div>
            </div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Cerrar chat"
              style={{
                background: 'transparent',
                border: 'none',
                color: '#fff',
                fontSize: '1.25rem',
                cursor: 'pointer',
                lineHeight: 1,
              }}
            >
              ×
            </button>
          </div>

          {/* Mensajes */}
          <div
            ref={scrollRef}
            style={{ flex: 1, overflowY: 'auto', padding: '14px 12px', display: 'flex', flexDirection: 'column', gap: '8px' }}
          >
            {msgs.map((m, i) => (
              <div
                key={i}
                style={{
                  alignSelf: m.rol === 'visitante' ? 'flex-end' : 'flex-start',
                  maxWidth: '85%',
                  padding: '9px 12px',
                  borderRadius: m.rol === 'visitante' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                  background: m.rol === 'visitante' ? '#2e7d32' : '#22252d',
                  color: '#f3f4f6',
                  fontSize: '0.86rem',
                  lineHeight: 1.45,
                  whiteSpace: 'pre-wrap',
                }}
              >
                {m.contenido}
              </div>
            ))}
            {typing && (
              <div
                style={{
                  alignSelf: 'flex-start',
                  padding: '9px 12px',
                  borderRadius: '12px 12px 12px 2px',
                  background: '#22252d',
                  color: '#9ca3af',
                  fontSize: '0.82rem',
                }}
              >
                Escribiendo…
              </div>
            )}
          </div>

          {/* Sugerencias */}
          <div style={{ padding: '0 12px 8px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {SUGERENCIAS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => enviar(s)}
                disabled={typing}
                style={{
                  border: '1px solid rgba(46,125,50,0.5)',
                  background: 'rgba(46,125,50,0.12)',
                  color: '#a5d6a7',
                  borderRadius: '999px',
                  padding: '4px 10px',
                  fontSize: '0.72rem',
                  cursor: 'pointer',
                }}
              >
                {s}
              </button>
            ))}
          </div>

          {/* Entrada */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              enviar(input);
            }}
            style={{ display: 'flex', gap: '8px', padding: '10px 12px', borderTop: '1px solid rgba(255,255,255,0.1)' }}
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu consulta…"
              maxLength={500}
              style={{
                flex: 1,
                background: '#1c1f26',
                border: '1px solid rgba(255,255,255,0.12)',
                borderRadius: '10px',
                padding: '9px 12px',
                color: '#f3f4f6',
                fontSize: '0.86rem',
                outline: 'none',
              }}
            />
            <button
              type="submit"
              disabled={typing || !input.trim()}
              style={{
                background: '#2e7d32',
                border: 'none',
                borderRadius: '10px',
                padding: '9px 14px',
                color: '#fff',
                fontWeight: 600,
                cursor: typing || !input.trim() ? 'default' : 'pointer',
                opacity: typing || !input.trim() ? 0.6 : 1,
              }}
            >
              ➤
            </button>
          </form>
        </div>
      )}

      {/* Botón flotante */}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? 'Cerrar chat' : 'Abrir chat de consultas'}
        style={{
          width: '58px',
          height: '58px',
          borderRadius: '50%',
          border: 'none',
          background: 'linear-gradient(135deg, #2e7d32, #43a047)',
          color: '#fff',
          fontSize: '1.55rem',
          cursor: 'pointer',
          boxShadow: '0 10px 28px rgba(46,125,50,0.45)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {open ? '×' : '💬'}
      </button>
    </div>
  );
}
