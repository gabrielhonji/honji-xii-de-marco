import { useEffect, useRef, useState } from "react";
import type { Theme } from "../model";
import { Tooltip } from "./Tooltip";
import { ThemeIcon } from "./Icons";
export function Header({
  theme,
  toggle,
  user,
  onLogout,
}: {
  theme: Theme;
  toggle: () => void;
  user: string;
  onLogout: () => void;
}) {
  const [accountOpen, setAccountOpen] = useState(false);
  const account = useRef<HTMLDivElement>(null);
  const initials = user.trim().split(/\s+/).filter(Boolean).slice(0, 2).map(part => part[0]).join('').toUpperCase() || 'XII';
  useEffect(() => {
    if (!accountOpen) return;
    const outside = (event: PointerEvent) => { if (!account.current?.contains(event.target as Node)) setAccountOpen(false); };
    const escape = (event: KeyboardEvent) => { if (event.key === 'Escape') setAccountOpen(false); };
    document.addEventListener('pointerdown', outside);
    document.addEventListener('keydown', escape);
    return () => { document.removeEventListener('pointerdown', outside); document.removeEventListener('keydown', escape); };
  }, [accountOpen]);
  return (
    <header>
      <div className="brand-cluster">
        <a className="brand" href="/" aria-label="HONJI — XII de Março, início">
          <svg
            className="honji-signature"
            viewBox="0 0 64 64"
            role="img"
            aria-label="Símbolo HONJI"
          >
            <use href="/assets/honji-symbol.svg#mark" />
          </svg>
          <span className="honji-wordmark">HONJI</span>
        </a>
        <a className="project-label" href="#workspace">
          <svg className="xii-icon" viewBox="0 0 64 64" aria-hidden="true">
            <use href="/assets/xii-icon.svg#mark" />
          </svg>
          <span className="project-text">
            XII de Março<span>Secretaria digital</span>
          </span>
        </a>
      </div>
      <div className="header-tools">
        <Tooltip
          text={theme === "dark" ? "Ativar tema claro." : "Ativar tema escuro."}
        >
          <button
            id="theme-toggle"
            className="theme-toggle"
            onClick={toggle}
            aria-label={
              theme === "dark" ? "Ativar tema claro" : "Ativar tema escuro"
            }
            aria-pressed={theme === "dark"}
          >
            <span id="theme-icon" aria-hidden="true">
              <ThemeIcon theme={theme} />
            </span>
          </button>
        </Tooltip>
        <div className="account-control" ref={account}>
          <button className="account-avatar" type="button" aria-label={`Abrir conta de ${user || 'Conta Honji'}`} aria-expanded={accountOpen} onClick={() => setAccountOpen(value => !value)}>{initials}</button>
          {accountOpen && <div className="account-panel"><a className="account-name" href="https://gabriel.honji.com.br/#perfil">{user || 'Conta Honji'}<span>Editar perfil</span></a><a href="https://gabriel.honji.com.br/#acesso">Área de acesso</a><button type="button" onClick={onLogout}>Sair</button></div>}
        </div>
      </div>
    </header>
  );
}
export function Hero() {
  return (
    <section className="hero">
      <div className="eyebrow">
        <span>01 / SECRETARIA DIGITAL</span>
      </div>
      <div className="hero-line">
        <h1>
          Participações.
          <br />
          Semestres.
          <br />
          <em>Reconhecimento.</em>
        </h1>
        <div className="hero-aside">
          <span className="hero-aside-label">ASSOCIAÇÃO ATLÉTICA ACADÊMICA</span>
          <div className="hero-aside-content">
            <svg
              className="honji-signature"
              viewBox="0 0 64 64"
              role="img"
              aria-label="Símbolo HONJI"
            >
              <use href="/assets/honji-symbol.svg#mark" />
            </svg>
            <p>
              Da planilha ao certificado.
              <br />
              Mais tempo para fazer a XII acontecer.
            </p>
            <a href="#workspace">
              Começar emissão{" "}
              <svg
                className="action-icon"
                viewBox="0 0 20 20"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M4 10h12m-5-5 5 5-5 5" />
              </svg>
            </a>
          </div>
        </div>
      </div>
      <div className="hero-bottom">
        <span>XII DE MARÇO / DESDE 2013</span>
        <span>UM CERTIFICADO PARA CADA SEMESTRE</span>
      </div>
    </section>
  );
}
export function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <div className="xii-brand">
          <svg className="xii-icon" viewBox="0 0 64 64" aria-hidden="true">
            <use href="/assets/xii-icon.svg#mark" />
          </svg>
          <span className="mark">
            XII<span>DE MARÇO</span>
          </span>
        </div>
        <p>
          Secretaria da Atlética XII de Março
          <br />
          <span>Feito para valorizar quem faz parte.</span>
        </p>
        <div className="footer-credit">
          <span>DESENVOLVIDO POR</span>
          <a
            href="https://github.com/gabrielhonji"
            target="_blank"
            rel="noopener noreferrer"
          >
            gabriel.honji
          </a>
          <span className="footer-separator" aria-hidden="true">·</span>
          <span>VERSÃO {__APP_VERSION__} · {__APP_RELEASE__}</span>
          <span className="footer-separator" aria-hidden="true">·</span>
          <span>UTFPR / APUCARANA</span>
        </div>
      </div>
    </footer>
  );
}
export function Upload({
  busy,
  status,
  onUpload,
  onHelp,
}: {
  busy: boolean;
  status: string;
  onUpload: (file: File | undefined) => void;
  onHelp: () => void;
}) {
  const [drag, setDrag] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  return (
    <div className="import-grid">
      <div
        className={"upload" + (drag ? " drag" : "")}
        id="drop"
        aria-busy={busy}
        onDragOver={(event) => {
          event.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDrag(false);
          onUpload(event.dataTransfer.files[0]);
        }}
      >
        <span className="file-icon">
          <svg
            className="action-icon"
            viewBox="0 0 20 20"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M6 3h6l4 4v10H6zM12 3v5h4M9 12h4m-2-2v4" />
          </svg>
        </span>
        <h3>Uma planilha. Todos os semestres.</h3>
        <p>
          Arraste as respostas do formulário para cá
          <br />
          ou escolha um arquivo no seu computador.
        </p>
        <Tooltip text="Importar respostas em CSV ou XLSX." shortcut="Enter">
          <label
            className="primary"
            htmlFor="file"
            role="button"
            tabIndex={busy ? -1 : 0}
            aria-controls="file"
            aria-disabled={busy}
            onKeyDown={(event) => {
              if ((event.key === "Enter" || event.key === " ") && !busy) {
                event.preventDefault();
                fileRef.current?.click();
              }
            }}
          >
            Selecionar arquivo{" "}
            <svg
              className="action-icon"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M6 3h6l4 4v10H6zM12 3v5h4M9 12h4m-2-2v4" />
            </svg>
          </label>
        </Tooltip>
        <input
          ref={fileRef}
          disabled={busy}
          onChange={(event) => {
            onUpload(event.target.files?.[0]);
            event.target.value = "";
          }}
          id="file"
          type="file"
          accept=".csv,.xlsx"
          hidden={true}
        />
        <small>CSV ou XLSX · até 10 MB · dados em memória</small>
        <div id="upload-status" role="status">
          {status}
        </div>
      </div>
      <aside className="guide">
        <span className="eyebrow">DO FORMULÁRIO À EMISSÃO</span>
        <h3>
          O trabalho repetitivo,
          <br />
          resolvido.
        </h3>
        <div>
          <b>01</b>
          <p>
            <strong>Importe as respostas</strong>
            <br />
            Use a exportação original do Google Forms.
          </p>
        </div>
        <div>
          <b>02</b>
          <p>
            <strong>Revise com contexto</strong>
            <br />
            Confira os períodos e corrija as ambiguidades.
          </p>
        </div>
        <div>
          <b>03</b>
          <p>
            <strong>Baixe tudo organizado</strong>
            <br />
            PDFs por pessoa, atividade e semestre em um ZIP.
          </p>
        </div>
        <Tooltip text="Consultar as regras de importação, revisão e emissão.">
          <button onClick={onHelp} id="help" className="text-action">
            <svg
              className="action-icon"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <circle cx="10" cy="10" r="7" />
              <path d="M8 7a2 2 0 0 1 4 0c0 2-2 2-2 4m0 3v.1" />
            </svg>
            Como funciona
          </button>
        </Tooltip>
      </aside>
    </div>
  );
}
