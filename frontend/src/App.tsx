import { useEffect, useRef, useState } from "react";
import { api, loadSession, logout, message, type Session } from "./api";
import {
  freshParticipation,
  localDate,
  participationKey,
  valid,
  type Participation,
  type DuplicateParticipation,
} from "./model";
import { useTheme } from "./hooks/useTheme";
import { Header, Hero, Footer, Upload } from "./components/Layout";
import { Review } from "./components/Review";
import { Editor } from "./components/Editor";
import { Dialog } from "./components/Dialog";
import { Duplicates } from "./components/Duplicates";

interface Notice {
  text: string;
  action?: () => void;
}
interface Analysis {
  records: Participation[];
  responses: number;
  duplicates: number;
  duplicate_records: DuplicateParticipation[];
}
interface Normalized {
  records: Participation[];
  changed: number;
}
export function App() {
  const { theme, toggle } = useTheme();
  const [records, setRecords] = useState<Participation[]>([]),
    [loaded, setLoaded] = useState(false);
  const [duplicates, setDuplicates] = useState<DuplicateParticipation[]>([]);
  const [reviewDuplicates, setReviewDuplicates] = useState(false);
  const [filename, setFilename] = useState(""),
    [status, setStatus] = useState(""),
    [busy, setBusy] = useState(false);
  const [current, setCurrent] = useState<Participation | null>(null),
    [help, setHelp] = useState(false);
  const [issued, setIssued] = useState(localDate),
    [naming, setNaming] = useState("name");
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null),
    [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null),
    [exported, setExported] = useState(false);
  const busyRef = useRef(false),
    downloadRef = useRef<string | null>(null),
    previewRef = useRef<string | null>(null);
  const lotVersion = useRef(0);
  const [session, setSession] = useState<Session | null>(null);
  const [sessionError, setSessionError] = useState("");
  useEffect(() => {
    loadSession().then((active) => {
      if (!active) window.location.assign("/auth/login");
      else setSession(active);
    }).catch((error) => setSessionError(message(error)));
  }, []);
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(
      () => setNotice(null),
      notice.action ? 10000 : 5500,
    );
    return () => clearTimeout(timer);
  }, [notice]);
  useEffect(
    () => () => {
      if (downloadRef.current) URL.revokeObjectURL(downloadRef.current);
      if (previewRef.current) URL.revokeObjectURL(previewRef.current);
    },
    [],
  );
  const notify = (text: string, action?: () => void) =>
    setNotice({ text, action });
  function invalidate() {
    if (downloadRef.current) URL.revokeObjectURL(downloadRef.current);
    downloadRef.current = null;
    setDownloadUrl(null);
    setExported(false);
  }
  function begin() {
    if (busyRef.current) return false;
    busyRef.current = true;
    setBusy(true);
    return true;
  }
  function finish() {
    busyRef.current = false;
    setBusy(false);
  }
  function checkIssued() {
    const input = document.getElementById("issued") as HTMLInputElement | null;
    if (!issued || !input?.checkValidity()) {
      notify("Escolha uma data válida para a emissão.");
      input?.reportValidity();
      input?.focus();
      return false;
    }
    return true;
  }
  async function upload(file: File | undefined) {
    if (!file || busyRef.current) return;
    if (!/\.(csv|xlsx)$/i.test(file.name))
      return notify("Selecione um arquivo CSV ou XLSX.");
    if (file.size > 10_000_000) return notify("O arquivo deve ter até 10 MB.");
    if (!begin()) return;
    setStatus("Lendo respostas e separando os semestres…");
    try {
      const bytes = new Uint8Array(await file.arrayBuffer());
      let binary = "";
      for (let i = 0; i < bytes.length; i += 8192)
        binary += String.fromCharCode(...bytes.subarray(i, i + 8192));
      const data: Analysis = await (
        await api("/api/analyze", { filename: file.name, data: btoa(binary) })
      ).json();
      invalidate();
      lotVersion.current++;
      setNotice(null);
      setRecords(data.records);
      setDuplicates(data.duplicate_records || []);
      setReviewDuplicates(false);
      setFilename(file.name);
      setLoaded(true);
      setStatus(
        `${data.responses} respostas importadas${data.duplicates ? ` · ${data.duplicates} duplicatas disponíveis para comparação na revisão` : ""}.`,
      );
      requestAnimationFrame(() =>
        document.getElementById("review")?.scrollIntoView({
          behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
            ? "instant"
            : "smooth",
        }),
      );
    } catch (error) {
      setStatus(message(error));
    } finally {
      finish();
    }
  }
  function save(added: Participation[]) {
    if (
      added.some((item) =>
        records.some(
          (existing) =>
            existing.id !== current?.id &&
            participationKey(existing) === participationKey(item),
        ),
      )
    )
      return "Esta participação já existe para a mesma pessoa, atividade, descrição e semestre. Confira o registro existente.";
    const position = records.findIndex((r) => r.id === current?.id),
      next = [...records];
    if (position >= 0) next.splice(position, 1, ...added);
    else next.push(...added);
    invalidate();
    setRecords(next);
    return undefined;
  }
  function chooseDuplicate(candidate: DuplicateParticipation) {
    if (busyRef.current) return;
    const existing = records.find((r) => r.id === candidate.duplicate_of);
    if (records.some((r) => r.id !== existing?.id && participationKey(r) === participationKey(candidate))) {
      notify("Esta versão coincide com outra participação do lote. Revise o registro existente.");
      return;
    }
    invalidate();
    const replacement = { ...candidate, id: existing?.id ?? crypto.randomUUID(), approved: false };
    setRecords((previous) => existing
      ? previous.map((r) => r.id === existing.id ? replacement : r)
      : [...previous, replacement]);
    setDuplicates((previous) => existing
      ? previous.map((r) => r.id === candidate.id
        ? { ...existing, id: candidate.id, duplicate_of: existing.id, approved: false }
        : r)
      : previous.filter((r) => r.id !== candidate.id));
    notify("Versão escolhida para o lote. Confira os dados e aprove antes de emitir.");
  }
  function approve(record: Participation) {
    if (busyRef.current) return;
    if (!valid(record) || record.warning) {
      setCurrent(record);
      return;
    }
    invalidate();
    setRecords((previous) =>
      previous.map((r) =>
        r.id === record.id ? { ...r, approved: !r.approved } : r,
      ),
    );
  }
  function remove(record: Participation) {
    if (busyRef.current) return;
    const position = records.indexOf(record),
      version = lotVersion.current;
    invalidate();
    setRecords((previous) => previous.filter((r) => r.id !== record.id));
    notify("Participação removida.", () => {
      if (version !== lotVersion.current) return;
      invalidate();
      setRecords((previous) => {
        if (previous.some((r) => r.id === record.id)) return previous;
        const next = [...previous];
        next.splice(Math.min(position, next.length), 0, record);
        return next;
      });
    });
  }
  async function normalize() {
    if (!begin()) return;
    try {
      const result: Normalized = await (
        await api("/api/normalize", { records })
      ).json();
      const counts = new Map<string, number>();
      result.records.forEach((r) =>
        counts.set(
          participationKey(r),
          (counts.get(participationKey(r)) || 0) + 1,
        ),
      );
      setRecords(
        result.records.map((r) =>
          counts.get(participationKey(r))! > 1
            ? {
                ...r,
                warning:
                  r.warning ||
                  "Descrição padronizada coincide com outra participação. Revise a duplicata.",
                approved: false,
              }
            : r,
        ),
      );
      invalidate();
      notify(
        result.changed
          ? `${result.changed} descrição${result.changed === 1 ? "" : "s"} padronizada${result.changed === 1 ? "" : "s"}. Períodos, horas e pendências foram preservados.`
          : "As descrições já estão padronizadas.",
      );
    } catch (error) {
      notify(message(error));
    } finally {
      finish();
    }
  }
  async function preview(record: Participation) {
    if (busyRef.current || !checkIssued()) return;
    if (!valid(record)) return setCurrent(record);
    if (!begin()) return;
    try {
      const response = await api("/api/preview", {
        record: { ...record, approved: true },
        issued,
      });
      if (previewRef.current) URL.revokeObjectURL(previewRef.current);
      previewRef.current = URL.createObjectURL(await response.blob());
      setPreviewUrl(previewRef.current);
    } catch (error) {
      notify(message(error));
    } finally {
      finish();
    }
  }
  function closePreview() {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current);
    previewRef.current = null;
    setPreviewUrl(null);
  }
  async function generate() {
    if (busyRef.current || !checkIssued()) return;
    const approved = records.filter(
      (r) => r.approved && valid(r) && !r.warning,
    );
    if (approved.length > 1000)
      return notify(
        "Emita até 1.000 certificados por lote. Desmarque registros para dividir a emissão.",
      );
    if (!approved.length || !begin()) return;
    try {
      const response = await api("/api/generate", {
        records: approved,
        issued,
        naming,
      });
      invalidate();
      downloadRef.current = URL.createObjectURL(await response.blob());
      setDownloadUrl(downloadRef.current);
      setExported(true);
      const link = document.createElement("a");
      link.href = downloadRef.current;
      link.download = `XII-certificados-${issued}.zip`;
      link.hidden = true;
      document.body.append(link);
      link.click();
      link.remove();
      notify(
        `${approved.length} certificado${approved.length === 1 ? "" : "s"} gerado${approved.length === 1 ? "" : "s"} com relatório de conferência.`,
      );
    } catch (error) {
      notify(message(error));
    } finally {
      finish();
    }
  }
  if (sessionError) return <main className="workspace"><p role="alert">{sessionError}</p></main>;
  if (!session) return <main className="workspace" aria-busy="true" />;
  return (
    <>
      <Header theme={theme} toggle={toggle} user={session.user.name} onLogout={async () => {
        const response = await logout();
        if (response.ok) {
          const body = (await response.json()) as { redirect: string };
          window.location.assign(body.redirect);
        }
      }} />
      <main>
        <Hero />
        <section id="workspace">
          <div className="section-head">
            <div>
              <div className="eyebrow">02 / ÁREA DE EMISSÃO</div>
              <h2>Seu próximo lote começa aqui.</h2>
            </div>
            <span className="privacy">Seus dados ficam nesta sessão.</span>
          </div>
          <div className="steps">
            <span className="active" id="step1">
              <b>01</b> Importar respostas
            </span>
            <span className={loaded ? "active" : ""} id="step2">
              <b>02</b> Conferir participações
            </span>
            <span className={exported ? "active" : ""} id="step3">
              <b>03</b> Exportar certificados
            </span>
          </div>
          <Upload
            busy={busy}
            status={status}
            onUpload={upload}
            onHelp={() => setHelp(true)}
          />
          {loaded && (
            <Review
              key={filename + lotVersion.current}
              records={records}
              duplicates={duplicates.length}
              onReviewDuplicates={() => setReviewDuplicates(true)}
              filename={filename}
              busy={busy}
              issued={issued}
              naming={naming}
              downloadUrl={downloadUrl}
              onApprove={approve}
              onApproveReady={() => {
                invalidate();
                setRecords((previous) =>
                  previous.map((r) =>
                    valid(r) && !r.warning ? { ...r, approved: true } : r,
                  ),
                );
                notify(
                  "Registros sem pendência aprovados. Confira a prévia antes de baixar.",
                );
              }}
              onNormalize={normalize}
              onAdd={() => setCurrent(freshParticipation())}
              onEdit={setCurrent}
              onPreview={preview}
              onRemove={remove}
              onIssued={(value) => {
                setIssued(value);
                invalidate();
              }}
              onNaming={(value) => {
                setNaming(value);
                invalidate();
              }}
              onGenerate={generate}
            />
          )}
        </section>
      </main>
      <Footer />
      {reviewDuplicates && <Duplicates records={records} duplicates={duplicates} busy={busy}
        onChoose={chooseDuplicate} onClose={() => setReviewDuplicates(false)} />}
      {current && (
        <Editor
          key={current.id}
          record={current}
          onClose={() => setCurrent(null)}
          onSave={save}
        />
      )}
      {previewUrl && (
        <Dialog
          id="preview"
          title="Prévia do certificado"
          onClose={closePreview}
        >
          <a
            id="open-pdf"
            className="secondary pdf-link"
            href={previewUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            Abrir PDF em outra aba
          </a>
          <iframe id="pdf-frame" src={previewUrl} title="Certificado em PDF" />
        </Dialog>
      )}
      {help && (
        <Dialog
          id="help-dialog"
          title="Como funciona"
          onClose={() => setHelp(false)}
        >
          <p>
            Exporte as respostas do formulário em CSV ou XLSX e selecione o
            arquivo. O sistema reconhece as colunas originais e separa os
            intervalos explícitos em semestres.
          </p>
          <p>
            Revise cada participação, confirme os casos ambíguos e aprove os
            registros que deseja emitir. Para EP, o modelo de referência usa 48
            horas; atividades contínuas usam 100 horas por semestre. Ações
            sociais exigem a carga horária confirmada.
          </p>
          <p>
            O ZIP inclui PDFs organizados por pessoa e um relatório CSV para
            conferência. Os dados não são salvos no servidor; recarregar a
            página encerra o lote. A distribuição utiliza um modelo neutro. Um
            template autorizado pode ser configurado somente no ambiente local.
            A assinatura deve ser obtida após a emissão.
          </p>
        </Dialog>
      )}
      {notice && (
        <div id="toast" role="status">
          {notice.text}
          {notice.action && (
            <button
              type="button"
              onClick={() => {
                notice.action?.();
                setNotice(null);
              }}
            >
              Desfazer
            </button>
          )}
        </div>
      )}
    </>
  );
}
