import { useState } from "react";
const ETIQUETAS_RESULTADO = {
  ganada: "Ganada",
  perdida: "Perdida",
  pendiente: "Pendiente",
  push: "Push",
};

function obtenerTextoCuota(apuesta) {
  if (apuesta.cuota_texto) {
    return apuesta.cuota_texto;
  }

  const cuota = Number(apuesta.cuota);

  if (Number.isFinite(cuota)) {
    return cuota.toFixed(2);
  }

  return "Sin cuota";
}

function formatearTexto(valor) {
  if (!valor) {
    return "No especificado";
  }

  const texto = String(valor).replace(/_/g, " ").trim();

  return texto.charAt(0).toUpperCase() + texto.slice(1);
}

function TicketHistorial({ apuesta, numeroApuesta, formatoDinero }) {
  const [detallesAbiertos, setDetallesAbiertos] = useState(false);
  const resultado = String(apuesta.resultado || "pendiente").toLowerCase();

  const modalidad = String(apuesta.modalidad || "straight").toLowerCase();

  const selecciones = Array.isArray(apuesta.selecciones)
    ? apuesta.selecciones
    : [];

  const esParlay = modalidad === "parlay" || selecciones.length > 1;
  const seleccionPrincipal =
    apuesta.seleccion || apuesta.selecciones?.[0]?.seleccion || "";

  const eventoPrincipal =
    apuesta.evento || apuesta.selecciones?.[0]?.evento || "";

  return (
    <article className={`ticket-historial resultado-${resultado}`}>
      <header className="ticket-historial-encabezado">
        <div>
          <span className="ticket-historial-id">Apuesta {numeroApuesta}</span>

          <h2>
            {esParlay
              ? `Parlay de ${selecciones.length} selecciones`
              : "Straight bet"}
          </h2>
        </div>

        <span className={`estado-apuesta estado-${resultado}`}>
          {ETIQUETAS_RESULTADO[resultado] || resultado}
        </span>
      </header>

      <div className="ticket-historial-contenido">
        <div className="ticket-historial-principal">
          <div className="datos-apuesta">
            <div>
              <span>Casa</span>
              <strong>{apuesta.casa || "Sin especificar"}</strong>
            </div>

            <div>
              <span>Deporte</span>
              <strong>{apuesta.deporte || "Sin especificar"}</strong>
            </div>

            <div>
              <span>Liga</span>
              <strong>{apuesta.liga || "Sin especificar"}</strong>
            </div>

            <div>
              <span>Fecha</span>
              <strong>{apuesta.fecha || "Sin fecha"}</strong>
            </div>
          </div>

          {!esParlay && (
            <div className="seleccion-straight">
              <span>Selección</span>

              <strong>{seleccionPrincipal || "Sin selección"}</strong>
            </div>
          )}

          {esParlay && (
            <ol className="selecciones-historial">
              {selecciones.map((seleccion, indice) => (
                <li key={`${apuesta.id}-${indice}`}>
                  <span className="numero-seleccion">{indice + 1}</span>

                  <div>
                    <strong>
                      {seleccion.seleccion ||
                        seleccion.tipo_apuesta ||
                        "Selección"}
                    </strong>

                    <span>{seleccion.evento || "Evento sin especificar"}</span>
                  </div>

                  <span className="cuota-seleccion">
                    {seleccion.cuota_texto_individual ||
                      seleccion.cuota_individual ||
                      "—"}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </div>

        <aside className="ticket-historial-finanzas">
          <div>
            <span>Stake</span>
            <strong>{formatoDinero.format(Number(apuesta.stake) || 0)}</strong>
          </div>

          <div>
            <span>Cuota</span>
            <strong>{obtenerTextoCuota(apuesta)}</strong>
          </div>

          <div>
            <span>Modalidad</span>
            <strong>{esParlay ? "Parlay" : "Straight"}</strong>
          </div>
        </aside>
      </div>
      {detallesAbiertos && (
        <section className="detalles-apuesta-expandida">
          <div className="detalle-expandido">
            <span>ID de apuesta</span>
            <strong>#{apuesta.id}</strong>
          </div>

          <div className="detalle-expandido">
            <span>Momento</span>
            <strong>{formatearTexto(apuesta.momento_apuesta)}</strong>
          </div>

          <div className="detalle-expandido">
            <span>Tipo de cuota</span>
            <strong>{formatearTexto(apuesta.tipo_cuota)}</strong>
          </div>

          <div className="detalle-expandido">
            <span>Cuota registrada</span>
            <strong>
              {apuesta.cuota_texto || apuesta.cuota || "No especificada"}
            </strong>
          </div>

          <div className="detalle-expandido detalle-evento">
            <span>Evento</span>
            <strong>{eventoPrincipal || "No especificado"}</strong>
          </div>

          <div className="detalle-expandido">
            <span>Resultado</span>
            <strong>{ETIQUETAS_RESULTADO[resultado] || resultado}</strong>
          </div>
        </section>
      )}
      <div className="acciones-ticket-historial">
        <button
          type="button"
          className="boton-detalles-apuesta"
          onClick={() => setDetallesAbiertos((estadoActual) => !estadoActual)}
          aria-expanded={detallesAbiertos}
        >
          {detallesAbiertos ? "Ocultar detalles" : "Ver detalles"}

          <span
            className={
              detallesAbiertos ? "flecha-detalles abierta" : "flecha-detalles"
            }
          >
            ↓
          </span>
        </button>
      </div>
    </article>
  );
}

export default TicketHistorial;
