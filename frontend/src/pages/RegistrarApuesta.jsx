import { useState } from "react";
import "../styles/registrar.css";

import { API_URL } from "../config/api";
import SelectorTrackBet from "../components/SelectorTrackBet";

const DEPORTES_REGISTRO = [
  { valor: "basquetbol", etiqueta: "Básquetbol" },
  { valor: "beisbol", etiqueta: "Béisbol" },
  { valor: "boxeo", etiqueta: "Boxeo" },
  { valor: "cricket", etiqueta: "Cricket" },
  { valor: "esports", etiqueta: "eSports" },
  { valor: "futbol", etiqueta: "Fútbol" },
  { valor: "futbol americano", etiqueta: "Fútbol americano" },
  { valor: "golf", etiqueta: "Golf" },
  { valor: "hockey", etiqueta: "Hockey" },
  { valor: "mma / ufc", etiqueta: "MMA / UFC" },
  { valor: "mixto", etiqueta: "Mixto" },
  { valor: "tenis", etiqueta: "Tenis" },
  { valor: "voleibol", etiqueta: "Voleibol" },
  { valor: "otro", etiqueta: "Otro" },
];

const TIPOS_CUOTA = [
  { valor: "americana", etiqueta: "Americana" },
  { valor: "decimal", etiqueta: "Decimal" },
];

function convertirCuotaADecimal(valor, tipo) {
  const texto = String(valor ?? "").trim();

  if (!texto) {
    return null;
  }

  if (tipo === "americana") {
    const cuotaAmericana = Number(texto);

    if (!Number.isFinite(cuotaAmericana) || cuotaAmericana === 0) {
      return null;
    }

    if (cuotaAmericana > 0) {
      return 1 + cuotaAmericana / 100;
    }

    return 1 + 100 / Math.abs(cuotaAmericana);
  }

  if (tipo === "decimal") {
    const cuotaDecimal = Number(texto);

    if (!Number.isFinite(cuotaDecimal) || cuotaDecimal <= 1) {
      return null;
    }

    return cuotaDecimal;
  }

  if (tipo === "fraccional") {
    const partes = texto.split("/");

    if (partes.length !== 2) {
      return null;
    }

    const numerador = Number(partes[0]);
    const denominador = Number(partes[1]);

    if (
      !Number.isFinite(numerador) ||
      !Number.isFinite(denominador) ||
      numerador <= 0 ||
      denominador <= 0
    ) {
      return null;
    }

    return 1 + numerador / denominador;
  }

  return null;
}

