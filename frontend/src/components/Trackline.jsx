function TrackLine({
  bankrollInicial,
  bankrollActual,
  cambioBankroll,
  formatoDinero,
  formatoPorcentaje,
}) {
  return (
    <section className="trackline">
      <div className="trackline-encabezado">
        <div>
          <p className="etiqueta-seccion">TRACKLINE</p>
          <h2>Evolución del bankroll</h2>
        </div>

        <strong
          className={
            cambioBankroll > 0
              ? "cambio positivo"
              : cambioBankroll < 0
                ? "cambio negativo"
                : "cambio neutro"
          }
        >
          {cambioBankroll > 0 ? "+" : ""}
          {formatoPorcentaje.format(cambioBankroll)}%
        </strong>
      </div>

      <div className="trayecto">
        <span className="nodo nodo-inicial" />
        <span className="recorrido" />
        <span className="nodo nodo-actual" />
      </div>

      <div className="trackline-valores">
        <div>
          <span>Bankroll inicial</span>

          <strong>{formatoDinero.format(bankrollInicial)}</strong>
        </div>

        <div className="valor-actual">
          <span>Bankroll actual</span>

          <strong>{formatoDinero.format(bankrollActual)}</strong>
        </div>
      </div>
    </section>
  );
}

export default TrackLine;
