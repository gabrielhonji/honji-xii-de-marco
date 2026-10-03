import { useMemo, useState } from "react";
import { activities, fold, valid, type Participation } from "../model";
import { Button } from "./Button";
import { Tooltip } from "./Tooltip";
import { Select } from "./Select";
import { Icon } from "./Icons";

interface Props {
  records: Participation[];
  filename: string;
  busy: boolean;
  issued: string;
  naming: string;
  downloadUrl: string | null;
  onApprove: (record: Participation) => void;
  onApproveReady: () => void;
  onNormalize: () => void;
  onAdd: () => void;
  onEdit: (record: Participation) => void;
  onPreview: (record: Participation) => void;
  onRemove: (record: Participation) => void;
  onIssued: (value: string) => void;
  onNaming: (value: string) => void;
  onGenerate: () => void;
}
export function Review(props: Props) {
  const { records, busy } = props;
  const [query, setQuery] = useState(""),
    [filter, setFilter] = useState("all");
  const approved = records.filter(
    (r) => r.approved && valid(r) && !r.warning,
  ).length;
  const visible = useMemo(
    () =>
      records.filter(
        (r) =>
          fold(`${r.name} ${r.ra}`).includes(fold(query)) &&
          (filter !== "pending" || r.warning || !valid(r)) &&
          (filter !== "approved" || r.approved),
      ),
    [records, query, filter],
  );
  return (
    <section id="review">
      <div className="stats">
        {[
          ["PARTICIPANTES", new Set(records.map((r) => r.ra)).size, "people"],
          ["CERTIFICADOS PROPOSTOS", records.length, "total"],
          [
            "PRECISAM DE REVISÃO",
            records.filter((r) => r.warning || !valid(r)).length,
            "pending",
          ],
          ["APROVADOS", approved, "approved"],
        ].map(([label, count, id]) => (
          <div key={id}>
            <span>{label}</span>
            <b id={String(id)}>{count}</b>
          </div>
        ))}
      </div>
      <div className="review-head">
        <div>
          <span className="eyebrow" id="filename">
            {props.filename}
          </span>
          <h2>Confira antes de emitir.</h2>
        </div>
        <Button
          id="approve-ready"
          tooltip="Aprovar somente registros válidos e sem pendência."
          disabled={busy}
          onClick={props.onApproveReady}
        >
          Aprovar registros sem pendência
        </Button>
      </div>
      <div className="toolbar">
        <input
          id="search"
          placeholder="Buscar nome ou RA"
          aria-label="Buscar nome ou RA"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <Select
          id="filter"
          label="Filtrar situação"
          value={filter}
          onChange={setFilter}
          options={[
            { value: "all", label: "Todas as participações" },
            { value: "pending", label: "Com pendência" },
            { value: "approved", label: "Aprovadas" },
          ]}
        />
        <Button
          id="normalize"
          tooltip="Unificar descrições sem alterar horas ou semestres."
          disabled={busy}
          onClick={props.onNormalize}
        >
          Padronizar descrições
        </Button>
        <Button
          id="add"
          tooltip="Adicionar uma participação manualmente."
          disabled={busy}
          onClick={props.onAdd}
        >
          + Adicionar participação
        </Button>
      </div>
      <p className="review-note">
        Revise também os registros reconhecidos automaticamente. Horas e
        períodos são editáveis. Anos sem semestre e eventos exigem confirmação.
      </p>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              {[
                "EMITIR",
                "PARTICIPANTE / RA",
                "ATIVIDADE",
                "SEMESTRE",
                "HORAS",
                "REVISÃO",
                "AÇÕES",
              ].map((label) => (
                <th key={label}>{label}</th>
              ))}
            </tr>
          </thead>
          <tbody id="rows">
            {visible.map((r) => (
              <tr key={r.id}>
                <td data-label="Emitir">
                  <label className="row-selection">
                    <input
                      type="checkbox"
                      checked={r.approved}
                      disabled={busy}
                      aria-label={`Aprovar ${r.name}, ${r.activity}, ${r.semester || "sem semestre"}`}
                      onChange={() => props.onApprove(r)}
                    />
                  </label>
                </td>
                <td data-label="Participante / RA">
                  {r.name}
                  <span className="sub">RA {r.ra}</span>
                </td>
                <td data-label="Atividade">
                  {activities[r.activity]}
                  <span className="sub">{r.detail}</span>
                </td>
                <td data-label="Semestre">{r.semester || "A confirmar"}</td>
                <td data-label="Horas">{r.hours} h</td>
                <td data-label="Revisão">
                  <span
                    className={r.warning || !valid(r) ? "badge warn" : "badge"}
                  >
                    {r.warning || !valid(r)
                      ? "Conferir"
                      : r.approved
                        ? "Aprovado"
                        : "Reconhecido"}
                  </span>
                </td>
                <td data-label="Ações">
                  <div className="record-actions">
                    <Button
                      variant="quiet"
                      icon="edit"
                      tooltip="Revisar dados desta participação."
                      disabled={busy}
                      onClick={() => props.onEdit(r)}
                    >
                      Revisar
                    </Button>
                    <Button
                      variant="quiet"
                      icon="preview"
                      tooltip="Abrir a prévia do certificado."
                      disabled={busy}
                      onClick={() => props.onPreview(r)}
                    >
                      Prévia
                    </Button>
                    <Button
                      variant="quiet"
                      icon="remove"
                      tooltip="Remover esta participação do lote."
                      className="remove-action"
                      disabled={busy}
                      aria-label={`Excluir participação de ${r.name}`}

                      onClick={() => props.onRemove(r)}
                    />
                  </div>
                </td>
              </tr>
            ))}
            {!visible.length && (
              <tr className="empty-state">
                <td colSpan={7}>
                  {records.length
                    ? "Nenhuma participação corresponde à busca ou ao filtro."
                    : "O lote está vazio. Adicione uma participação ou importe outro arquivo."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="export">
        <div>
          <span className="eyebrow">03 / FINALIZAR LOTE</span>
          <h3>Prontos para reconhecer.</h3>
          <p id="export-note">
            {approved} certificado{approved === 1 ? "" : "s"} aprovado
            {approved === 1 ? "" : "s"} para emissão.
          </p>
          <small>
            Modelo sem assinatura digital. Confira e obtenha a assinatura
            institucional após a emissão.
          </small>
        </div>
        <div className="export-controls">
          <label>
            Data da emissão
            <input
              type="date"
              id="issued"
              required
              value={props.issued}
              disabled={busy}
              onChange={(event) => props.onIssued(event.target.value)}
            />
          </label>
          <label>
            Nome dos arquivos
            <Select
              id="naming"
              label="Nome dos arquivos"
              value={props.naming}
              disabled={busy}
              onChange={props.onNaming}
              options={[
                { value: "name", label: "Nome - atividade - semestre" },
                { value: "ra", label: "RA - atividade - semestre" },
              ]}
            />
          </label>
          <Button
            id="generate"
            tooltip="Gerar PDFs e relatório dos registros aprovados."
            variant="primary"
            icon="download"
            disabled={busy || !approved}
            onClick={props.onGenerate}
          >
            {busy ? "Processando…" : "Baixar certificados .ZIP"}
          </Button>
          {props.downloadUrl && (
            <div className="download-result">
              <span>ZIP pronto.</span>
              <Tooltip text="Baixar novamente o lote já gerado, sem repetir a emissão.">
                <a
                  className="download-link"
                  href={props.downloadUrl}
                  download={`XII-certificados-${props.issued}.zip`}
                >
                  Baixar novamente <Icon name="download" />
                </a>
              </Tooltip>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
