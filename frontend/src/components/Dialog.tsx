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
    dialog.showModal();
    return () => dialog.close();
  }, []);
  return (
    <dialog
      id={id}
      ref={ref}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
    >
      <div className="dialog-head">
        <h2>{title}</h2>
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
