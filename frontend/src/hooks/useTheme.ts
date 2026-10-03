import { useEffect, useLayoutEffect, useState } from "react";
import type { Theme } from "../model";
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    try {
      const saved = localStorage.getItem("xii-theme");
      if (saved === "light" || saved === "dark") return saved;
    } catch {}
    return matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  });
  useLayoutEffect(() => {
    document.documentElement.dataset.theme = theme;
  }, [theme]);
  useEffect(() => {
    const preference = matchMedia("(prefers-color-scheme: dark)");
    const sync = (event: MediaQueryListEvent) => {
      try {
        if (localStorage.getItem("xii-theme")) return;
      } catch {}
      setTheme(event.matches ? "dark" : "light");
    };
    preference.addEventListener("change", sync);
    return () => preference.removeEventListener("change", sync);
  }, []);
  const toggle = () =>
    setTheme((previous) => {
      const next = previous === "dark" ? "light" : "dark";
      try {
        localStorage.setItem("xii-theme", next);
      } catch {}
      return next;
    });
  return { theme, toggle };
}
