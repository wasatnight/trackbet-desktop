import { useEffect, useMemo, useState } from "react";

import TicketHistorial from "../components/TicketHistorial";
import { obtenerApuestas } from "../services/apuestas";
import "../styles/historial.css";
import SelectorTrackBet from "../components/SelectorTrackBet";

const formatoDinero = new Intl.NumberFormat("es-MX", {
  style: "currency",
  currency: "MXN",
  minimumFractionDigits: 2,
});

const APUESTAS_POR_PAGINA = 5;
const DEPORTES_FILTRO = [
  { valor: "todos", etiqueta: "Todos" },
  { valor: "basquetbol", etiqueta: "Básquetbol" },
  { valor: "beisbol", etiqueta: "Béisbol" },
  { valor: "boxeo", etiqueta: "Boxeo" },
  { valor: "cricket", etiqueta: "Cricket" },
  { valor: "esports", etiqueta: "eSports" },
  { valor: "futbol", etiqueta: "Fútbol" },
  {
    valor: "futbol americano",
    etiqueta: "Fútbol americano",
  },
  { valor: "golf", etiqueta: "Golf" },
  { valor: "hockey", etiqueta: "Hockey" },
  { valor: "mma", etiqueta: "MMA / UFC" },
  { valor: "mixto", etiqueta: "Mixto" },
  { valor: "tenis", etiqueta: "Tenis" },
  { valor: "voleibol", etiqueta: "Voleibol" },
  { valor: "otro", etiqueta: "Otro" },
];
const RESULTADOS_FILTRO = [
  { valor: "todas", etiqueta: "Todas" },
  { valor: "ganada", etiqueta: "Ganadas" },
  { valor: "perdida", etiqueta: "Perdidas" },
  { valor: "pendiente", etiqueta: "Pendientes" },
  { valor: "push", etiqueta: "Push" },
];
const ORDENES_FILTRO = [
  { valor: "recientes", etiqueta: "Más recientes" },
  { valor: "antiguas", etiqueta: "Más antiguas" },
  { valor: "stake-mayor", etiqueta: "Stake mayor" },
  { valor: "stake-menor", etiqueta: "Stake menor" },
];

const DEPORTES_CONOCIDOS = new Set(
  DEPORTES_FILTRO.filter(
    (deporte) => deporte.valor !== "todos" && deporte.valor !== "otro",
  ).map((deporte) => deporte.valor),
);