function formatoNumero(valor) {
  return new Intl.NumberFormat("es-MX", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(valor);
}

const MOMENTOS_REGISTRO = [
  { valor: "prepartido", etiqueta: "Prepartido" },
  { valor: "en_vivo", etiqueta: "En vivo" },
];

function RegistrarApuesta() {
  const [modalidad, setModalidad] = useState("straight");
  const [casa, setCasa] = useState("");
  const [deporte, setDeporte] = useState("futbol");
  const [liga, setLiga] = useState("");
  const [momento, setMomento] = useState("prepartido");
  const [evento, setEvento] = useState("");
  const [mercado, setMercado] = useState("");
  const [seleccion, setSeleccion] = useState("");
  const [tipoCuota, setTipoCuota] = useState("americana");
  const [cuota, setCuota] = useState("");
  const [seleccionesParlay, setSeleccionesParlay] = useState([
    {
      id: 1,
      deporte: "futbol",
      liga: "",
      evento: "",
      mercado: "",
      seleccion: "",
      tipoCuota: "americana",
      cuota: "",
    },
    {
      id: 2,
      deporte: "futbol",
      liga: "",
      evento: "",
      mercado: "",
      seleccion: "",
      tipoCuota: "americana",
      cuota: "",
    },
  ]);

  const [siguienteIdSeleccion, setSiguienteIdSeleccion] = useState(3);
  function actualizarSeleccionParlay(id, campo, valor) {
    setSeleccionesParlay((seleccionesActuales) =>
      seleccionesActuales.map((seleccionParlay) =>
        seleccionParlay.id === id
          ? {
              ...seleccionParlay,
              [campo]: valor,
            }
          : seleccionParlay,
      ),
    );
  }
  const [stake, setStake] = useState("");

  function agregarSeleccionParlay() {
    setSeleccionesParlay((seleccionesActuales) => [
      ...seleccionesActuales,
      {
        id: siguienteIdSeleccion,
        deporte: "futbol",
        liga: "",
        evento: "",
        mercado: "",
        seleccion: "",
        tipoCuota: "americana",
        cuota: "",
      },
    ]);

    setSiguienteIdSeleccion((idActual) => idActual + 1);
  }

  function eliminarSeleccionParlay(id) {
    setSeleccionesParlay((seleccionesActuales) => {
      if (seleccionesActuales.length <= 2) {
        return seleccionesActuales;
      }

      return seleccionesActuales.filter(
        (seleccionParlay) => seleccionParlay.id !== id,
      );
    });
  }

  const cuotaDecimalPrevia =
    modalidad === "straight"
      ? convertirCuotaADecimal(cuota, tipoCuota)
      : seleccionesParlay.reduce((acumulado, seleccionParlay) => {
          const cuotaSeleccion = convertirCuotaADecimal(
            seleccionParlay.cuota,
            seleccionParlay.tipoCuota,
          );

          if (acumulado === null || cuotaSeleccion === null) {
            return null;
          }

          return acumulado * cuotaSeleccion;
        }, 1);

  const stakeNumerico = Number(stake);

  const retornoEstimado =
    cuotaDecimalPrevia !== null &&
    Number.isFinite(stakeNumerico) &&
    stakeNumerico > 0
      ? stakeNumerico * cuotaDecimalPrevia
      : null;

  const gananciaEstimada =
    retornoEstimado !== null ? retornoEstimado - stakeNumerico : null;
  const [registrando, setRegistrando] = useState(false);
  const [mensajeRegistro, setMensajeRegistro] = useState("");
  const [errorRegistro, setErrorRegistro] = useState("");

  async function registrarApuesta() {
    setMensajeRegistro("");
    setErrorRegistro("");

    const casaLimpia = casa.trim();
    const stakeFinal = Number(stake);

    if (!casaLimpia) {
      setErrorRegistro("Ingresa la casa de apuestas.");
      return;
    }

    if (!Number.isFinite(stakeFinal) || stakeFinal <= 0) {
      setErrorRegistro("Ingresa un stake válido mayor que 0.");
      return;
    }

    let endpoint;
    let datos;

    if (modalidad === "straight") {
      if (
        !liga.trim() ||
        !evento.trim() ||
        !mercado.trim() ||
        !seleccion.trim()
      ) {
        setErrorRegistro("Completa Liga, Evento, Mercado y Selección.");
        return;
      }

      const cuotaFinal = Number(cuota);

      if (
        convertirCuotaADecimal(cuota, tipoCuota) === null ||
        !Number.isFinite(cuotaFinal)
      ) {
        setErrorRegistro("Ingresa una cuota válida.");
        return;
      }

      endpoint = "/apuestas";

      datos = {
        casa: casaLimpia,
        deporte,
        liga: liga.trim(),
        evento: evento.trim(),
        mercado: mercado.trim(),
        seleccion: seleccion.trim(),
        momento_apuesta: momento,
        tipo_cuota: tipoCuota,
        cuota: cuotaFinal,
        stake: stakeFinal,
      };
    } else {
      const parlayIncompleto = seleccionesParlay.some(
        (pierna) =>
          !pierna.deporte ||
          !pierna.liga.trim() ||
          !pierna.evento.trim() ||
          !pierna.mercado.trim() ||
          !pierna.seleccion.trim() ||
          convertirCuotaADecimal(pierna.cuota, pierna.tipoCuota) === null,
      );

      if (parlayIncompleto) {
        setErrorRegistro(
          "Completa todos los datos y cuotas de las selecciones del parlay.",
        );
        return;
      }

      if (cuotaDecimalPrevia === null) {
        setErrorRegistro("No se pudo calcular la cuota combinada del parlay.");
        return;
      }

      endpoint = "/apuestas/parlay";

      datos = {
        casa: casaLimpia,
        momento_apuesta: momento,

        selecciones: seleccionesParlay.map((pierna) => ({
          deporte: pierna.deporte,
          liga: pierna.liga.trim(),
          evento: pierna.evento.trim(),
          mercado: pierna.mercado.trim(),
          seleccion: pierna.seleccion.trim(),
          tipo_cuota: pierna.tipoCuota,
          cuota: Number(pierna.cuota),
        })),

        tipo_cuota: "decimal",
        cuota: cuotaDecimalPrevia,
        stake: stakeFinal,
      };
    }

    try {
      setRegistrando(true);

      const respuesta = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(datos),
      });

      const respuestaDatos = await respuesta.json();

      if (!respuesta.ok) {
        const detalle = respuestaDatos?.detail;

        if (typeof detalle === "string") {
          throw new Error(detalle);
        }

        throw new Error(
          "La API rechazó la apuesta. Revisa los datos ingresados.",
        );
      }

      setMensajeRegistro(
        `Apuesta registrada correctamente. ID: ${respuestaDatos.id}`,
      );
    } catch (errorCapturado) {
      setErrorRegistro(
        errorCapturado instanceof Error
          ? errorCapturado.message
          : "No se pudo registrar la apuesta.",
      );
    } finally {
      setRegistrando(false);
    }
  }

  return (
    <main className="pagina pagina-registro">
      <div className="registro-contenedor">
        <header className="cabecera-registro">
          <p className="marca">TRACKBET</p>

          <h1 className="titulo-gradient">Registrar apuesta</h1>

          <p className="subtitulo">
            Registra cada jugada y mantén tu rendimiento bajo control.
          </p>
        </header>

        <section className="bloque-registro bloque-modalidad">
          <div className="encabezado-bloque-registro">
            <div>
              <span className="codigo-registro">TB · NUEVA APUESTA</span>
              <h2>Tipo de apuesta</h2>
            </div>

            <span className="estado-registro">Paso 1</span>
          </div>

          <div className="selector-modalidad">
            <button
              type="button"
              className={
                modalidad === "straight"
                  ? "opcion-modalidad activa"
                  : "opcion-modalidad"
              }
              onClick={() => setModalidad("straight")}
            >
              <span className="numero-modalidad">01</span>

              <span>
                <strong>Straight</strong>
                <small>Apuesta individual</small>
              </span>
            </button>

            <button
              type="button"
              className={
                modalidad === "parlay"
                  ? "opcion-modalidad activa"
                  : "opcion-modalidad"
              }
              onClick={() => setModalidad("parlay")}
            >
              <span className="numero-modalidad">02</span>

              <span>
                <strong>Parlay</strong>
                <small>Múltiples selecciones</small>
              </span>
            </button>
          </div>
        </section>
        <section className="bloque-registro bloque-datos-generales">
          <div className="encabezado-bloque-registro">
            <div>
              <span className="codigo-registro">TB · DATOS GENERALES</span>

              <h2>Información de la apuesta</h2>
            </div>

            <span className="estado-registro">Paso 2</span>
          </div>

          <div className="grid-datos-generales">
            <label className="campo-registro">
              <span>Casa de apuestas</span>

              <input
                type="text"
                value={casa}
                onChange={(evento) => setCasa(evento.target.value)}
                placeholder="Ej. Stake, Caliente, Playdoit..."
              />
            </label>

            {modalidad === "straight" && (
              <div className="campo-registro">
                <span>Deporte</span>

                <SelectorTrackBet
                  value={deporte}
                  onChange={setDeporte}
                  opciones={DEPORTES_REGISTRO}
                  ariaLabel="Seleccionar deporte"
                />
              </div>
            )}

            {modalidad === "straight" && (
              <label className="campo-registro">
                <span>Liga</span>

                <input
                  type="text"
                  value={liga}
                  onChange={(evento) => setLiga(evento.target.value)}
                  placeholder="Ej. Liga MX, MLB, NFL..."
                />
              </label>
            )}

            <div className="campo-registro">
              <span>Momento</span>

              <SelectorTrackBet
                value={momento}
                onChange={setMomento}
                opciones={MOMENTOS_REGISTRO}
                ariaLabel="Seleccionar momento"
              />
            </div>
          </div>
        </section>

        {modalidad === "straight" && (
          <section className="bloque-registro bloque-detalle-apuesta">
            <div className="encabezado-bloque-registro">
              <div>
                <span className="codigo-registro">TB · STRAIGHT</span>

                <h2>Detalles de la selección</h2>
              </div>

              <span className="estado-registro">Paso 3</span>
            </div>

            <div className="grid-detalle-straight">
              <label className="campo-registro campo-evento">
                <span>Evento</span>

                <input
                  type="text"
                  value={evento}
                  onChange={(eventoInput) =>
                    setEvento(eventoInput.target.value)
                  }
                  placeholder="Ej. México vs Argentina"
                />
              </label>

              <label className="campo-registro">
                <span>Mercado</span>

                <input
                  type="text"
                  value={mercado}
                  onChange={(eventoInput) =>
                    setMercado(eventoInput.target.value)
                  }
                  placeholder="Ej. Moneyline, Over/Under..."
                />
              </label>

              <label className="campo-registro">
                <span>Selección</span>

                <input
                  type="text"
                  value={seleccion}
                  onChange={(eventoInput) =>
                    setSeleccion(eventoInput.target.value)
                  }
                  placeholder="Ej. México, Over 2.5..."
                />
              </label>

              <div className="campo-registro">
                <span>Tipo de cuota</span>

                <SelectorTrackBet
                  value={tipoCuota}
                  onChange={setTipoCuota}
                  opciones={TIPOS_CUOTA}
                  ariaLabel="Seleccionar tipo de cuota"
                />
              </div>

              <label className="campo-registro campo-cuota">
                <span>Cuota</span>

                <input
                  type="text"
                  inputMode={tipoCuota === "fraccional" ? "text" : "decimal"}
                  value={cuota}
                  onChange={(eventoInput) => setCuota(eventoInput.target.value)}
                  placeholder={
                    tipoCuota === "americana"
                      ? "Ej. -118 o +150"
                      : tipoCuota === "decimal"
                        ? "Ej. 1.85"
                        : "Ej. 5/2"
                  }
                />
              </label>
            </div>
          </section>
        )}

        {modalidad === "parlay" && (
          <section className="bloque-registro bloque-parlay">
            <div className="encabezado-bloque-registro">
              <div>
                <span className="codigo-registro">TB · PARLAY BUILDER</span>

                <h2>Construye tu parlay</h2>
              </div>

              <span className="estado-registro">Paso 3</span>
            </div>

            <div className="lista-selecciones-parlay">
              {seleccionesParlay.map((seleccionParlay, indice) => (
                <article
                  className="seleccion-parlay-registro"
                  key={seleccionParlay.id}
                >
                  <div className="cabecera-seleccion-parlay">
                    <div className="identificador-seleccion-parlay">
                      <span>{indice + 1}</span>

                      <div>
                        <strong>Selección {indice + 1}</strong>

                        <small>Pierna del parlay</small>
                      </div>
                    </div>

                    {seleccionesParlay.length > 2 && (
                      <button
                        type="button"
                        className="boton-eliminar-seleccion"
                        onClick={() =>
                          eliminarSeleccionParlay(seleccionParlay.id)
                        }
                      >
                        Eliminar
                      </button>
                    )}
                  </div>

                  <div className="grid-seleccion-parlay">
                    <div className="campo-registro">
                      <span>Deporte</span>

                      <SelectorTrackBet
                        value={seleccionParlay.deporte}
                        onChange={(valor) =>
                          actualizarSeleccionParlay(
                            seleccionParlay.id,
                            "deporte",
                            valor,
                          )
                        }
                        opciones={DEPORTES_REGISTRO}
                        ariaLabel={`Seleccionar deporte de la selección ${indice + 1}`}
                      />
                    </div>

                    <label className="campo-registro">
                      <span>Liga</span>

                      <input
                        type="text"
                        value={seleccionParlay.liga}
                        onChange={(eventoInput) =>
                          actualizarSeleccionParlay(
                            seleccionParlay.id,
                            "liga",
                            eventoInput.target.value,
                          )
                        }
                        placeholder="Ej. Liga MX, MLB..."
                      />
                    </label>

                    <label className="campo-registro campo-evento-parlay">
                      <span>Evento</span>

                      <input
                        type="text"
                        value={seleccionParlay.evento}
                        onChange={(eventoInput) =>
                          actualizarSeleccionParlay(
                            seleccionParlay.id,
                            "evento",
                            eventoInput.target.value,
                          )
                        }
                        placeholder="Ej. México vs Argentina"
                      />
                    </label>

                    <label className="campo-registro">
                      <span>Mercado</span>

                      <input
                        type="text"
                        value={seleccionParlay.mercado}
                        onChange={(eventoInput) =>
                          actualizarSeleccionParlay(
                            seleccionParlay.id,
                            "mercado",
                            eventoInput.target.value,
                          )
                        }
                        placeholder="Ej. Moneyline, Total..."
                      />
                    </label>

                    <label className="campo-registro">
                      <span>Selección</span>

                      <input
                        type="text"
                        value={seleccionParlay.seleccion}
                        onChange={(eventoInput) =>
                          actualizarSeleccionParlay(
                            seleccionParlay.id,
                            "seleccion",
                            eventoInput.target.value,
                          )
                        }
                        placeholder="Ej. México, Over 2.5..."
                      />
                    </label>

                    <div className="campo-registro">
                      <span>Tipo de cuota</span>

                      <SelectorTrackBet
                        value={seleccionParlay.tipoCuota}
                        onChange={(valor) =>
                          actualizarSeleccionParlay(
                            seleccionParlay.id,
                            "tipoCuota",
                            valor,
                          )
                        }
                        opciones={TIPOS_CUOTA}
                        ariaLabel={`Seleccionar tipo de cuota de la selección ${indice + 1}`}
                      />
                    </div>

                    <label className="campo-registro">
                      <span>Cuota</span>

                      <input
                        type="text"
                        value={seleccionParlay.cuota}
                        onChange={(eventoInput) =>
                          actualizarSeleccionParlay(
                            seleccionParlay.id,
                            "cuota",
                            eventoInput.target.value,
                          )
                        }
                        placeholder={
                          seleccionParlay.tipoCuota === "americana"
                            ? "Ej. -110 o +135"
                            : seleccionParlay.tipoCuota === "decimal"
                              ? "Ej. 1.91"
                              : "Ej. 10/11"
                        }
                      />
                    </label>
                  </div>
                </article>
              ))}
            </div>

            <button
              type="button"
              className="boton-agregar-seleccion"
              onClick={agregarSeleccionParlay}
            >
              + Añadir selección
            </button>
          </section>
        )}

        <section className="bloque-registro bloque-resumen-registro">
          <div className="encabezado-bloque-registro">
            <div>
              <span className="codigo-registro">TB · CAPITAL</span>

              <h2>Stake y resumen</h2>
            </div>

            <span className="estado-registro">Paso 4</span>
          </div>

          <div className="zona-stake-registro">
            <label className="campo-registro campo-stake">
              <span>Stake</span>

              <div className="input-dinero-registro">
                <span>$</span>

                <input
                  type="number"
                  inputMode="decimal"
                  min="0"
                  step="0.01"
                  value={stake}
                  onChange={(evento) => setStake(evento.target.value)}
                  placeholder="0.00"
                />
              </div>
            </label>

            <div className="resumen-previo-registro">
              <div className="metrica-resumen-registro">
                <span>Modalidad</span>

                <strong>
                  {modalidad === "straight" ? "Straight" : "Parlay"}
                </strong>
              </div>

              <div className="metrica-resumen-registro">
                <span>
                  {modalidad === "straight"
                    ? "Cuota decimal"
                    : "Cuota combinada"}
                </span>

                <strong>
                  {cuotaDecimalPrevia !== null
                    ? formatoNumero(cuotaDecimalPrevia)
                    : "—"}
                </strong>
              </div>

              <div className="metrica-resumen-registro">
                <span>Retorno estimado</span>

                <strong className="valor-retorno-registro">
                  {retornoEstimado !== null
                    ? `$${formatoNumero(retornoEstimado)}`
                    : "—"}
                </strong>
              </div>

              <div className="metrica-resumen-registro">
                <span>Ganancia potencial</span>

                <strong className="valor-ganancia-registro">
                  {gananciaEstimada !== null
                    ? `+$${formatoNumero(gananciaEstimada)}`
                    : "—"}
                </strong>
              </div>
            </div>
          </div>
        </section>
        <section className="acciones-registro">
          {errorRegistro && (
            <div className="mensaje-registro mensaje-registro-error">
              {errorRegistro}
            </div>
          )}

          {mensajeRegistro && (
            <div className="mensaje-registro mensaje-registro-exito">
              {mensajeRegistro}
            </div>
          )}

          <button
            type="button"
            className="boton-registrar-apuesta"
            onClick={registrarApuesta}
            disabled={registrando}
          >
            {registrando ? "Registrando apuesta..." : "Registrar apuesta"}
          </button>
        </section>
      </div>
    </main>
  );
}

export default RegistrarApuesta;
