function EncabezadoTrackBet() {
  return (
    <>
      <header className="encabezado">
        <div className="identidad">
          <div className="marca-track" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>

          <div>
            <p className="marca">TRACKBET</p>

            <h1 className="titulo-gradient">Tu rendimiento, bajo control.</h1>

            <p className="subtitulo">
              Seguimiento financiero de tus apuestas deportivas.
            </p>
          </div>
        </div>

        <div className="estado-api">
          <span className="indicador-api" />
          API conectada
        </div>
      </header>

      <div className="linea-identidad" />
    </>
  );
}

export default EncabezadoTrackBet;
