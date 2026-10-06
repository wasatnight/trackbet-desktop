function MovimientoCapital({ resumen, formatoDinero }) {
  return (
    <section className="movimiento-capital">
      <div className="movimiento-titulo">
        <p className="etiqueta-seccion">CAPITAL FLOW</p>

        <h2>Movimiento del capital</h2>
      </div>

      <div className="movimiento-datos">
        <div>
          <span>Stake total</span>

          <strong>{formatoDinero.format(resumen.stake_total)}</strong>
        </div>

        <div>
          <span>Stake resuelto</span>

          <strong>{formatoDinero.format(resumen.stake_resuelto)}</strong>
        </div>

        <div>
          <span>Stake en juego</span>

          <strong>{formatoDinero.format(resumen.stake_pendiente)}</strong>
        </div>
      </div>
    </section>
  );
}

export default MovimientoCapital;
