import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: "127.0.0.1",
    strictPort: true,
    proxy: Object.fromEntries(
      [
        "/api",
        "/assets",
        "/site.webmanifest",
        "/identidade",
        "/identity.js",
        "/identity.css",
        "/style.css",
        "/responsive.css",
      ].map((path) => [
        path,
        {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
          headers: { Origin: "http://127.0.0.1:8000" },
        },
      ]),
    ),
  },
  build: { outDir: "../web/dist", emptyOutDir: true, assetsDir: "static" },
});
