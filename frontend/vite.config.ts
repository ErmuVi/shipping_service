import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// В деве фронтенд живет на :5173 и проксирует API на FastAPI (:8080).
// Благодаря этому кука сессии остается same-origin и CORS не нужен.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8080",
      "/healthcheck": "http://localhost:8080",
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
