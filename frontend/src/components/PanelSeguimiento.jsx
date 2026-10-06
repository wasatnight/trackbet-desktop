function PanelSeguimiento({ resumen, formatoDinero }) {
  return (
    <section className="panel-seguimiento">
      <article className="metrica">
        <span className="numero-metrica">{resumen.apuestas_totales}</span>

        <span>Apuestas registradas</span>
      </article>

      <article className="metrica">
        <span className="numero-metrica">{resumen.apuestas_resueltas}</span>

        <span>Apuestas resueltas</span>
      </article>

      <article className="metrica">
        <span className="numero-metrica">{resumen.apuestas_pendientes}</span>

        <span>Apuestas pendientes</span>
      </article>

      <article className="metrica">
        <span className="numero-metrica">
          {formatoDinero.format(resumen.stake_pendiente)}
        </span>

        <span>Exposición pendiente</span>
      </article>
    </section>
  );
}

export default PanelSeguimiento;