function normalizarTexto(valor) {
  const textoNormalizado = String(valor ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  const equivalencias = {
    soccer: "futbol",
    "futbol soccer": "futbol",
    basketball: "basquetbol",
    baseball: "beisbol",
    boxing: "boxeo",
    box: "boxeo",
    ufc: "mma",
    "artes marciales mixtas": "mma",
    nfl: "futbol americano",
    "american football": "futbol americano",
    "ice hockey": "hockey",
    "e sports": "esports",
  };

  return equivalencias[textoNormalizado] ?? textoNormalizado;
}

function construirTextoBusqueda(apuesta) {
  const selecciones = Array.isArray(apuesta.selecciones)
    ? apuesta.selecciones
    : [];

  const campos = [
    apuesta.id,
    apuesta.fecha,
    apuesta.casa,
    apuesta.deporte,
    apuesta.liga,
    apuesta.evento,
    apuesta.seleccion,
    apuesta.tipo_apuesta,
    apuesta.modalidad,
    apuesta.resultado,
    ...selecciones.flatMap((seleccion) => [
      seleccion.deporte,
      seleccion.liga,
      seleccion.evento,
      seleccion.tipo_apuesta,
      seleccion.seleccion,
    ]),
  ];

  return campos.map((campo) => normalizarTexto(campo)).join(" ");
}

function Historial() {
  const [paginaActual, setPaginaActual] = useState(1);
  const [apuestas, setApuestas] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [filtroResultado, setFiltroResultado] = useState("todas");
  const [filtroDeporte, setFiltroDeporte] = useState("todos");
  const [orden, setOrden] = useState("recientes");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const numeracionApuestas = useMemo(() => {
    const apuestasOrdenadas = [...apuestas].sort(
      (primera, segunda) => Number(primera.id) - Number(segunda.id),
    );

    return new Map(
      apuestasOrdenadas.map((apuesta, indice) => [apuesta.id, indice + 1]),
    );
  }, [apuestas]);

  function irAPagina(nuevaPagina) {
    setPaginaActual(nuevaPagina);
  }

  useEffect(() => {
    const temporizador = setTimeout(() => {
      window.scrollTo({
        top: 0,
        left: 0,
        behavior: "smooth",
      });
    }, 50);

    return () => clearTimeout(temporizador);
  }, [paginaActual]);

  useEffect(() => {
    const controlador = new AbortController();

    async function cargarHistorial() {
      try {
        const datos = await obtenerApuestas(controlador.signal);

        setApuestas(datos);
      } catch (errorCapturado) {
        if (errorCapturado.name !== "AbortError") {
          setError(
            errorCapturado instanceof Error
              ? errorCapturado.message
              : "No se pudo cargar el historial.",
          );
        }
      } finally {
        if (!controlador.signal.aborted) {
          setCargando(false);
        }
      }
    }

    cargarHistorial();

    return () => {
      controlador.abort();
    };
  }, []);

  const apuestasFiltradas = useMemo(() => {
    const textoBuscado = normalizarTexto(busqueda);

    const filtradas = apuestas.filter((apuesta) => {
      const resultado = normalizarTexto(apuesta.resultado || "pendiente");

      const coincideResultado =
        filtroResultado === "todas" || resultado === filtroResultado;

      const deporte = normalizarTexto(apuesta.deporte);

      const coincideDeporte =
        filtroDeporte === "todos" ||
        (filtroDeporte === "otro"
          ? Boolean(deporte) && !DEPORTES_CONOCIDOS.has(deporte)
          : deporte === filtroDeporte);

      const coincideBusqueda =
        !textoBuscado || construirTextoBusqueda(apuesta).includes(textoBuscado);

      return coincideResultado && coincideDeporte && coincideBusqueda;
    });

    return [...filtradas].sort((primera, segunda) => {
      if (orden === "antiguas") {
        return Number(primera.id) - Number(segunda.id);
      }

      if (orden === "stake-mayor") {
        return (Number(segunda.stake) || 0) - (Number(primera.stake) || 0);
      }

      if (orden === "stake-menor") {
        return (Number(primera.stake) || 0) - (Number(segunda.stake) || 0);
      }

      return Number(segunda.id) - Number(primera.id);
    });
  }, [apuestas, busqueda, filtroDeporte, filtroResultado, orden]);

  const totalPaginas = Math.max(
    1,
    Math.ceil(apuestasFiltradas.length / APUESTAS_POR_PAGINA),
  );

  const apuestasPaginadas = useMemo(() => {
    const inicio = (paginaActual - 1) * APUESTAS_POR_PAGINA;

    const fin = inicio + APUESTAS_POR_PAGINA;

    return apuestasFiltradas.slice(inicio, fin);
  }, [apuestasFiltradas, paginaActual]);

  useEffect(() => {
    setPaginaActual(1);
  }, [busqueda, filtroDeporte, filtroResultado, orden]);

  return (
    <main className="pagina-historial">
      <div className="historial-contenedor">
        <header className="cabecera-historial">
          <div>
            <p className="marca">TRACKBET</p>
            <h1 className="titulo-gradient">Historial de apuestas</h1>

            <p className="subtitulo">
              Consulta y localiza cada movimiento de tu trayectoria.
            </p>
          </div>

          <div className="contador-historial">
            <span>Mostrando</span>

            <strong>{apuestasFiltradas.length}</strong>

            <span>de {apuestas.length}</span>
          </div>
        </header>

        <section
          className="filtros-historial"
          aria-label="Filtros del historial"
        >
          <label className="campo-filtro">
            <span>Buscar</span>

            <input
              type="search"
              value={busqueda}
              onChange={(evento) => setBusqueda(evento.target.value)}
              placeholder="Evento, liga, casa, deporte..."
            />
          </label>

          <label className="campo-filtro">
            <span>Deporte</span>

            <SelectorTrackBet
              value={filtroDeporte}
              onChange={setFiltroDeporte}
              opciones={DEPORTES_FILTRO}
              ariaLabel="Filtrar por deporte"
            />
          </label>

          <label className="campo-filtro">
            <span>Resultado</span>

            <SelectorTrackBet
              value={filtroResultado}
              onChange={setFiltroResultado}
              opciones={RESULTADOS_FILTRO}
              ariaLabel="Filtrar por resultado"
            />
          </label>

          <label className="campo-filtro">
            <span>Orden</span>

            <SelectorTrackBet
              value={orden}
              onChange={setOrden}
              opciones={ORDENES_FILTRO}
              ariaLabel="Ordenar apuestas"
            />
          </label>
          <button
            type="button"
            className="boton-limpiar-filtros"
            onClick={() => {
              setBusqueda("");
              setFiltroDeporte("todos");
              setFiltroResultado("todas");
              setOrden("recientes");
            }}
          >
            Limpiar
          </button>
        </section>

        {cargando && (
          <section className="mensaje mensaje-cargando">
            Cargando historial de apuestas...
          </section>
        )}

        {error && (
          <section className="mensaje mensaje-error">
            <strong>No se pudo cargar el historial.</strong>

            <span>{error}</span>
          </section>
        )}

        {!cargando && !error && apuestasFiltradas.length === 0 && (
          <section className="historial-vacio">
            <span>TRACK 00</span>
            <h2>No encontramos apuestas</h2>

            <p>Modifica los filtros o registra una nueva apuesta.</p>
          </section>
        )}

        {apuestasFiltradas.length > 0 && (
          <section className="lista-historial">
            {apuestasPaginadas.map((apuesta) => (
              <TicketHistorial
                key={apuesta.id}
                apuesta={apuesta}
                numeroApuesta={numeracionApuestas.get(apuesta.id) ?? 0}
                formatoDinero={formatoDinero}
              />
            ))}
          </section>
        )}
        {apuestasFiltradas.length > APUESTAS_POR_PAGINA && (
          <nav className="paginacion-historial">
            <div className="estado-paginacion">
              <span>Página</span>
              <strong>{paginaActual}</strong>
              <span>de {totalPaginas}</span>
            </div>

            <div className="controles-paginacion">
              <button
                type="button"
                disabled={paginaActual === 1}
                onClick={() => irAPagina(paginaActual - 1)}
              >
                ← Anterior
              </button>

              <button
                type="button"
                disabled={paginaActual === totalPaginas}
                onClick={() => irAPagina(paginaActual + 1)}
              >
                Siguiente →
              </button>
            </div>

            <button
              type="button"
              className="boton-volver-inicio"
              onClick={() => irAPagina(1)}
            >
              Regresar al inicio
            </button>
          </nav>
        )}
      </div>
    </main>
  );
}

export default Historial;
