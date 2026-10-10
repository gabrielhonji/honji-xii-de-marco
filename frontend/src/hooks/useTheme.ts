import { useEffect, useLayoutEffect, useState } from "react";
import type { Theme } from "../model";
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const cookie = document.cookie.split('; ').find(item => item.startsWith('honji_theme='))?.split('=')[1];
    if (cookie === "light" || cookie === "dark") return cookie;
    try {
      const saved = localStorage.getItem("honji-theme");
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
        if (localStorage.getItem("honji-theme")) return;
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
        localStorage.setItem("honji-theme", next);
      } catch {}
      const secure = location.protocol === 'https:' ? '; Secure' : '';
      document.cookie = `honji_theme=${next}; Domain=.honji.com.br; Path=/; Max-Age=31536000; SameSite=Lax${secure}`;
      return next;
    });
  return { theme, toggle };
}
