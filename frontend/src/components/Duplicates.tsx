import { useState } from "react";
import { activities, type Participation, type DuplicateParticipation } from "../model";
import { Dialog } from "./Dialog";
import { Button } from "./Button";

export function Duplicates({ records, duplicates, busy, onChoose, onClose }: {
  records: Participation[];
  duplicates: DuplicateParticipation[];
  busy: boolean;
  onChoose: (record: DuplicateParticipation) => void;
  onClose: () => void;
}) {
  const [index, setIndex] = useState(0);
  const position = Math.min(index, Math.max(0, duplicates.length - 1));
  const candidate = duplicates[position];
  const current = candidate && records.find((r) => r.id === candidate.duplicate_of);
  function version(record: Participation, label: string) {
    return <section className="duplicate-version">
      <span className="eyebrow">{label}</span>
      <h3>{record.name}</h3>
      <dl>
        <dt>RA</dt><dd>{record.ra}</dd>
        <dt>Atividade</dt><dd>{activities[record.activity]} · {record.detail}</dd>
        <dt>Semestre / horas</dt><dd>{record.semester || "A confirmar"} · {record.hours} h</dd>
        <dt>Origem</dt><dd>Linha {record.row || "manual"}</dd>
      </dl>
      <p className="source">{record.source || "Participação manual"}</p>
      {record.warning && <p className="duplicate-warning">{record.warning}</p>}
    </section>;
  }
  return <Dialog id="duplicates" title="Comparar respostas duplicadas" onClose={onClose}>
    <p>Respostas da mesma pessoa, atividade e semestre foram separadas para evitar emissão em dobro. Compare a origem e escolha a versão que deve ficar no lote. A escolha precisa ser aprovada novamente.</p>
    {candidate ? <>
      <div className="duplicate-comparison">
        {current ? version(current, "NO LOTE") : <section className="duplicate-version"><p>A versão inicial foi removida do lote. Você pode recuperar esta resposta.</p></section>}
        {version(candidate, "ALTERNATIVA")}
      </div>
      <Button className="duplicate-choice" disabled={busy} onClick={() => onChoose(candidate)} tooltip="Usar esta resposta no lote, sem emitir duas vezes a mesma participação.">{current ? "Usar a alternativa no lote" : "Recuperar para revisão"}</Button>
      <p>Ao substituir, a versão anterior fica aqui como alternativa. Fechar mantém a versão atual.</p>
      <nav className="pagination" aria-label="Navegar respostas duplicadas">
        <Button disabled={position === 0 || busy} onClick={() => setIndex(position - 1)}>Anterior</Button>
        <span role="status">{position + 1} de {duplicates.length}</span>
        <Button disabled={position >= duplicates.length - 1 || busy} onClick={() => setIndex(position + 1)}>Próxima</Button>
      </nav>
    </> : <p>Nenhuma alternativa restante para comparar.</p>}
  </Dialog>;
}
