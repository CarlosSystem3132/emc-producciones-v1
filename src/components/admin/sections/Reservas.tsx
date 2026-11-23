import { useCallback, useEffect, useState } from 'react';
import { useAutoRefresh } from '../../../lib/useAutoRefresh';
import { api, fecha, money, ApiError } from '../../../lib/adminApi';
import type { ListResponse, Reserva } from '../../../lib/adminApi';

const ESTADOS: Reserva['estado'][] = ['bloqueado', 'reservado', 'vendido', 'expirado', 'cancelado'];

export default function Reservas() {
  const [items, setItems] = useState<Reserva[]>([]);
  const [total, setTotal] = useState(0);
  const [estado, setEstado] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (estado) params.set('estado', estado);
      const res = await api.get<ListResponse<Reserva>>(`/reservas?${params}`);
      setItems(res.items);
      setTotal(res.total);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar');
    }
  }, [estado]);

  useEffect(() => {
    load();
  }, [load]);
  useAutoRefresh(load); // refresco automático al cambiar datos

  const run = async (fn: () => Promise<unknown>, msg: string) => {
    try {
      await fn();
      setInfo(msg);
      setError(null);
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Error en la operación');
      setInfo(null);
    }
  };

  const extender = (r: Reserva) => {
    const motivo = prompt('Motivo de la extensión (negociación activa):');
    if (!motivo) return;
    const minutos = confirm('Aceptar = 30 minutos · Cancelar = 60 minutos') ? 30 : 60;
    run(() => api.post(`/reservas/${r.id}/extender`, { minutos, motivo }), `Reserva extendida ${minutos} min.`);
  };

  const vender = (r: Reserva) => {
    const monto = prompt('Monto de la venta (USD):');
    if (!monto || isNaN(Number(monto))) return;
    run(() => api.post(`/reservas/${r.id}/vender`, { monto: Number(monto) }), 'Venta registrada.');
  };

  // ---- Fase 4: pagos, firma digital y facturación ----

  const registrarPago = (r: Reserva) => {
    const monto = prompt('Monto del pago (USD):');
    if (!monto || isNaN(Number(monto))) return;
    const metodo = prompt('Método (efectivo / transferencia / qr / tarjeta / otro):', 'transferencia') ?? 'efectivo';
    const referencia = prompt('Referencia / comprobante (opcional):');
    run(
      () => api.post(`/reservas/${r.id}/pagos`, {
        monto: Number(monto),
        metodo: metodo.trim() || 'efectivo',
        referencia: referencia || null,
      }),
      'Pago registrado (pendiente de confirmación).',
    );
  };

  const solicitarFirma = (r: Reserva) => {
    const nombre = prompt('Nombre del firmante:');
    if (!nombre) return;
    const email = prompt('Correo del firmante (opcional):');
    api
      .post<{ url_publica: string }>(`/reservas/${r.id}/firmas`, {
        firmante_nombre: nombre,
        firmante_email: email || null,
      })
      .then((res) => {
        setInfo(`✍️ Solicitud de firma creada. Enlace para el cliente: ${res.url_publica}`);
        setError(null);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Error al solicitar firma'));
  };

  const facturar = (r: Reserva) => {
    const nit = prompt('NIT del cliente:');
    if (!nit) return;
    const razon = prompt('Razón social:');
    api
      .post<{ numero: string }>('/facturas', {
        reserva_id: r.id,
        nit,
        razon_social: razon || null,
      })
      .then((res) => {
        setInfo(`🧾 Factura ${res.numero} creada (borrador). Edítala en Reportes/Facturación.`);
        setError(null);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : 'Error al facturar'));
  };

  return (
    <div className="admin-section">
      <header className="admin-section-head">
        <h2>Reservas</h2>
        <p>{total} reserva(s). Bloqueos temporales, reservas y ventas.</p>
      </header>

      <div className="admin-toolbar">
        <select className="admin-input" value={estado} onChange={(e) => setEstado(e.target.value)}>
          <option value="">Todos los estados</option>
          {ESTADOS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <button type="button" className="btn" onClick={() => run(() => api.post('/reservas/liberar-expiradas'), 'Expirados liberados.')}>
          Liberar expirados
        </button>
      </div>

      {error && <p className="reserva-error">⚠️ {error}</p>}
      {info && <p className="admin-ok">✅ {info}</p>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Reserva</th>
              <th>Stand</th>
              <th>Estado</th>
              <th>Creada</th>
              <th>Expira</th>
              <th>Monto</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {items.map((r) => (
              <tr key={r.id}>
                <td title={r.id}>{r.id.slice(0, 8)}…</td>
                <td>{r.stand_id.slice(0, 8)}…</td>
                <td><span className={`admin-pill estado-${r.estado}`}>{r.estado}</span></td>
                <td>{fecha(r.created_at)}</td>
                <td>
                  {fecha(r.fecha_expiracion)}
                  {r.fecha_extension && <small className="admin-muted"> (extendida)</small>}
                </td>
                <td>{money(r.monto)}</td>
                <td className="admin-actions">
                  {r.estado === 'bloqueado' && (
                    <>
                      <button type="button" className="admin-btn-mini" onClick={() => run(() => api.post(`/reservas/${r.id}/confirmar`), 'Reserva confirmada.')}>
                        Confirmar
                      </button>
                      <button type="button" className="admin-btn-mini" onClick={() => extender(r)}>
                        Extender
                      </button>
                    </>
                  )}
                  {(r.estado === 'bloqueado' || r.estado === 'reservado') && (
                    <>
                      <button type="button" className="admin-btn-mini success" onClick={() => vender(r)}>
                        Vender
                      </button>
                      <button type="button" className="admin-btn-mini danger" onClick={() => run(() => api.post(`/reservas/${r.id}/cancelar`), 'Reserva cancelada.')}>
                        Cancelar
                      </button>
                    </>
                  )}
                  {r.estado !== 'expirado' && r.estado !== 'cancelado' && (
                    <button type="button" className="admin-btn-mini" onClick={() => registrarPago(r)}>
                      Pago
                    </button>
                  )}
                  {(r.estado === 'reservado' || r.estado === 'vendido') && (
                    <>
                      <button type="button" className="admin-btn-mini" onClick={() => solicitarFirma(r)}>
                        Firma
                      </button>
                      <button type="button" className="admin-btn-mini" onClick={() => facturar(r)}>
                        Factura
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr><td colSpan={7} className="admin-muted">Sin reservas.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
