import {
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
export interface SelectOption {
  value: string;
  label: string;
}
interface Props {
  id: string;
  label: string;
  value: string;
  options: SelectOption[];
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function Select({
  id,
  label,
  value,
  options,
  onChange,
  disabled = false,
}: Props) {
  const generated = useId(),
    listId = `${generated}-list`;
  const root = useRef<HTMLDivElement>(null),
    trigger = useRef<HTMLButtonElement>(null),
    list = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false),
    [active, setActive] = useState(0);
  const [position, setPosition] = useState({
    left: 0,
    top: 0,
    width: 0,
    maxHeight: 260,
  });
  const typed = useRef(""),
    typedAt = useRef(0);
  const selected = options.findIndex((option) => option.value === value);
  function show() {
    if (disabled) return;
    setActive(Math.max(0, selected));
    setOpen(true);
  }
  function choose(index: number) {
    if (options[index]) onChange(options[index].value);
    setOpen(false);
    trigger.current?.focus();
  }
  useLayoutEffect(() => {
    if (!open || !trigger.current) return;
    const rect = trigger.current.getBoundingClientRect(),
      height = window.innerHeight;
    const below = height - rect.bottom - 12,
      above = rect.top - 12;
    const upwards =
      below < Math.min(options.length * 44 + 8, 260) && above > below;
    const maxHeight = Math.max(
      44,
      Math.min(260, upwards ? above - 8 : below - 8),
    );
    const menuHeight = Math.min(position.width===rect.width&&list.current?list.current.scrollHeight:options.length*44+10,maxHeight);
    setPosition({
      left: Math.max(
        12,
        Math.min(
          rect.left,
          document.documentElement.clientWidth - rect.width - 12,
        ),
      ),
      top: upwards ? rect.top - menuHeight - 8 : rect.bottom + 8,
      width: rect.width,
      maxHeight,
    });
  }, [open, options.length, position.width]);
  useLayoutEffect(() => {
    if (open)
      list.current
        ?.querySelector(`[data-index="${active}"]`)
        ?.scrollIntoView({ block: "nearest" });
  }, [active, open]);
  useEffect(() => {
    if (!open) return;
    const outside = (event: PointerEvent) => {
      if (!root.current?.contains(event.target as Node)) setOpen(false);
    };
    const reposition = (event: Event) => {
      if (!list.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("pointerdown", outside);
    window.addEventListener("resize", reposition);
    window.addEventListener("scroll", reposition, true);
    return () => {
      document.removeEventListener("pointerdown", outside);
      window.removeEventListener("resize", reposition);
      window.removeEventListener("scroll", reposition, true);
    };
  }, [open]);
  useEffect(() => {
    if (disabled) setOpen(false);
  }, [disabled]);
  function keyboard(event: KeyboardEvent<HTMLButtonElement>) {
    if (
      ["ArrowDown", "ArrowUp", "Home", "End", "Enter", " "].includes(event.key)
    ) {
      event.preventDefault();
      if (!open) {
        show();
        return;
      }
      if (event.key === "Enter" || event.key === " ") return choose(active);
      setActive((index) =>
        event.key === "Home"
          ? 0
          : event.key === "End"
            ? options.length - 1
            : (index + (event.key === "ArrowDown" ? 1 : -1) + options.length) %
              options.length,
      );
    } else if (event.key === "Escape" && open) {
      event.preventDefault();
      event.stopPropagation();
      setOpen(false);
    } else if (event.key === "Tab") setOpen(false);
    else if (
      event.key.length === 1 &&
      !event.ctrlKey &&
      !event.metaKey &&
      !event.altKey
    ) {
      const now = Date.now();
      typed.current =
        (now - typedAt.current > 700 ? "" : typed.current) +
        event.key.toLocaleLowerCase("pt-BR");
      typedAt.current = now;
      const index = options.findIndex((option) =>
        option.label.toLocaleLowerCase("pt-BR").startsWith(typed.current),
      );
      if (index >= 0) {
        if (open) setActive(index);
        else onChange(options[index].value);
      }
    }
  }
  return (
    <div className="custom-select" ref={root}>
      <button
        id={id}
        ref={trigger}
        className="select-trigger"
        type="button"
        role="combobox"
        aria-label={label}
        aria-expanded={open}
        aria-controls={listId}
        aria-haspopup="listbox"
        aria-activedescendant={open ? `${listId}-${active}` : undefined}
        disabled={disabled}
        onClick={() => (open ? setOpen(false) : show())}
        onKeyDown={keyboard}
        onBlur={(event) => {
          if (!root.current?.contains(event.relatedTarget as Node))
            setOpen(false);
        }}
      >
        <span>{options[selected]?.label || "Selecionar"}</span>
        <svg viewBox="0 0 20 20" className="select-chevron" aria-hidden="true">
          <path fill="currentColor" d="m5 8 5 5 5-5Z" />
        </svg>
      </button>
      {open && (
        <div
          ref={list}
          id={listId}
          role="listbox"
          aria-label={label}
          className="select-options"
          style={position}
        >
          {options.map((option, index) => (
            <button
              key={option.value}
              id={`${listId}-${index}`}
              data-index={index}
              type="button"
              role="option"
              tabIndex={-1}
              aria-selected={option.value === value}
              className={index === active ? "option-active" : ""}
              onPointerMove={() => setActive(index)}
              onPointerDown={(event) => event.preventDefault()}
              onClick={() => choose(index)}
            >
              <span>{option.label}</span>
              {option.value === value && (
                <svg viewBox="0 0 20 20" aria-hidden="true">
                  <path fill="currentColor" d="m3 10 4 4L17 4l-2-2-8 8-2-2Z" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
