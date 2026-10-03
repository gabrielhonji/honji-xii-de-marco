import type { Theme } from "../model";
export type IconName =
  "edit" | "preview" | "remove" | "download" | "file" | "next";
const paths: Record<IconName, string> = {
  edit: "M4 13 13 4l3 3-9 9H4zM11 6l3 3",
  preview:
    "M2 10s3-5 8-5 8 5 8 5-3 5-8 5-8-5-8-5ZM10 8a2 2 0 1 0 0 4 2 2 0 0 0 0-4",
  remove: "M5 6h10l-1 11H6zM3 6h14M7 6V3h6v3M8 9v5m4-5v5",
  download: "M10 3v10m-4-4 4 4 4-4M4 14v3h12v-3",
  file: "M6 3h6l4 4v10H6zM12 3v5h4M9 12h4m-2-2v4",
  next: "M4 10h12m-5-5 5 5-5 5",
};
export function Icon({ name }: { name: IconName }) {
  return (
    <svg
      className="action-icon shrink-0"
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[name]} />
    </svg>
  );
}
export function ThemeIcon({ theme }: { theme: Theme }) {
  return (
    <svg
      viewBox="0 0 20 20"
      width="20"
      height="20"
      fill="currentColor"
      aria-hidden="true"
    >
      {theme === "dark" ? (
        <>
          {Array.from({ length: 8 }, (_, i) => (
            <rect
              key={i}
              x="9.25"
              y="1"
              width="1.5"
              height="3"
              rx=".75"
              transform={`rotate(${i * 45} 10 10)`}
            />
          ))}
          <circle cx="10" cy="10" r="3.4" />
        </>
      ) : (
        <path
          d="M16 3.07A8 8 0 1 0 16 16.93A8 8 0 0 1 16 3.07Z"
          transform="rotate(-35 10 10)"
        />
      )}
    </svg>
  );
}
