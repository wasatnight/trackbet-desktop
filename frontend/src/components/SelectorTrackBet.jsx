import { useEffect, useRef, useState } from "react";

function SelectorTrackBet({ value, onChange, opciones, ariaLabel }) {
  const [abierto, setAbierto] = useState(false);
  const contenedorRef = useRef(null);

  useEffect(() => {
    function cerrarAlHacerClickFuera(evento) {
      if (
        contenedorRef.current &&
        !contenedorRef.current.contains(evento.target)
      ) {
        setAbierto(false);
      }
    }

    document.addEventListener("pointerdown", cerrarAlHacerClickFuera);

    return () => {
      document.removeEventListener("pointerdown", cerrarAlHacerClickFuera);
    };
  }, []);

  const opcionActual =
    opciones.find((opcion) => opcion.valor === value) ?? opciones[0];

  return (
    <div className="selector-trackbet" ref={contenedorRef}>
      <button
        type="button"
        className={`selector-trackbet-boton ${abierto ? "abierto" : ""}`}
        aria-label={ariaLabel}
        aria-expanded={abierto}
        onClick={() => setAbierto((estado) => !estado)}
      >
        <span>{opcionActual.etiqueta}</span>
        <span className="selector-trackbet-flecha">{abierto ? "⌃" : "⌄"}</span>
      </button>

      {abierto && (
        <div className="selector-trackbet-menu">
          {opciones.map((opcion) => (
            <button
              type="button"
              key={opcion.valor}
              className={`selector-trackbet-opcion ${
                opcion.valor === value ? "seleccionada" : ""
              }`}
              onClick={() => {
                onChange(opcion.valor);
                setAbierto(false);
              }}
            >
              {opcion.etiqueta}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default SelectorTrackBet;
