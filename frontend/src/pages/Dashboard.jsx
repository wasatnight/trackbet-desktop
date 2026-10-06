import { useEffect, useState } from "react";
import "../App.css";

import { API_URL } from "../config/api";
import EncabezadoTrackBet from "../components/EncabezadoTrackBet";
import MovimientoCapital from "../components/MovimientoCapital";
import PanelSeguimiento from "../components/PanelSeguimiento";
import TarjetasFinancieras from "../components/TarjetasFinancieras";
import TrackLine from "../components/TrackLine";

const formatoDinero = new Intl.NumberFormat("es-MX", {
  style: "currency",
  currency: "MXN",
  minimumFractionDigits: 2,
});

const formatoPorcentaje = new Intl.NumberFormat("es-MX", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function Dashboard() {
  const [resumen, setResumen] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controlador = new AbortController();

    async function cargarResumenFinanciero() {
      try {
        const respuesta = await fetch(
          `${API_URL}/reportes/resumen-financiero`,
          {
            signal: controlador.signal,
          },
        );

        if (!respuesta.ok) {
          throw new Error(
            `La API respondió con el código ${respuesta.status}.`,
          );
        }

        const datos = await respuesta.json();
        setResumen(datos);
      } catch (errorCapturado) {
        if (errorCapturado.name !== "AbortError") {
          setError(
            errorCapturado instanceof Error
              ? errorCapturado.message
              : "Ocurrió un error desconocido.",
          );
        }
      } finally {
        if (!controlador.signal.aborted) {
          setCargando(false);
        }
      }
    }

    cargarResumenFinanciero();

    return () => {
      controlador.abort();
    };
  }, []);

  const cambioBankroll =
    resumen && resumen.bankroll_inicial > 0
      ? ((resumen.bankroll_actual - resumen.bankroll_inicial) /
          resumen.bankroll_inicial) *
        100
      : 0;

  return (
    <main className="pagina">
      <div className="dashboard">
        <EncabezadoTrackBet />

        {cargando && (
          <section className="mensaje mensaje-cargando">
            Cargando información financiera...
          </section>
        )}

        {error && (
          <section className="mensaje mensaje-error">
            <strong>No se pudo cargar TrackBet.</strong>
            <span>{error}</span>
          </section>
        )}

        {resumen && (
          <>
            <TrackLine
              bankrollInicial={resumen.bankroll_inicial}
              bankrollActual={resumen.bankroll_actual}
              cambioBankroll={cambioBankroll}
              formatoDinero={formatoDinero}
              formatoPorcentaje={formatoPorcentaje}
            />

            <TarjetasFinancieras
              resumen={resumen}
              formatoDinero={formatoDinero}
              formatoPorcentaje={formatoPorcentaje}
            />

            <PanelSeguimiento resumen={resumen} formatoDinero={formatoDinero} />

            <MovimientoCapital
              resumen={resumen}
              formatoDinero={formatoDinero}
            />
          </>
        )}
      </div>
    </main>
  );
}

export default Dashboard;
