import {
  cloneElement,
  useEffect,
  useId,
  useLayoutEffect,
  useRef,
  useState,
  type ReactElement,
} from "react";

export function Tooltip({
  text,
  shortcut,
  children,
}: {
  text: string;
  shortcut?: string;
  children: ReactElement<{ "aria-describedby"?: string }>;
}) {
  const id = useId(),
    anchor = useRef<HTMLSpanElement>(null),
    bubble = useRef<HTMLSpanElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const [open, setOpen] = useState(false),
    [position, setPosition] = useState({ left: 0, top: 0 });
  function hide() {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
    setOpen(false);
  }
  function show(delay = 0) {
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => setOpen(true), delay);
  }
  useLayoutEffect(() => {
    if (!open) return;
    const target = anchor.current?.querySelector("button,a,label,input,select");
    if (!target || !bubble.current) return;
    const rect = target.getBoundingClientRect(),
      tip = bubble.current.getBoundingClientRect();
    setPosition({
      left: Math.min(
        innerWidth - tip.width / 2 - 12,
        Math.max(tip.width / 2 + 12, rect.left + rect.width / 2),
      ),
      top:
        rect.top - tip.height - 9 >= 8
          ? rect.top - tip.height - 9
          : rect.bottom + 9,
    });
  }, [open]);
  useEffect(() => {
    if (!open)
      return () => {
        if (timer.current) clearTimeout(timer.current);
      };
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") hide();
    };
    window.addEventListener("scroll", hide, true);
    window.addEventListener("resize", hide);
    window.addEventListener("keydown", escape);
    return () => {
      if (timer.current) clearTimeout(timer.current);
      window.removeEventListener("scroll", hide, true);
      window.removeEventListener("resize", hide);
      window.removeEventListener("keydown", escape);
    };
  }, [open]);
  return (
    <span
      className="tooltip-anchor"
      ref={anchor}
      onPointerEnter={(event) => {
        if (event.pointerType !== "touch") show(300);
      }}
      onPointerLeave={hide}
      onFocus={(event) => {
        if (event.target.matches(":focus-visible")) show();
      }}
      onBlur={hide}
    >
      {cloneElement(children, {
        "aria-describedby":
          [children.props["aria-describedby"], open ? id : null]
            .filter(Boolean)
            .join(" ") || undefined,
      })}
      {open && (
        <span
          ref={bubble}
          id={id}
          role="tooltip"
          className="honji-tooltip"
          style={{ left: position.left, top: position.top }}
        >
          <span>{text}</span>
          {shortcut && <kbd>{shortcut}</kbd>}
        </span>
      )}
    </span>
  );
}
