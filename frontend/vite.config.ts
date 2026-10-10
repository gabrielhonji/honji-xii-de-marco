import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import packageJson from "./package.json" with { type: "json" };
const release = new Date().toISOString().replace(/[-:]/g, "").replace("T", "-").slice(0, 15);

export default defineConfig({
  plugins: [react(), tailwindcss()],
  define: {
    __APP_VERSION__: JSON.stringify(packageJson.version),
    __APP_RELEASE__: JSON.stringify(release),
  },
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
