import TicketFinanciero from "./TicketFinanciero";

function TarjetasFinancieras({ resumen, formatoDinero, formatoPorcentaje }) {
  const estadoGanancia = resumen.ganancia_neta >= 0 ? "positivo" : "negativo";

  const estadoRoi = resumen.roi >= 0 ? "positivo" : "negativo";

  return (
    <section className="tarjetas-principales">
      <TicketFinanciero
        codigo="TB-001"
        variante="violeta"
        titulo="Bankroll actual"
        valor={formatoDinero.format(resumen.bankroll_actual)}
        detalle="Capital disponible estimado"
      />

      <TicketFinanciero
        codigo="TB-002"
        variante="verde"
        titulo="Ganancia neta"
        valor={formatoDinero.format(resumen.ganancia_neta)}
        detalle="Resultado acumulado"
        estado={estadoGanancia}
      />

      <TicketFinanciero
        codigo="TB-003"
        variante="cian"
        titulo="ROI histórico"
        valor={`${formatoPorcentaje.format(resumen.roi)}%`}
        detalle="Retorno sobre stake resuelto"
        estado={estadoRoi}
      />
    </section>
  );
}

export default TarjetasFinancieras;
