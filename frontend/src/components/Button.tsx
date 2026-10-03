import type { ButtonHTMLAttributes } from "react";
import { Icon, type IconName } from "./Icons";
import { Tooltip } from "./Tooltip";
type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  icon?: IconName;
  variant?: "primary" | "secondary" | "quiet";
  tooltip?: string;
  shortcut?: string;
};
export function Button({
  icon,
  variant = "secondary",
  className = "",
  children,
  tooltip,
  shortcut,
  ...props
}: Props) {
  const button = (
    <button
      type="button"
      className={`${variant === "quiet" ? "" : variant} min-h-11 transition-colors duration-150 disabled:cursor-wait focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-honji-accent ${className}`}
      {...props}
    >
      {icon && <Icon name={icon} />}
      {children}
    </button>
  );
  return tooltip ? (
    <Tooltip text={tooltip} shortcut={shortcut}>
      {button}
    </Tooltip>
  ) : (
    button
  );
}
