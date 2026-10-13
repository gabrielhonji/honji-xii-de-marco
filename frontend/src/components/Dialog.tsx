import { useEffect, useRef, type ReactNode } from "react";
import { Tooltip } from "./Tooltip";
export function Dialog({
  id,
  title,
  onClose,
  children,
}: {
  id: string;
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = ref.current!;
    const previous=document.activeElement instanceof HTMLElement?document.activeElement:null;
    dialog.showModal();
    dialog.querySelector<HTMLElement>('button:not(:disabled),input:not(:disabled),[tabindex="0"]')?.focus();
    const keyboard=(event:KeyboardEvent)=>{
      if(event.key!=='Tab')return;
      const controls=Array.from(dialog.querySelectorAll<HTMLElement>('button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),textarea:not(:disabled),[tabindex="0"]')).filter(element=>element.getClientRects().length>0);
      const first=controls[0],last=controls.at(-1);
      if(first&&event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}
      else if(last&&!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}
    };
    dialog.addEventListener('keydown',keyboard);
    return () => {dialog.removeEventListener('keydown',keyboard);dialog.close();if(previous?.isConnected)previous.focus();};
  }, []);
  return (
    <dialog
      id={id}
      ref={ref}
      aria-labelledby={`${id}-title`}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
    >
      <div className="dialog-head">
        <h2 id={`${id}-title`}>{title}</h2>
        <Tooltip text={id === "editor" ? "Cancelar" : "Fechar"} shortcut="Esc">
          <button
            type="button"
            id={`close-${id}`}
            onClick={onClose}
            aria-label="Fechar"
          >
            ×
          </button>
        </Tooltip>
      </div>
      {children}
    </dialog>
  );
}
