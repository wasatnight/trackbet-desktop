function TicketFinanciero({
  codigo,
  variante,
  titulo,
  valor,
  detalle,
  estado,
}) {
  const claseValor = estado ? `valor-ticket ${estado}` : "valor-ticket";

  return (
    <article className={`ticket ticket-${variante}`}>
      <span className="ticket-codigo">{codigo}</span>

      <p className="titulo-ticket">{titulo}</p>

      <p className={claseValor}>{valor}</p>

      <p className="detalle-ticket">{detalle}</p>
    </article>
  );
}

export default TicketFinanciero;
