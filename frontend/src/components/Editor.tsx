import { useEffect, useRef, useState, type FormEvent } from "react";
import { activities, valid, type Activity, type Participation } from "../model";
import { api, message } from "../api";
import { Dialog } from "./Dialog";
import { Button } from "./Button";
import { Select } from "./Select";

export function Editor({
  record,
  onClose,
  onSave,
}: {
  record: Participation;
  onClose: () => void;
  onSave: (records: Participation[]) => string | undefined;
}) {
  const [draft, setDraft] = useState({ ...record });
  const [start, setStart] = useState(""),
    [end, setEnd] = useState("");
  const [error, setError] = useState(""),
    [saving, setSaving] = useState(false);
  const active = useRef(true);
  useEffect(() => {
    active.current = true;
    return () => {
      active.current = false;
    };
  }, []);
  const change = <K extends keyof Participation>(
    key: K,
    value: Participation[K],
  ) => setDraft((previous) => ({ ...previous, [key]: value }));
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (saving) return;
    setError("");
    const next = {
      ...draft,
      name: draft.name.trim(),
      ra: draft.ra.trim(),
      detail: draft.detail.trim(),
      semester: draft.semester.trim(),
      warning: "",
    };
    let semesters = [next.semester];
    if (start || end) {
      if (!/^20\d{2}\.[12]$/.test(start) || !/^20\d{2}\.[12]$/.test(end))
        return setError("Preencha início e fim no formato 2026.1.");
      const index = (s: string) =>
        Number(s.slice(0, 4)) * 2 + Number(s.at(-1)) - 1;
      const first = index(start),
        last = index(end);
      if (last < first || last - first > 40)
        return setError(
          "Confira o intervalo: fim após início e máximo de 20 anos.",
        );
      semesters = Array.from(
        { length: last - first + 1 },
        (_, offset) =>
          `${Math.floor((first + offset) / 2)}.${((first + offset) % 2) + 1}`,
      );
    }
    if (!valid({ ...next, semester: semesters[0] }))
      return setError("Confira nome, RA, semestre, descrição e horas.");
    setSaving(true);
    try {
      const normalized: { records: Participation[] } = await (
        await api("/api/normalize", { records: [next] })
      ).json();
      if (!active.current) return;
      next.detail = normalized.records[0].detail;
      const problem = onSave(
        semesters.map((semester) => ({
          ...next,
          semester,
          id: crypto.randomUUID(),
        })),
      );
      if (problem) setError(problem);
      else onClose();
    } catch (error) {
      if (active.current) setError(message(error));
    } finally {
      if (active.current) setSaving(false);
    }
  }
  return (
    <Dialog id="editor" title="Revisar participação" onClose={onClose}>
      <form
        id="edit-form"
        onSubmit={submit}
        onKeyDown={(event) => {
          if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
            event.preventDefault();
            if (!saving) event.currentTarget.requestSubmit();
          }
        }}
      >
        {error && (
          <p id="edit-error" className="form-error" role="alert">
            {error}
          </p>
        )}
        <p className="source" id="source">
          {record.source
            ? `Resposta original (linha ${record.row}): ${record.source}\n${record.warning || ""}`
            : "Nova participação"}
        </p>
        <label>
          Nome completo
          <input
            id="edit-name"
            value={draft.name}
            onChange={(event) => change("name", event.target.value)}
            required
            maxLength={150}
          />
        </label>
        <div className="form-grid">
          <label>
            RA
            <input
              id="edit-ra"
              value={draft.ra}
              onChange={(event) => change("ra", event.target.value)}
              required
              pattern="[0-9]{5,12}"
            />
          </label>
          <label>
            Atividade
            <Select
              id="edit-activity"
              label="Atividade"
              value={draft.activity}
              onChange={(value) => change("activity", value as Activity)}
              options={Object.entries(activities).map(([value, label]) => ({
                value,
                label,
              }))}
            />
          </label>
        </div>
        <label>
          Função / modalidade / evento
          <input
            id="edit-detail"
            value={draft.detail}
            onChange={(event) => change("detail", event.target.value)}
            required
            maxLength={350}
          />
        </label>
        <div className="form-grid">
          <label>
            Semestre
            <input
              id="edit-semester"
              value={draft.semester}
              onChange={(event) => change("semester", event.target.value)}
              pattern="20[0-9]{2}\.[12]"
              placeholder="2026.1"
            />
          </label>
          <label>
            Carga horária
            <input
              id="edit-hours"
              type="number"
              min="0.5"
              max="2000"
              step="0.01"
              required
              value={draft.hours}
              onChange={(event) => change("hours", event.target.valueAsNumber)}
            />
          </label>
        </div>
        <p>
          Para um período longo, preencha os dois limites abaixo. Será criado um
          registro para cada semestre, incluindo início e fim.
        </p>
        <div className="form-grid">
          <label>
            De (opcional)
            <input
              id="range-start"
              value={start}
              onChange={(event) => setStart(event.target.value)}
              placeholder="2023.1"
              pattern="20[0-9]{2}\.[12]"
            />
          </label>
          <label>
            Até (opcional)
            <input
              id="range-end"
              value={end}
              onChange={(event) => setEnd(event.target.value)}
              placeholder="2024.2"
              pattern="20[0-9]{2}\.[12]"
            />
          </label>
        </div>
        <label className="check">
          <input
            id="edit-approved"
            type="checkbox"
            checked={draft.approved}
            onChange={(event) => change("approved", event.target.checked)}
          />{" "}
          Conferi os dados e aprovo a emissão
        </label>
        <Button
          tooltip="Salvar os dados e aplicar o intervalo confirmado."
          shortcut="Ctrl / ⌘ + Enter"
          type="submit"
          variant="primary"
          icon="next"
          disabled={saving}
        >
          {saving ? "Salvando…" : "Salvar participação"}
        </Button>
      </form>
    </Dialog>
  );
}
