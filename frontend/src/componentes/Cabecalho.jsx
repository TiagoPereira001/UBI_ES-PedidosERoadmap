// Topo de cada ecrã, como nos mockups: título a marcador, uma linha de contexto e as ações à direita.
export default function Cabecalho({ titulo, sub, children }) {
  return (
    <header className="topo">
      <div>
        <h1>{titulo}</h1>
        {sub && <p className="sub">{sub}</p>}
      </div>
      {children && <div className="acoes">{children}</div>}
    </header>
  );
}
